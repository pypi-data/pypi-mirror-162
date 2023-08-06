#!/usr/bin/python

"""Plot LFEs for given order parameter across temperature range."""

import argparse

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlibstyles import styles
from matplotlibstyles import plotutils

from origamipy import plotting


def main():
    args = vars(parse_args())
    f = setup_figure()
    gs = gridspec.GridSpec(1, 1, f)
    ax = f.add_subplot(gs[0, 0])
    axes = [ax, ax.twiny()]

    p = plotting.LFEsRepTempsPlot(args)
    p.plot_figure(axes)
    p.setup_axis(axes)
    #    set_labels(f, ax, mappable)
    plot_filebase = f"{args['plots_dir']}/{args['filebase']}"
    save_figure(f, plot_filebase)


def setup_figure():
    styles.set_default_style()
    figsize = (plotutils.cm_to_inches(10), plotutils.cm_to_inches(7))

    return plt.figure(figsize=figsize, dpi=300, constrained_layout=True)


def set_labels(f, ax, mappable):
    plt.legend()


def save_figure(f, plot_filebase):
    # f.savefig(plot_filebase + '.pgf', transparent=True)
    f.savefig(plot_filebase + ".pdf", transparent=True)
    f.savefig(plot_filebase + ".png", transparent=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input_dir", type=str, help="Directory of inputs")
    parser.add_argument("plots_dir", type=str, help="Plots directory")
    parser.add_argument("filebase", type=str, help="Filebase")

    return parser.parse_args()


if __name__ == "__main__":
    main()
