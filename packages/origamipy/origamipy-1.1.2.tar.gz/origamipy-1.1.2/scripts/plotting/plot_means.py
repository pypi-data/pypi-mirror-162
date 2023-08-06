#!/usr/bin/python

"""Plot an order parameter from multiple simulations."""

import argparse

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlibstyles import styles
from matplotlibstyles import plotutils

from origamipy import plotting


def main():
    args = vars(parse_args())
    f = setup_figure()
    gs = gridspec.GridSpec(1, 1, f)
    ax = f.add_subplot(gs[0])

    p = plotting.MeansPlot(args)
    p.plot_figure(ax)
    p.setup_axis(ax, args["tag"], None)
    #    set_labels(ax, ax)
    plotting.save_figure(f, args["plot_filebase"])


def setup_figure():
    styles.set_thin_style()
    figsize = (plotutils.cm_to_inches(14), plotutils.cm_to_inches(11))

    return plt.figure(figsize=figsize, dpi=300, constrained_layout=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input_dir", type=str, help="Directory of inputs")
    parser.add_argument("plot_filebase", type=str, help="Plots directory")
    parser.add_argument("tag", type=str, help="OP tag")
    parser.add_argument(
        "--assembled_values",
        nargs="+",
        type=int,
        help="Values of OP in assembled state",
    )
    parser.add_argument("--systems", nargs="+", type=str, help="Systems")
    parser.add_argument("--varis", nargs="+", type=str, help="Simulation variants")
    parser.add_argument(
        "--posts",
        nargs="+",
        type=str,
        help="Extra part of mean name (e.g. _temps for MWUS extrapolation",
    )
    parser.add_argument(
        "--nncurves", nargs="+", type=bool, help="Include shifted NN curve"
    )
    parser.add_argument(
        "--staple_M", default="", type=float, help="Staple concentration"
    )
    parser.add_argument(
        "--binds", default="", type=float, help="Domain binding entropy"
    )
    parser.add_argument(
        "--bindh", default="", type=float, help="Domain binding enthalpy"
    )
    parser.add_argument("--stackene", default="", type=float, help="Stacking energy")
    parser.add_argument(
        "--continuous", nargs="+", type=bool, help="Plot curves as continuous"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
