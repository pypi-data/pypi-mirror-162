###############################################################################
# Copyright (C) 2020-2021 Habana Labs, Ltd. an Intel Company
###############################################################################
from habana_frameworks.tensorflow import habana_ops
from habana_frameworks.tensorflow import impl_override_utils

from tensorflow.python.framework import tensor_util
from tensorflow.keras import constraints
from tensorflow.keras import initializers
from tensorflow.keras import regularizers
from tensorflow.keras.layers import LayerNormalization


class HabanaLayerNormalization(LayerNormalization):
    """
    Has the same behaviour as
    https://www.tensorflow.org/api_docs/python/tf/keras/layers/LayerNormalization

    If other device than HPU is explicitly assigned, then it will fallback to regular implementation.
    """

    def __new__(cls, *args, **kwargs):
        return impl_override_utils.select_keras_layer(HabanaLayerNormalization, LayerNormalization, cls, *args, **kwargs)

    def __init__(self,
                 axis=-1,
                 epsilon=1e-3,
                 center=True,
                 scale=True,
                 beta_initializer='zeros',
                 gamma_initializer='ones',
                 beta_regularizer=None,
                 gamma_regularizer=None,
                 beta_constraint=None,
                 gamma_constraint=None,
                 **kwargs):
        super(HabanaLayerNormalization, self).__init__(**kwargs)
        if isinstance(axis, (list, tuple)):
            self.axis = axis[:]
        elif isinstance(axis, int):
            self.axis = axis
        else:
            raise TypeError('Expected an int or a list/tuple of ints for the '
                            'argument \'axis\', but received: %r' % axis)

        self.epsilon = epsilon
        self.center = center
        self.scale = scale
        self.beta_initializer = initializers.get(beta_initializer)
        self.gamma_initializer = initializers.get(gamma_initializer)
        self.beta_regularizer = regularizers.get(beta_regularizer)
        self.gamma_regularizer = regularizers.get(gamma_regularizer)
        self.beta_constraint = constraints.get(beta_constraint)
        self.gamma_constraint = constraints.get(gamma_constraint)

        self.supports_masking = True

    def build(self, input_shape):
        ndims = len(input_shape)
        if ndims is None:
            raise ValueError(
                'Input shape %s has undefined rank.' % input_shape)

        # Convert axis to list and resolve negatives
        if isinstance(self.axis, int):
            self.axis = [self.axis]
        elif isinstance(self.axis, tuple):
            self.axis = list(self.axis)
        for idx, x in enumerate(self.axis):
            if x < 0:
                self.axis[idx] = ndims + x

        # Validate axes
        for x in self.axis:
            if x < 0 or x >= ndims:
                raise ValueError('Invalid axis: %d' % x)
        if len(self.axis) != len(set(self.axis)):
            raise ValueError('Duplicate axis: {}'.format(tuple(self.axis)))

        param_shape = [input_shape[dim] for dim in self.axis]
        if self.scale:
            self.gamma = self.add_weight(
                name='gamma',
                shape=param_shape,
                initializer=self.gamma_initializer,
                regularizer=self.gamma_regularizer,
                constraint=self.gamma_constraint,
                trainable=True,
                experimental_autocast=False)
        else:
            self.gamma = None

        if self.center:
            self.beta = self.add_weight(
                name='beta',
                shape=param_shape,
                initializer=self.beta_initializer,
                regularizer=self.beta_regularizer,
                constraint=self.beta_constraint,
                trainable=True,
                experimental_autocast=False)
        else:
            self.beta = None

        self.built = True

    def call(self, inputs):
        outputs, _, _ = habana_ops.habana_layer_norm(
            x=inputs,
            beta=self.beta,
            gamma=self.gamma,
            axes=tensor_util.make_tensor_proto(self.axis),
            epsilon=tensor_util.make_tensor_proto(self.epsilon)
        )
        return outputs

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {
            'axis': self.axis,
            'epsilon': self.epsilon,
            'center': self.center,
            'scale': self.scale,
            'beta_initializer': initializers.serialize(self.beta_initializer),
            'gamma_initializer': initializers.serialize(self.gamma_initializer),
            'beta_regularizer': regularizers.serialize(self.beta_regularizer),
            'gamma_regularizer': regularizers.serialize(self.gamma_regularizer),
            'beta_constraint': constraints.serialize(self.beta_constraint),
            'gamma_constraint': constraints.serialize(self.gamma_constraint)
        }
        base_config = super(HabanaLayerNormalization, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


def _override_op():
    import tensorflow.keras
    tensorflow.keras.layers.LayerNormalization = HabanaLayerNormalization
