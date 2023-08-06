###############################################################################
# Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################

from tensorflow.python.eager import context
from tensorflow.python.framework import ops
from habana_frameworks.tensorflow import habana_ops


def get_device_name():
    """Returns device name, or empty string if not available.

    Returns:
        Device name.
    """
    if context.executing_eagerly():
        return context.get_device_name()
    else:
        g = ops.get_default_graph()
        device_stack_len = len(g._device_function_stack)
        return g._device_function_stack.peek_top_obj()._device_name_or_function if device_stack_len > 0 else ""


def select_keras_layer(new_layer, old_layer, cls, *args, **kwargs):
    """Provides Habana-specific version of Layer, or original implementation when conditions are not met.
    Conditions for override:
    - op override must be allowed
    - device is not explicitly set to other device than HPU
    - new layer should inherit from old layer
    This function is meant to be used within '__new__'.

    Args:
        new_layer: Habana-specific layer
        old_layer: original Keras layer

    Returns:
        Layer.
    """
    device_name = get_device_name()
    if not habana_ops.is_op_override_allowed or (device_name and 'HPU' not in device_name):
        instance = super(new_layer, cls).__new__(old_layer)
        # Old layer is not a subclass of new layer, so __init__ must be run manually.
        old_layer.__init__(instance, *args, **kwargs)
        return instance
    else:
        return super(new_layer, cls).__new__(new_layer, *args, **kwargs)


def select_tf_op(new_op, old_op, *args, **kwargs):
    """Provides Habana-specific version of Op, or original implementation when conditions are not met.
    Conditions for override:
    - op override must be allowed
    - device is not explicitly set to other device than HPU
    This function in meant to be used within Habana-specific function.

    Args:
        new_op: Habana-specific op
        old_op: original TensorFlow op

    Returns:
        Op.
    """
    device_name = get_device_name()
    if not habana_ops.is_op_override_allowed or (device_name and 'HPU' not in device_name):
        return old_op(*args, **kwargs)
    else:
        return new_op(*args, **kwargs)