###############################################################################
# Copyright (C) 2021-2022 Habana Labs, Ltd. an Intel Company
###############################################################################

import tensorflow as tf
from tensorflow.python.framework import ops

from habana_frameworks.tensorflow import habana_ops
from habana_frameworks.tensorflow.impl_override_utils import select_tf_op

__all__ = ['habana_gelu']

_old_gelu_fn = tf.nn.gelu


def _habana_gelu_impl(features, approximate=False, name=None):
    features = ops.convert_to_tensor(features, name="features")
    output, _ = habana_ops.habana_gelu(
        data_input=features, approximate=approximate)
    return output


def habana_gelu(features, approximate=False, name=None):
    """
    Has the same behaviour as
    https://www.tensorflow.org/api_docs/python/tf/nn/gelu

    If other device than HPU is explicitly assigned, then it will fallback to regular implementation.
    """
    return select_tf_op(_habana_gelu_impl, _old_gelu_fn, features, approximate=approximate, name=name)


def _override_op():
    tf.nn.gelu = habana_gelu
    tf.keras.activations.gelu = habana_gelu
