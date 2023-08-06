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
    @ops.RegisterGradient("HabanaInstanceNorm")
    def _HabanaInstanceNorm(op, *grads):
        """ Return the gradients for the HabanaInstanceNorm.

        Args:
        op: HabanaInstanceNormOp for which we compute gradients.
        *grad: An argument list for tensors of gradients wrt the outputs
            with grad[0] as grad_y.

        Returns:
        grad_x: gradient for x
        grad_beta: gradient for beta (bias)
        grad_gamma: gradient for gamma (scale)
        """
        return habana_ops.habana_instance_norm_grad(
            input=op.inputs[0],
            grad_in=grads[0],
            gamma=op.inputs[2],
            mean=op.outputs[1],
            istd=op.outputs[2],
            epsilon=op.get_attr('epsilon'),
            axis=op.get_attr('axis')
    )
