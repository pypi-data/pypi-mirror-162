###############################################################################
# Copyright (C) 2021-2022 Habana Labs, Ltd. an Intel Company
###############################################################################
from tensorflow.python.framework import ops


def _register_grad(habana_ops):
    @ops.RegisterGradient("HabanaGelu")
    def _HabanaGeluGrad(op, *grads):
        return habana_ops.habana_gelu_grad(grad_input=grads[0], input=op.inputs[0], tanh=op.outputs[1],
                                           approximate=op.get_attr('approximate'))
