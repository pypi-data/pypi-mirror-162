###############################################################################
# Copyright (C) 2021-2022 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################

""" This script contains support for all-compare diagnostic mode.
"""

import logging
import math
import os

import tensorflow as tf
from habana_frameworks.tensorflow.util import condition_env_var

HABANA_ALLCOMPARE_ENV_VAR_NAME = "HABANA_TF_ALLCOMPARE"
HABANA_ALLCOMPARE_LOG_LEVEL_ENV_VAR_NAME = "LOG_LEVEL_ALLCOMPARE"
DEFAULT_ALLCOMPARE_LOG_LEVEL = "INFO"

_logger = logging.getLogger("allcompare")


def compute_error_rel(a, b):
    """ Computes the difference between given tensors relative to the length of their sum. Zero means they are identical.
    """
    a = tf.cast(a, tf.float32)
    b = tf.cast(b, tf.float32)
    return 2 * tf.norm(a - b) / (1 + tf.norm((a + b)))


def compute_error_rel2(a, b):
    """ Computes the difference between given tensors relative to the sum of their lengths. Zero means they are identical.
    """
    a = tf.cast(a, tf.float32)
    b = tf.cast(b, tf.float32)
    return tf.norm(a - b) / (0.1 + tf.norm(a) + tf.norm(b))


def compute_error_cosine(a, b):
    """ Computes the difference between given tensors using cosine similarity (reduced dot product). Zero means they are identical.
    """
    a = tf.cast(a, tf.float32)
    b = tf.cast(b, tf.float32)
    return 0.5 * (1.0 - tf.tensordot(a, b, len(a.shape)) / (0.00001 + tf.norm(a) * tf.norm(b)))


def make_error_fn(v):
    """ Returns an error function (tensor similarity function) from a user specified parameter.
    """
    if isinstance(v, str):
        v = v.lower()
        if v == "rel":
            return compute_error_rel
        elif v == "rel2":
            return compute_error_rel2
        elif v == "cosine":
            return compute_error_cosine
    elif callable(v):
        return v
    raise TypeError(f"Cannot make error function from: {v}")


def mpi_broadcast_sample(*args):
    """ Performs an MPI-based broadcast (from worker:0) given one or more tensors.
    """
    def on_tensor(t):
        from mpi4py import MPI
        comm_world = MPI.COMM_WORLD

        orig_t_dtype = t.dtype
        if t.dtype == tf.bfloat16:
            t = tf.cast(t, dtype=tf.float32)

        t = t.numpy()
        t = comm_world.bcast(t, root=0)
        t = tf.convert_to_tensor(t)

        if t.dtype != orig_t_dtype:
            t = tf.cast(t, dtype=orig_t_dtype)

        return t

    out = [tf.py_function(func=on_tensor, inp=[
        arg], Tout=arg.dtype) for arg in args]

    # The following step is a must when working with Estimator, which runs in graph-mode.
    # py_function mechanism is unable to properly infer tensor shapes for outputs in all cases.
    for i in range(len(args)):
        out[i].set_shape(args[i].shape)

    if len(out) == 1:
        out = out[0]
    return out


_global_instance_key = 0x7F000000


def tf_distribute_broadcast_sample(*args):
    """ Performs a tf.distribute-based "CPU" broadcast (from worker:0) given one or more tensors.
    """
    def broadcast_tensor(t):
        from mpi4py import MPI
        from tensorflow.python.ops import collective_ops

        # For simplicity, Open MPI is used here to obtain rank and size.
        # TODO: [SW-84134] Make tf_distribute_broadcast_sample (allcompare) not using MPI to get the rank and size
        comm_world = MPI.COMM_WORLD
        size = comm_world.Get_size()
        rank = comm_world.Get_rank()

        def get_cpu_group_key():
            return -1

        def get_unique_instance_key():
            global _global_instance_key
            _global_instance_key += 1
            return _global_instance_key

        orig_t = t

        with tf.device("/device:CPU:0"):
            if rank == 0:
                if t.dtype == tf.bfloat16:
                    t = tf.cast(t, dtype=tf.float32)

                t = collective_ops.broadcast_send_v2(
                    t, group_size=size, group_key=get_cpu_group_key(), instance_key=get_unique_instance_key())

                with tf.control_dependencies([t]):
                    return tf.identity(orig_t)
            else:
                t_recv_dtype = t.dtype if t.dtype != tf.bfloat16 else tf.float32

                t = collective_ops.broadcast_recv_v2(
                    t.shape, t_recv_dtype, group_size=size, group_key=get_cpu_group_key(), instance_key=get_unique_instance_key())

                if t.dtype != orig_t.dtype:
                    t = tf.cast(t, dtype=orig_t.dtype)

                return t

    out = [broadcast_tensor(arg) for arg in args]

    if len(out) == 1:
        out = out[0]
    return out


class Criterion:
    def __init__(self, threshold, start_generation=0):
        self.threshold = threshold
        self.start_generation = start_generation
        self.check_fn = Criterion._default_check_fn

    def __call__(self, value):
        return self.check_fn(self, value)

    @ staticmethod
    def make(v):
        if isinstance(v, Criterion):
            return v
        elif isinstance(v, float):
            return Criterion(v)
        else:
            raise TypeError(f"Cannot make Criterion instance from '{v}'")

    @ staticmethod
    def _default_check_fn(criterion, value):
        assert isinstance(
            criterion, Criterion), "Invalid parameter 'criterion'."
        assert isinstance(value, float), "Invalid parameter 'value'."
        allcompare = AllCompare.access_if_enabled()
        assert allcompare is not None, "Expected enabled AllCompare instance."
        return value <= criterion.threshold or allcompare.global_generation < criterion.start_generation


class TrackedSimilarity:
    def __init__(self, name):
        self.name = name
        self.value = float("nan")
        self.variable = tf.Variable(
            initial_value=self.value, name=name, dtype=tf.float32)
        self.generation = -1
        self.value_history = {}
        self._criterion = None
        self.error_count = 0
        self.max_error = -math.inf

    @property
    def criterion(self):
        return self._criterion

    @criterion.setter
    def criterion(self, value):
        self._criterion = Criterion.make(value)


class AllCompare:
    """ Provides means to execute all-compare technique by asserting that worker's gradients do not change after all-reduce operation.
        By instantiating this class, the user states that the training script supports the technique by providing means to ensure
        that every worker runs non-randomized operations (no dropouts) and processes identical input batches as other workers (no data sharding).
        This can be easily achieved using broadcast_sample() method, which returns a transformation function broadcasting the sample (i.e. input batch and expected output) from the root rank.
    """
    _instance = None
    _is_enabled_by_env = condition_env_var(
        HABANA_ALLCOMPARE_ENV_VAR_NAME, False)

    def __init__(self,
                 override_enabled: bool = None,
                 compute_error_fn="rel2",
                 broadcast_sample_fn=mpi_broadcast_sample,
                 global_criterion=0.001,
                 log_level=os.environ.get(
                     HABANA_ALLCOMPARE_LOG_LEVEL_ENV_VAR_NAME, DEFAULT_ALLCOMPARE_LOG_LEVEL).upper(),
                 log_ok=True,
                 log_error=True,
                 stop_on_error=False):
        assert AllCompare._instance is None, "There may be only one instance of AllCompare class."
        AllCompare._instance = self

        _logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        _logger.addHandler(ch)

        self._is_enabled = override_enabled if override_enabled is not None else AllCompare._is_enabled_by_env
        if self._is_enabled:
            _logger.info("All-compare diagnostic mode enabled.")

        self.compute_error_fn = make_error_fn(compute_error_fn)
        self.broadcast_sample_fn = broadcast_sample_fn
        self._global_criterion = Criterion.make(global_criterion)
        self.log_ok = log_ok
        self.log_error = log_error
        self.stop_on_error = stop_on_error

        self.tracked_similarities = {}
        self.global_generation = 0
        self.error_count = 0
        self.max_error = -math.inf

    @classmethod
    def access(cls):
        """ Returns AllCompare singleton instance or None if it was not instantiated.
        """
        assert cls._instance is not None or not cls._is_enabled_by_env, "The current training script does not support all-compare diagnostic mode."
        return cls._instance

    @classmethod
    def access_if_enabled(cls):
        """ Returns AllCompare singleton instance if it was instantiated and is enabled, otherwise None.
        """
        allcompare = cls.access()
        return allcompare if (allcompare is not None and allcompare.is_enabled) else None

    @property
    def logger(self):
        """ Logger associated with all-compare diagnostic mode.
        """
        return _logger

    @property
    def is_enabled(self):
        """ Indicates whether the all-compare feature has been enabled and tracks similarities.
        """
        return self._is_enabled

    def enable(self):
        """ Turns on all-compare diagnostic mode (regardless of HABANA_TF_ALLCOMPARE setting).
        """
        self._is_enabled = True

    def disable(self):
        """ Turns off all-compare diagnostic mode.
        """
        self._is_enabled = False

    @property
    def global_criterion(self):
        return self._global_criterion

    @global_criterion.setter
    def global_criterion(self, value):
        self._global_criterion = Criterion.make(value)

    def expect_similar(self, tensor, tensor_expected, name=None, name_prefix="AllCompare"):
        """ Expects that the specified pair of tensors are similar.
            Effectively computes the error formula and tracks its values (as there may be many error values for the same formulate in the future).
            If 'name' is not specified, it is build based on 'tensor_expected' (warning: not all tensors may have names in eager-execution mode).
        """
        assert self.is_enabled, "Unable to use AllCompare feature unless enabled."

        if name is None:
            name = tensor_expected.name.replace(":", "__")
        if name_prefix is not None:
            name = f"{name_prefix}/{name}"

        _logger.info(f"Tracking similarity: '{name}'")

        if name in self.tracked_similarities:
            similarity = self.tracked_similarities[name]
        else:
            similarity = TrackedSimilarity(name)
            self.tracked_similarities[name] = similarity

        error_tensor = self.compute_error_fn(
            tensor, tensor_expected)

        _co_assign = similarity.variable.assign(error_tensor)

        _co_py_func = tf.py_function(func=AllCompare._on_tracked_similarity,
                                     inp=[name, error_tensor], Tout=[])

        with tf.control_dependencies([_co_assign, _co_py_func]):
            error_tensor = tf.identity(error_tensor)

        return error_tensor, similarity

    @ staticmethod
    def _on_tracked_similarity(name, error_val):
        """ Private function called whenever any of the tracked similarity is computed and its error value provided to the Python script (thus may access its value reliably).
        """
        allcompare = AllCompare.access_if_enabled()
        if allcompare is None:
            _logger.warning(
                "unexpected: AllCompare._on_tracked_similarity() called, but AllCompare service is not available.")
            return

        name = name.numpy().decode("ascii")
        error_val = float(error_val)

        similarities = allcompare.tracked_similarities
        if name not in similarities:
            _logger.warning(
                f"Similarity tensor '{name}' not tracked.")
            return

        similarity = similarities[name]
        similarity.value = error_val
        assert allcompare.global_generation >= similarity.generation, "Impossible condition met"
        if allcompare.global_generation == similarity.generation:
            allcompare.global_generation += 1
        similarity.generation = allcompare.global_generation
        similarity.value_history[similarity.generation] = error_val

        criterion = similarity.criterion if similarity.criterion is not None else allcompare.global_criterion
        if criterion is not None:
            is_err = not criterion(error_val)

            def format_error_val(v):
                return f"{v:.5f}" if not math.isinf(v) else "---"

            similarity.max_error = max(similarity.max_error, error_val)
            allcompare.max_error = max(allcompare.max_error, error_val)

            if is_err:
                similarity.error_count += 1
                allcompare.error_count += 1
                if allcompare.log_error:
                    _logger.error(
                        f"All-compare mismatch: '{name}'[{similarity.generation}] has error: {format_error_val(error_val)} (max:{format_error_val(similarity.max_error)} glob:{format_error_val(allcompare.max_error)})")
                if allcompare.stop_on_error:
                    raise RuntimeError("Stopping due to all-compare error.")
            else:
                if allcompare.log_ok:
                    _logger.info(
                        f"All-compare OK: '{name}'[{similarity.generation}] with value: {format_error_val(error_val)} (max:{format_error_val(similarity.max_error)} glob:{format_error_val(allcompare.max_error)})")

    @ property
    def broadcast_sample(self):
        """ Broadcast function used by the all-compare subsystem. May be broadcast based on Open MPI or tf.distribute.
        """
        return self.broadcast_sample_fn

    def expect_similar_workerbroad(self, tensor, name=None):
        """ Expects that the specified tensor is similar on all workers.
            Uses broadcast from worker:0 to build a comparison formula.
        """
        assert self.is_enabled, "Unable to use AllCompare feature unless enabled."
        return self.expect_similar(self.broadcast_sample(tensor), tensor, name=name, name_prefix="AllCompare/WorkerBroad")


class AllCompareStopOnErrorCallback(tf.keras.callbacks.Callback):
    """ A Keras callback which can halt the training on all-compare error.
    """

    def __init__(self, stop_on_error=True):
        self.allcompare = AllCompare.access_if_enabled()
        self.stop_on_error = stop_on_error

    def on_train_begin(self, logs=None):
        if self.allcompare is None:
            return

        self.allcompare.tracked_similarities.clear()

    def on_train_batch_end(self, batch, logs=None):
        if self.allcompare is None:
            return

        if self.stop_on_error and self.allcompare.error_count != 0:
            raise RuntimeError("Stopping due to all-compare errors.")

    def on_train_end(self, logs=None):
        if self.allcompare is None:
            return

        self.allcompare.tracked_similarities.clear()


def expect_similar(tensor, tensor_expected, name=None, name_prefix="AllCompare"):
    """ Expects that the specified pair of tensors are similar.
        Effectively computes the error formula and tracks its values (as there may be many error values for the same formulate in the future).
        If 'name' is not specified, it is build based on 'tensor_expected' (warning: not all tensors may have names in eager-execution mode).
    """
    allcompare = AllCompare.access_if_enabled()
    if allcompare is not None:
        return allcompare.expect_similar(tensor, tensor_expected, name=name, name_prefix=name_prefix)
    # else: return None


def expect_similar_workerbroad(tensor, name=None):
    """ Expects that the specified tensor is similar on all workers.
        Uses broadcast from worker:0 to build a comparison formula.
    """
    allcompare = AllCompare.access_if_enabled()
    if allcompare is not None:
        return allcompare.expect_similar_workerbroad(tensor, name=name)
    # else: return None
