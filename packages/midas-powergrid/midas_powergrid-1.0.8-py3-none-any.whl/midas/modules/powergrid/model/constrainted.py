from typing import List

from ..elements.bus import PPBus
from ..elements.line import PPLine
from ..elements.load import PPLoad
from ..elements.sgen import PPSgen
from ..elements.transformer import PPTransformer
from . import LOG
from .static import PandapowerGrid


class ConstraintedGrid(PandapowerGrid):
    def __init__(self, constraints):
        super().__init__()

        self._constraints_to_load = constraints
        self.constraints = dict()
        self._lf_states: List[bool] = []  # just for more precise logging

    def setup(self, gridfile, grid_idx, grid_params):
        super().setup(gridfile, grid_idx, grid_params)

        self._load_constraints()

    def set_inputs(self, etype, idx, data):
        etype = etype.lower()
        if etype not in ["load", "sgen", "trafo", "switch", "storage"]:
            LOG.info("Invalid etype %s. Skipping.", etype)
            return False

        for name, value in data.items():
            self.grid[etype].at[idx, name] = value

            if etype in self.constraints:
                # Constraint can change the value
                setattr(self.constraints[etype][idx], name, value)

    def run_powerflow(self, time, max_iter=2):

        self._lf_states.append(self.lf_converged)  # previous state

        # Run once to check current state
        super().run_powerflow(time)

        if time < 0:
            # The first step is done before the simulation to make use
            # of numba's speed-up during the simulation
            return

        state_changed = False

        # Now constraints can change the input state if necessary
        # Constraints will definitively change the state of the grid
        # so another power flow calculation is required afterwards
        for key in ["trafo", "load", "sgen", "line", "bus"]:
            if key not in self.constraints:
                continue
            for element in self.constraints[key]:
                state_changed = element.step(time) or state_changed

        # Maybe more elements were put out of service than necessary
        # e.g., when the critical element is the last one checked.
        # Performing another iteration allows elements to switch on
        # again if no constraints are violated.
        if max_iter > 1:
            return self.run_powerflow(time, max_iter - 1)

        super().run_powerflow(time)
        if state_changed:
            if not self._lf_states[0] and self.lf_converged:
                LOG.info(f"At step {time}: Constraints fixed failing LF.")
            if not self._lf_states[0] and not self.lf_converged:
                LOG.info(f"At step {time}: LF still not converging.")
            if self._lf_states[0] and not self.lf_converged:
                LOG.info(f"At step {time}: LF broke due to constraints.")
            if self._lf_states[0] and self.lf_converged:
                LOG.info(f"At step {time}: LF still converging.")

        self._lf_states = []

    def _load_constraints(self):
        for constr in self._constraints_to_load:
            etype, value = constr
            self.constraints.setdefault(etype, list())
            for idx in range(len(self.grid[etype])):
                self.constraints[etype].append(self._create(etype, idx, value))

    def _create(self, etype, index, value):
        if etype == "trafo":
            clazz = PPTransformer
        # if classname == PPTransformer:
        #     etype = self.grid[classname.pp_key()]["std_type"][index]

        #     return PPTransformer(index, self.grid)
        # TODO: elif other elements
        elif etype == "bus":
            clazz = PPBus
        elif etype == "load":
            clazz = PPLoad
        elif etype == "sgen":
            clazz = PPSgen
        elif etype == "line":
            clazz = PPLine
        return clazz(index, self.grid, value)
