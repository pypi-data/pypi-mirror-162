"""
hmc.py

"""
from __future__ import absolute_import, division, print_function, annotations
from typing import Optional

from l2hmc.experiment.experiment import BaseExperiment


from abc import ABC, abstractmethod


class HamiltonianMonteCarlo(ABC):
    def __init__(
            self,
            experiment: BaseExperiment,
            beta: Optional[float] = 1.0,
            nlog: Optional[int] = 10,
            nleapfrog: Optional[int] = None,
            eps: Optional[float] = None,
            nsteps: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.experiment = experiment

