"""
network.py

Contains the tensorflow implementation of the Normalizing Flow network

used to train the L2HMC model.
"""
from __future__ import absolute_import, annotations, division, print_function
from typing import Optional

import logging
import numpy as np

import tensorflow as tf

from l2hmc.configs import (
    NetWeight,
    NetworkConfig,
    ConvolutionConfig
)

from l2hmc.network.tensorflow.utils import PeriodicPadding

log = logging.getLogger(__name__)

TF_FLOAT = tf.keras.backend.floatx()
Conv2d = tf.keras.layers.Conv2D

Tensor = tf.Tensor
Model = tf.keras.Model
Layer = tf.keras.layers.Layer
Add = tf.keras.layers.Add
Input = tf.keras.layers.Input
Dense = tf.keras.layers.Dense
Conv2D = tf.keras.layers.Conv2D
Dropout = tf.keras.layers.Dropout
Flatten = tf.keras.layers.Flatten
Reshape = tf.keras.layers.Reshape
Multiply = tf.keras.layers.Multiply
Activation = tf.keras.layers.Activation
MaxPooling2D = tf.keras.layers.MaxPooling2D
BatchNormalization = tf.keras.layers.BatchNormalization


class ScaledTanh(Layer):
    def __init__(
            self,
            units: int,
            name: Optional[str] = None,
            **kwargs,
    ) -> None:
        super(ScaledTanh, self).__init__(name=name, **kwargs)
        self.units = units

    def build(self, input_shape):
        self.coeff = self.add_weight(
            shape=(1, self.units),
            initializer='zeros',
            trainable=True,
        )
        self.w = self.add_weight(shape=(input_shape[-1], self.units),
                                 initializer='random_normal',
                                 trainable=True)
        self.b = self.add_weight(shape=(self.units,),
                                 initializer='zeros',
                                 trainable=True)

    def call(self, inputs):
        return tf.math.exp(self.coeff) * tf.math.tanh(
            tf.matmul(inputs, self.w) + self.b
        )


ACTIVATION_FNS = {
    'elu': tf.keras.activations.elu,
    'tanh': tf.keras.activations.tanh,
    'relu': tf.keras.activations.relu,
    'swish': tf.keras.activations.swish,
}


class LeapfrogLayer(Model):
    def __init__(
            self,
            xshape: tuple[int],
            network_config: NetworkConfig,
            input_shapes: Optional[dict[str, tuple[int, int]]] = None,
            net_weight: Optional[NetWeight] = None,
            conv_config: Optional[ConvolutionConfig] = None,
            name: Optional[str] = None,
    ) -> None:
        super().__init__()
        if net_weight is None:
            net_weight = NetWeight(1., 1., 1.)

        self.name = name if name is not None else 'network'
        self.xshape = xshape
        self.net_config = network_config
        self.nw = net_weight
        self.xdim = int(np.cumprod(xshape[1:])[-1])
        if input_shapes is None:
            input_shapes = {
                'x': (int(self.xdim), int(2)),
                'v': (int(self.xdim), int(1)),
            }

        self.input_shapes = {}
        for key, val in input_shapes.items():
            if isinstance(val, (list, tuple)):
                self.input_shapes[key] = np.cumprod(val)[-1]
            elif isinstance(val, int):
                self.input_shapes[key] = val
            else:
                raise ValueError(
                    'Unexpected value in input shapes!'
                )

        act_fn = self.net_config.activation_fn
        if isinstance(act_fn, str):
            act_fn = ACTIVATION_FNS.get(act_fn, None)

        assert callable(act_fn)
        self.activation_fn = act_fn
        self.units = self.net_config.units
        if conv_config is not None and len(conv_config.filters) > 0:
            self.conv_config = conv_config
            if len(xshape) == 3:
                d, nt, nx = xshape[0], xshape[1], xshape[2]
            elif len(xshape) == 4:
                _, d, nt, nx = xshape[0], xshape[1], xshape[2], xshape[3]
            else:
                raise ValueError(f'Invalid value for `xshape`: {xshape}')

            self.nt = nt
            self.nx = nx
            self.d = d
            # p0 = PeriodicPadding(conv_config.sizes[0] - 1)
            conv_stack = []
            iterable = enumerate(zip(conv_config.filters, conv_config.sizes))
            for idx, (f, n) in iterable:
                conv_stack.append(
                    PeriodicPadding(n - 1)
                )
                conv_stack.append(
                    Conv2D(f, n, activation=self.activation_fn)
                )
                if (idx + 1) % 2 == 0:
                    conv_stack.append(
                        MaxPooling2D((2, 2), name=f'{name}/xPool{idx}')
                    )

            conv_stack = [
                PeriodicPadding(conv_config.sizes[0] - 1),
                Conv2d(d, conv_config.filters[0], conv_config.sizes[0])
            ]
            # TODO: FIX
            # iterable = zip(conv_config.filters[1:], conv_config.sizes[1:])
            # for idx, (f, n) in enumerate(iterable):
            #     conv_stack.append(PeriodicPadding(n - 1))
            #     conv_stack.append(nn.LazyConv2d(n, f))
            #     # , padding=(n-1), padding_mode='circular'))
            #     # conv_stack.append(self.activation_fn)
            #     if (idx + 1) % 2 == 0:
            #         conv_stack.append(nn.MaxPool2d(conv_config.pool[idx]))

            # conv_stack.append(nn.Flatten(1))
            # if network_config.use_batch_norm:
            #     conv_stack.append(nn.BatchNorm1d(-1))

            # self.conv_stack = nn.ModuleList(conv_stack)

        else:
            self.conv_stack = []

        self.flatten = Flatten(1)
        self.x_layer = Dense(self.units[0], name=f'{name}_xlayer')
        self.v_layer = Dense(self.units[0], name=f'{name}_vlayer')
        self.hidden_layers = []
        for idx, units in enumerate(self.units[1:]):
            self.hidden_layers.append(Dense(units, name=f'{name}_hidden{idx}'))
            # h = nn.Linear(self.units[idx], units)
            # self.hidden_layers.append(h)

        self.scale = ScaledTanh(self.xdim, name=f'{name}_scale')
        self.transf = ScaledTanh(self.xdim, name=f'{name}_transf')
        self.transl = Dense(self.xdim, name=f'{name}_transl')
        self.dropout = None
        if self.net_config.dropout_prob > 0:
            self.dropout = Dropout(
                self.net_config.dropout_prob
            )

        self.batch_norm = None
        if self.net_config.use_batch_norm:
            self.batch_norm = BatchNormalization(-1, name=f'{name}_batchnorm')

    def call(
            self,
            inputs: tuple[Tensor, Tensor],
            training: Optional[bool] = None,
    ) -> tuple[Tensor, Tensor, Tensor]:
        x, v = inputs
        z = self.activation_fn(self.x_layer(x) + self.v_layer(v))
        for layer in self.hidden_layers:
            z = self.activation_fn(layer(z))

        if self.dropout is not None:
            z = self.dropout(z, training=training)

        if self.batch_norm is not None:
            z = self.batch_norm(z, training=training)

        s = self.nw.s * self.scale(z)
        t = self.nw.t * self.transl(z)
        q = self.nw.q * self.transf(z)

        return s, t, q
