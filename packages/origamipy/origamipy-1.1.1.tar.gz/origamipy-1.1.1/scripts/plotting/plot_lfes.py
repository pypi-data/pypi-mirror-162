#!/usr/bin/python

"""Plot LFEs of given order parameter."""

import argparse

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlibstyles import styles
from matplotlibstyles import plotutils

from origamipy import plotting


def main():
    args = parse_args()
    f = setup_figure()
    gs = gridspec.GridSpec(1, 1, f)
    ax = f.add_subplot(gs[0, 0])
    if args.post_lfes == None:
        args.post_lfes = ["" for _ in range(len(args.systems))]

    args = vars(args)

    p = plotting.LFEsPlot(args)
    p.plot_figure(f, ax)
    p.setup_axis(ax, ylabel=args["tag"])
    # p.set_labels(ax)
    plotting.save_figure(f, args["plot_filebase"])


def setup_figure():
    styles.set_default_style()
    figsize = (plotutils.cm_to_inches(10), plotutils.cm_to_inches(7))

    return plt.figure(figsize=figsize, dpi=300, constrained_layout=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input_dir", type=str, help="Input directory")
    parser.add_argument("plot_filebase", type=str, help="Plots directory")
    parser.add_argument("tag", type=str, help="OP tag")
    parser.add_argument("--systems", nargs="+", type=str, help="Systems")
    parser.add_argument("--varis", nargs="+", type=str, help="Simulation variants")
    parser.add_argument(
        "--post_lfes", nargs="+", type=str, help="Filename additions after lfes, if any"
    )
    parser.add_argument(
        "--stacking_enes",
        nargs="+",
        type=float,
        help="Stacking energies (for colormap)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
