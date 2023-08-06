"""
pytorch/test_lattice.py

Implements basic methods for testing lattice objects.
"""
from __future__ import absolute_import, division, print_function, annotations

import torch
from math import pi as PI
from scipy.special import i1, i0

TWO_PI = 2. * PI

Tensor = torch.Tensor

from l2hmc.lattice.pytoch.lattice import plaq_exact
