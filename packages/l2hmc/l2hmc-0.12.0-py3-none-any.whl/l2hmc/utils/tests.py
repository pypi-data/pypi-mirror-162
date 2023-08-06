"""
utils/tests.py

Contains simple tests.
"""
from __future__ import absolute_import, division, print_function, annotations
from typing import Optional, Union

import l2hmc.configs as cfgs

import logging
import numpy as np

import torch
import tensorflow as tf
from l2hmc.dynamics.pytorch.dynamics import State as ptState
from l2hmc.dynamics.tensorflow.dynamics import State as tfState


log = logging.getLogger(__name__)

StateLike = Union[cfgs.State, ptState, tfState]


def grab(x: torch.Tensor) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        return x.detach().numpy()


def check_diff(x, y, name: Optional[str] = None):
    if isinstance(x, StateLike) and isinstance(y, StateLike):
        xd = {'x': x.x, 'v': x.v, 'beta': x.beta}
        yd = {'x': y.x, 'v': y.v, 'beta': y.beta}
        for (kx, vx), (_, vy) in zip(xd.items(), yd.items()):
            check_diff(vx, vy, name=f'State.{kx}')

    if isinstance(x, dict) and isinstance(y, dict):
        for (kx, vx), (_, vy) in zip(x.items(), y.items()):
            check_diff(vx, vy, name=kx)
    else:
        if isinstance(x, torch.Tensor):
            x = grab(x)

        if isinstance(y, torch.Tensor):
            y = grab(y)

        if isinstance(x, tf.Tensor):
            x = x.numpy()  # type: ignore
        if isinstance(y, tf.Tensor):
            y = y.numpy()  # type: ignore

        dstr = []
        diff = (x - y)
        if name is not None:
            dstr.append(f"'{name}''")
        dstr.append(f'  sum(diff): {diff.sum()}')
        dstr.append(f'  min(diff): {diff.min()}')
        dstr.append(f'  max(diff): {diff.max()}')
        dstr.append(f'  mean(diff): {diff.mean()}')
        dstr.append(f'  std(diff): {diff.std()}')
        dstr.append(f'  np.allclose: {np.allclose(x, y)}')
        log.info('\n'.join(dstr))
