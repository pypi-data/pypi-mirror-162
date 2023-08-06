#!/usr/bin/python

"""Plot numfulldomains and numfullybound staples LFEs.

Has not been tested recently, so consider only as a starting point.
"""

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
    axes = [ax, ax.twiny()]
    if args.post_lfes == None:
        args.post_lfes = [""] * 3

    args = vars(args)

    p = plotting.LFEsFullDomainsFullyBoundStaplesPlot(args)
    p.plot_figure(axes)
    p.setup_axis(axes)
    # set_labels(axes)
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
    parser.add_argument("system", type=str, help="System")
    parser.add_argument("--varis", nargs="+", type=str, help="Simulation variants")
    parser.add_argument(
        "--post_lfes", nargs="+", type=str, help="Filename additions after lfes, if any"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
