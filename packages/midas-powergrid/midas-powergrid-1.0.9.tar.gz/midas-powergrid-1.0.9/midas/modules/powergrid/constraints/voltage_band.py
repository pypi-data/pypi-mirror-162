import numpy as np
from midas.modules.powergrid.elements.base import GridElement

from .base import Constraint


class ConstraintVoltageBand(Constraint):
    def __init__(
        self, element: GridElement, lower_band: float, upper_band: float
    ):
        super().__init__(element)

        self._vm_pu_max = upper_band
        self._vm_pu_min = lower_band

        self.over_voltage = False
        self.under_voltage = False

    def check(self, time) -> bool:
        self.satisfied = True
        voltage = self._element.grid.res_bus.vm_pu.loc[self._element.index]

        self.over_voltage = voltage > self._vm_pu_max
        self.under_voltage = voltage < self._vm_pu_min

        if np.isnan(voltage) or self.over_voltage or self.under_voltage:
            self.satisfied = False
            self.violated_value = voltage

        return self.satisfied

    def handle_violation(self):

        self._element.set_load_service_state(in_service=False)
        self._element.set_sgen_service_state(in_service=False)

        self._element.in_service = False
