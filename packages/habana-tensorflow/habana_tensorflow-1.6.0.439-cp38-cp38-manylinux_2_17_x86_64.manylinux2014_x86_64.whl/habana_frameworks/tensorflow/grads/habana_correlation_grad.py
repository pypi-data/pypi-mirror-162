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
    @ops.RegisterGradient("HabanaCorrelation")
    def _HabanaCorrelationGrad(op, *grads):
        """Returns grad * (y*x^(y-1), z*log(x))."""
        grads_list = list(grads)
        cntr = op.inputs[0]
        srnd = op.inputs[1]
        scales = op.inputs[2]
        trans_x = op.inputs[3]
        trans_y = op.inputs[4]
        interp = op.outputs[1]
        grid = op.outputs[2]
        grads = habana_ops.ops.habana_correlation_grad(
            grad_in=grads_list[0], cntr=cntr, interp=interp, grid=grid, name=op.name+"_grad")
        return grads.cntr_grad, grads.srnd_grad, scales, trans_x, trans_y
