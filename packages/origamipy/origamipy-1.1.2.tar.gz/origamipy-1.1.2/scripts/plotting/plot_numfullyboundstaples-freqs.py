#!/usr/bin/python

"""Plot frequencies of configurations at given order parameter."""

import argparse

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlibstyles import styles
from matplotlibstyles import plotutils

from origamipy import plotting


def main():
    args = parse_args()
    f = setup_figure()
    gs = gridspec.GridSpec(args.stapletypes - 1, 1, f)
    axes = []
    for i in range(args.stapletypes - 1):
        axes.append(f.add_subplot(gs[i, 0]))

    plot_filebase = (
        f"{args.plot_dir}/{args.filebase}_" f"{args.slice_tag}-{args.tagbase}_freqs"
    )

    args = vars(args)

    p = plotting.NumFullyBoundStaplesFreqsPlot(args)
    p.plot_figure(axes)
    p.setup_axes(axes)
    p.set_labels(f, axes)
    plotting.save_figure(f, plot_filebase)


def setup_figure():
    styles.set_thin_style()
    figsize = (plotutils.cm_to_inches(5), plotutils.cm_to_inches(20))

    return plt.figure(figsize=figsize, dpi=300, constrained_layout=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input_dir", type=str, help="Directory of inputs")
    parser.add_argument("plot_dir", type=str, help="Output directory")
    parser.add_argument("filebase", type=str, help="Filebase")
    parser.add_argument("stapletypes", type=int, help="Number of staple types")
    parser.add_argument("mapfile", type=str, help="Index-to-staple type map filename")
    parser.add_argument(
        "--slice_tag",
        default="numfullyboundstaples",
        type=str,
        help="OP tag to slice along",
    )
    parser.add_argument(
        "--tagbase", default="staplestates", type=str, help="OP tag base"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
