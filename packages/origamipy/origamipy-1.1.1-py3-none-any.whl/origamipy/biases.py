"""Bias functions.

The classes here are intended to mirror some of the biases in the LatticeDNAOrigami
program, but also can include additional biases for using the MBAR method to extrapolate
to other thermodynamic states.

All bias classes should implement __call__(temp, order_parameters), and return the bias
in units of kb K. They should also implmement the propery fileformat_value to be some
or something trivially convertiable to a string (e.g. an int).
"""

import json

import numpy as np


STACK_TAG = "numstackedpairs"


class NoBias:
    """Null bias function that returns 0."""
    def __call__(self, *args):
        return 0

    @property
    def fileformat_value(self):
        return 0


class StackingBias:
    """Bias for the stacking energy based on a multiplier."""
    def __init__(self, stack_energy, stack_mult):
        self._stack_energy = stack_energy
        self._stack_mult = stack_mult
        self._complementary_stack_mult = 1 - float(stack_mult)

    def __call__(self, temp, order_params):
        total_stack_energy = order_params[STACK_TAG] * self._stack_energy
        return -total_stack_energy * self._complementary_stack_mult

    @property
    def fileformat_value(self):
        return self._stack_mult


class HybridizationBias:
    """Bias for the average hybridization energy.

    The entropy is multiplied by temperature so that it can return the energy in units
    of kb K. This is because I end up dividing the bias by temperature later, as all
    biases before this one were plain energies, while here it is has an entropic
    component, which should not be divided by temperature to get the unitless exponent
    for the ensemble distribution.
    """
    def __init__(self, bindh, binds, misbindh, misbinds, hyb_mult):
        self._bindh = bindh
        self._binds = binds
        self._misbindh = misbindh
        self._misbinds = misbinds
        self._hyb_mult = hyb_mult
        self._complementary_hyb_mult = 1 - float(hyb_mult)

    def __call__(self, temp, order_params):
        bdomains = order_params["numfulldomains"]
        mdomains = order_params["nummisdomains"]
        bound_hyb_energy = bdomains * (self._bindh - self._binds * temp)
        misbound_hyb_energy = mdomains * (self._misbindh - self._misbinds * temp)
        total_hyb_energy = bound_hyb_energy + misbound_hyb_energy

        return -total_hyb_energy * self._complementary_hyb_mult

    @property
    def fileformat_value(self):
        return self._hyb_mult


class GridBias:
    """Grid bias with linear step well outside grid.

    It assumes that the input bias is desired, not the bias calculated for that
    iteration. The biases are written in kb T, so here the energy is multiplied by
    temperature as the bias is later divided by temperature.
    """

    def __init__(self, tags, window, min_outside_bias, slope, inp_filebase, itr):
        self._tags = tags
        self._window = window
        self._min_outside_bias = min_outside_bias
        self._slope = slope

        # Create window file postfix
        self._postfix = "_win"
        for win_min in window[0]:
            self._postfix += "-" + str(win_min)

        self._postfix += "-"
        for win_max in window[1]:
            self._postfix += "-" + str(win_max)

        # Read biases from file
        self._postfix += f"_iter-{itr}"
        filename = f"{inp_filebase}{self._postfix}-inp.biases"
        grid_biases = json.load(open(filename))
        self._grid_biases = {}
        for entry in grid_biases["biases"]:
            point = tuple(entry["point"])
            bias = entry["bias"]
            self._grid_biases[point] = bias

    def __call__(self, temp, order_params):
        biases = []
        for step in range(order_params.steps):
            point = tuple(order_params[tag][step] for tag in self._tags)
            bias = 0

            # Grid bias
            if point in self._grid_biases.keys():
                bias += self._grid_biases[point]

            # Linear step bias
            for i, param in enumerate(point):
                min_param = self._window[0][i]
                max_param = self._window[1][i]
                if param < min_param:
                    bias += self._slope * (min_param - param - 1)
                    bias += self._min_outside_bias
                elif param > max_param:
                    bias = self._slope * (param - max_param - 1)
                    bias += self._min_outside_bias

            biases.append(bias)

        return np.array(biases) * temp

    @property
    def fileformat_value(self):
        return self._postfix


class TotalBias:
    """Sum of all individual biases."""
    def __init__(self, biases):
        self._biases = biases

    def __call__(self, temp, order_params):
        return sum([bias(temp, order_params) for bias in self._biases])
