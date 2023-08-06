#!/usr/bin/python

"""Plot order parameter series for all threads and reps.

Plots number of bound staples, number of bound domains, number of misbound
domains, and number of stacked pairs.

Has not been tested recently, so consider only as a starting point.
"""

import argparse

import matplotlib.pyplot as plt
from matplotlibstyles import styles
from matplotlibstyles import plotutils
import numpy as np

from origamipy import plotting


def main():
    args = parse_args()
    skip = 1
    out_filebase = "{}/{}-{}_timeseries".format(args.output_dir, args.system, args.vari)
    tags = ["numstaples", "numfulldomains", "nummisdomains", "numstackedpairs"]
    labels = ["Bound staples", "Bound domains", "Misbound domains", "Stacked pairs"]
    figsize = (
        plotutils.cm_to_inches(10),
        plotutils.cm_to_inches(args.reps * 7 * len(args.temps)),
    )
    styles.set_default_style()
    f, axes = plt.subplots(args.reps * len(args.temps), 1, figsize=figsize, dpi=300)

    ax_i = -1
    for temp in args.temps:
        for rep in range(args.reps):
            ax_i += 1
            ax = axes[ax_i]
            ax.set_xlabel("Walltime / s")
            ax.set_title(f"T={temp}, rep={rep}")

            timeseries = {}
            times = []
            for tag in tags:
                timeseries[tag] = []

            for run in range(args.runs):
                filebase = "{}/{}-{}_run-{}_rep-{}-{}".format(
                    args.input_dir, args.system, args.vari, run, rep, temp
                )
                ops_filename = "{}.ops".format(filebase)
                ops = read_ops_from_file(ops_filename, tags, skip)
                times_filename = "{}.times".format(filebase)
                new_times = np.loadtxt(times_filename, skiprows=1)[::skip, 1]
                if run != 0:
                    new_times += times[-1]

                times.extend(new_times.tolist())

                for tag in tags:
                    timeseries[tag].extend(ops[tag])

            # Plot timeseries
            for i, tag in enumerate(tags):
                ax.plot(
                    times,
                    timeseries[tag],
                    marker=None,
                    label=labels[i],
                    color="C{}".format(i),
                    zorder=4 - i,
                )

            # Plot expected value
            for i, tag in enumerate(tags):
                if args.assembled_values[i] != 0:
                    ax.axhline(
                        args.assembled_values[i], linestyle="--", color="C{}".format(i)
                    )

    # Plot legend
    ax = axes[0]
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(
        handles, labels, frameon=False, loc="center", bbox_to_anchor=(0.7, 0.25)
    )

    plt.tight_layout(pad=0.5, h_pad=0, w_pad=0)
    f.savefig("{}.pdf".format(out_filebase), transparent=True)
    f.savefig("{}.png".format(out_filebase), transparent=True)


def read_ops_from_file(filename, tags, skip):
    """Read specified order parameters from file

    Returns a dictionary of tags to values.
    """
    with open(filename) as inp:
        header = inp.readline().split(", ")

    all_ops = np.loadtxt(filename, skiprows=1, dtype=int)[::skip]
    ops = {}
    for i, tag in enumerate(header):
        if tag in tags:
            ops[tag] = all_ops[:, i + 1]

    return ops


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input_dir", type=str, help="Directory of inputs")
    parser.add_argument("output_dir", type=str, help="Output directory")
    parser.add_argument("system", type=str, help="System")
    parser.add_argument("vari", type=str, help="Simulation variant")
    parser.add_argument("runs", type=int, help="Number of runs")
    parser.add_argument("reps", type=int, help="Number of reps")
    parser.add_argument("--temps", nargs="+", type=str, help="Temperatures")
    parser.add_argument(
        "--assembled_values",
        nargs="+",
        type=int,
        help="Bound staples bound domains misbound domains " "fully stacked pairs",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
