###############################################################################
# Copyright (C) 2022 Habana Labs, Ltd. an Intel Company
###############################################################################
import tensorflow as tf
from tensorflow.python.framework import ops

def _register_grad(habana_ops):
    @ops.RegisterGradient("HabanaSoftmax")
    def _HabanaSoftmaxGrad(op, *grads):
        return habana_ops.habana_softmax_grad(y=op.outputs[0], dzdy=grads[0], axis=tf.make_tensor_proto(op.get_attr('axis')))
