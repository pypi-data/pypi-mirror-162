###############################################################################
# Copyright (C) 2020-2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################

import os
import sys
import tensorflow as tf
import logging
from .lib_utils import habana_module_path, libraries_location
from .profiling.hook_init import profiling_hook_init
from .synapse_logger_helpers import synapse_logger_init
from .multinode_helpers import _setup_env_for_multinode, run_once
import glob
import importlib
from .sysconfig import version_dict
import threading

log = logging.getLogger(__file__)


def _override_ops():
    """Searches through 'ops' directory and invokes '_override_op' where available."""
    ops = glob.glob(os.path.join(os.path.dirname(__file__), "ops", "*.py"))
    for op in ops:
        op_name = os.path.basename(op).split(".")[0]
        mod = importlib.import_module(".ops." + op_name, package="habana_frameworks.tensorflow")
        if hasattr(mod, "_override_op"):
            mod._override_op()


@run_once  # Make sure to only register once because second attempt causes tf error.
def _register_grads(habana_ops):
    grads = glob.glob(os.path.join(os.path.dirname(__file__), "grads", "*.py"))
    for grad in grads:
        if "__init__" not in grad:
            grad_name = os.path.basename(grad).split(".")[0]
            mod = importlib.import_module(".grads." + grad_name, package="habana_frameworks.tensorflow")
            mod._register_grad(habana_ops)


class _HabanaOps:
    def __init__(self):
        self.ops = None
        self._is_op_override_allowed = True

    def __getattr__(self, op):
        assert self.is_initialized, f"looking for {op}, but habana module seems not to be loaded yet"
        return getattr(self.ops, op)

    @property
    def is_initialized(self):
        return self.ops is not None

    @property
    def is_op_override_allowed(self):
        return self._is_op_override_allowed

    @is_op_override_allowed.setter
    def is_op_override_allowed(self, allow_op_override):
        self._is_op_override_allowed = allow_op_override

    def initialize(self, ops):
        if self.is_initialized:
            print(f"warning: attempting to reinitialize ops", file=sys.stderr)
            return False
        self.ops = ops
        return True

    def __repr__(self):
        return f"_HabanaOps class, initialized={self.is_initialized}, store={self.ops}, len={len(dir(self.ops))}"


habana_ops = _HabanaOps()

media_ops = _HabanaOps()


def is_loaded():
    return habana_ops.is_initialized


def is_op_override_allowed():
    """Get status of op override.

    Returns:
        Allowed if True.
    """
    return habana_ops._is_op_override_allowed


def set_op_override_allowed(allow_op_override):
    """Enable or disable override of subgraph-based ops to Habana optimized versions.

    Args:
        allow_op_override: Allowed if True.
    """
    habana_ops._is_op_override_allowed = allow_op_override


def _check_driver_version():
    try:
        with open("/sys/class/habanalabs/hl0/driver_ver", "r") as f:
            driver_ver = f.read().split("\n", 1)[0]
            if not version_dict["VERSION"] in driver_ver:
                log.warning(
                    "Habana-TensorFlow(%s) and Habanalabs Driver(%s) versions differ!"
                    % (version_dict["VERSION"], driver_ver)
                )
    except:
        log.warning("Unable to read habanalabs driver file - probably driver missing in the system")


def _compute_tf_sha256_log() -> str:
    """Find TF library in the process and calculates its sha256.

    Returns:
        SHA256 of tensorflow library in the process.
    """
    import hashlib

    tf_lib_path = None
    with open(f"/proc/{os.getpid()}/maps") as file:
        for line in file:
            if "libtensorflow_framework" in line:
                tf_lib_path = line.split()[-1]
                break
    assert tf_lib_path is not None, "Failed to find TensorFlow library in the process"

    sha256_hash = hashlib.sha256()
    with open(tf_lib_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_habana_module(allow_op_override: bool = None):
    """
    Loads Habana library.

    Args:
        allow_op_override:
            Allow override of subgraph-based ops to Habana optimized version. Enabled by default.
            May be required for explicit device placement in some cases (eg. LayerNorm).
            Setting won't be altered if None is set. Bool values will override previous setting.
    """
    if allow_op_override is not None and habana_ops.is_op_override_allowed != allow_op_override:
        habana_ops.is_op_override_allowed = allow_op_override

    if is_loaded():
        return
    _check_driver_version()
    # setup multinode, if applicable
    _setup_env_for_multinode()

    if not habana_module_path:
        raise Exception("Habana module was not found. Neither in package, nor in LD_LIBRARY_PATH..")

    if "HABANA_PROFILE" not in os.environ:
        os.environ["HABANA_PROFILE"] = "profile_api"

    log.info("Loading Habana module from %s", str(habana_module_path))
    tf.load_library(habana_module_path)

    synapse_logger_init()
    profiling_hook_init()

    log.info("Loading Habana as OpLibrary from %s", str(habana_module_path))
    op_library = tf.load_op_library(habana_module_path)
    habana_ops.initialize(op_library)

    _override_ops()
    _register_grads(habana_ops)

    _load_media_module()

    from .habana_device import log as habana_log

    # compute&log hash of TF lib is slow - doing it in a separate thread
    threading.Thread(
        target=lambda: habana_log.info(f"Found TensorFlow library with SHA256: {_compute_tf_sha256_log()}"),
        daemon=True,
    ).start()

    from tensorflow.python.eager import context
    if context.context_safe() != None:
        # Force TF to reinitialize physical devices list
        context.context().reinitialize_physical_devices()

    def on_exit_cleanup():
        if context.context_safe() != None:
            # Try to ensure cleanest possible teardown
            context.context().clear_kernel_cache()

    import atexit
    atexit.register(on_exit_cleanup)

    log.info("Successfully loaded Habana module")


def _load_media_module():
    if media_ops.is_initialized:
        return

    tf.load_library(os.path.join(libraries_location, "media_tf_bridge.so." + tf.__version__))
    media = tf.load_op_library(os.path.join(libraries_location, "media_tf_bridge.so." + tf.__version__))
    media_ops.initialize(media)


def load_op_library(lib_path):
    """Load op library function for habana custom ops libraries

    In order to ensure proper initialization of TensorFlow and Habana-TensorFlow,
    Custom ops libs have to be loaded with this function

    Note: load_habana_module() needs to be called before this function
    """
    if not is_loaded():
        raise Exception("Habana module not initialized. Call load_habana_module() first.")
    return tf.load_op_library(lib_path)
