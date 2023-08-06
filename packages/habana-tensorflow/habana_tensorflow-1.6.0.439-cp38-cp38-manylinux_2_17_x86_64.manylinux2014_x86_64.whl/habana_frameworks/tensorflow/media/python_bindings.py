###############################################################################
# Copyright (C) 2022 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################
import imp
import tensorflow as tf

from habana_frameworks.tensorflow.library_loader import media_ops


def _load_media_tf_bridge_binary():
    # import of media_tf_bridge binding and _load_media_module both introduce
    # media_tf_bridge.so into the process _load_media_module must execute first,
    # otherwise htf.media_ops will be empty!
    assert media_ops.is_initialized, "make sure to call load_habana_module() before importing media_tf_bridge binding"
    from habana_frameworks.tensorflow.sysconfig import get_lib_dir

    version_suffix = ".".join(tf.__version__.split(".")[0:3])
    media_tf_bridge_so_path = f"{get_lib_dir()}/media_tf_bridge.so.{version_suffix}"
    return imp.load_dynamic("media_tf_bridge", media_tf_bridge_so_path)


_media_tf_bridge = _load_media_tf_bridge_binary()


def register_pipeline(pipeline):
    _media_tf_bridge.register_pipeline(id(pipeline), pipeline)
    return id(pipeline)


def finalize_media():
    _media_tf_bridge.finalize_media()
