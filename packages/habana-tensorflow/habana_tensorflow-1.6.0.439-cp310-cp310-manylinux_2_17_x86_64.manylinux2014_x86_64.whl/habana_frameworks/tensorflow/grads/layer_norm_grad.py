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
from tensorflow.python.framework import ops


def _register_grad(habana_ops):
    @ops.RegisterGradient("HabanaLayerNorm")
    def _HabanaLayerNorm(op, *grads):
        """ Return the gradients for the 3 inputs of HabanaLayerNorm.

        Args:
        op: HabanaLayerNormOp for which we compute gradients.
        *grad: An argument list for tensors of gradients wrt the outputs
            with grad[0] as grad_y.

        Returns:
        grad_x: gradient for x
        grad_beta: gradient for beta (bias)
        grad_gamma: gradient for gamma (scale)
        """

        return habana_ops.habana_layer_norm_grad(
            x=op.inputs[0],
            grad_in=grads[0],
            mean=op.outputs[1],
            istd=op.outputs[2],
            gamma=op.inputs[2],
            epsilon=op.get_attr('epsilon'),
            axes=op.get_attr('axes')
    )