"""Plotting functions and classes.

Each plot type has its own class which inherits from a base class, Plot. See the
docstring of that class for more details.
"""

import sys

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import ticker
from matplotlibstyles import plotutils
import numpy as np
import pandas as pd
from scipy import interpolate

from origamipy import files
from origamipy import mbar_wrapper
from origamipy import nearest_neighbour as nn
from origamipy import utility


def save_figure(f, plot_filebase):
    f.savefig(plot_filebase + ".pgf", transparent=True)
    f.savefig(plot_filebase + ".pdf", transparent=True)
    f.savefig(plot_filebase + ".png", transparent=True)


class Plot:
    """Base class for all plot types.

    The idea is to provide a consistent way to make plots with scripts that
    provide the parameters.

    Attributes:
        args: A dictionary with a standard set of keys. Only a subset of keys may need
            to be defined for a particular method. Possible keys:

            systems: List of systems
            varis: List of varis
            input_dir: Directory containing data to plot
            tag: order parameter tag
            post_lfes: Filename that follows after lfes
            stacking_enes: Stacking energy / kb K

    Methods:
        plot_figure: Make the plot
        setup_axis: Setup the axis, which should be called after plot_figure
        set_labels: Set labels, legend, colourbar
    """

    def __init__(self, args):
        self._args = args
        self._title = None

    def set_labels(self, ax):
        plt.legend()


class LFEsPlot(Plot):
    """LFEs along given order parameter for multiple simulations."""

    def plot_figure(self, f, ax, colorbar=True):
        systems = self._args["systems"]
        varis = self._args["varis"]
        input_dir = self._args["input_dir"]
        tag = self._args["tag"]
        post_lfes = self._args["post_lfes"]
        stacking_enes = self._args["stacking_enes"]

        if stacking_enes is not None:
            stacking_enes = [abs(e) for e in stacking_enes]
            cmap = plotutils.create_truncated_colormap(0.2, 0.8, name="plasma")
            # mappable = plotutils.create_linear_mappable(
            #    cmap, abs(stacking_enes[0]), abs(stacking_enes[-1]))
            # colors = [mappable.to_rgba(abs(e)) for e in stacking_enes]
            increment = stacking_enes[1] - stacking_enes[0]
            cmap, norm, colors = plotutils.create_segmented_colormap(
                cmap, stacking_enes, increment
            )
        else:
            cmap = cm.get_cmap("tab10")
            colors = [cmap(i) for i in range(len(systems))]

        for i in range(len(systems)):
            system = systems[i]
            vari = varis[i]
            post_lfe = post_lfes[i]
            if post_lfe != "":
                post_lfe = "-" + post_lfe

            inp_filebase = f"{input_dir}/{system}-{vari}_lfes{post_lfe}-{tag}"
            lfes = pd.read_csv(f"{inp_filebase}.aves", sep=" ", index_col=0)
            lfe_stds = pd.read_csv(f"{inp_filebase}.stds", sep=" ", index_col=0)
            temp = lfes.columns[0]
            lfes = lfes[temp]
            lfes = lfes - lfes[0]
            lfe_stds = lfe_stds[temp]

            label = f"{system}-{vari}"
            ax.errorbar(
                lfes.index,
                lfes,
                yerr=lfe_stds,
                marker="o",
                label=label,
                color=colors[i],
            )

        if stacking_enes is not None and colorbar == True:
            ax.set_title(" ")
            label = r"Stacking multiplier"
            tick_labels = [
                f"${stacking_enes[0]/1000:.1f}$",
                f"${stacking_enes[1]/1000:.2f}$",
                f"${stacking_enes[2]/1000:.1f}$",
                f"${stacking_enes[3]/1000:.2f}$",
                f"${stacking_enes[4]/1000:.1f}$",
            ]
            plotutils.plot_segmented_colorbar(
                f, ax, cmap, norm, label, tick_labels, "horizontal"
            )

    def setup_axis(
        self,
        ax,
        ylabel=None,
        xlabel=None,
        ylim_bottom=None,
        ylim_top=None,
        xlim_right=None,
        title=None,
        pad=None,
    ):
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_ylim(bottom=ylim_bottom, top=ylim_top)
        ax.set_xlim(right=xlim_right)
        if pad is not None:
            ax.set_title(title, loc="left", pad=pad)


class LFEsOPsPlot(Plot):
    """LFEs along multiple order parameter for a single simulation at melting temp."""

    def plot_figure(self, ax, lfe_i=None):
        input_dir = self._args["input_dir"]
        filebase = self._args["filebase"]
        tags = self._args["tags"]
        labels = self._args["labels"]

        for tag, label in zip(tags, labels):
            inp_filebase = f"{input_dir}/{filebase}_lfes-melting-{tag}"
            lfes = pd.read_csv(f"{inp_filebase}.aves", sep=" ", index_col=0)
            lfe_stds = pd.read_csv(f"{inp_filebase}.stds", sep=" ", index_col=0)
            lfes = lfes.iloc[:, 0]
            if lfe_i is not None:
                lfes = lfes - lfes[lfe_i]

            lfe_stds = lfe_stds.iloc[:, 0]

            ax.errorbar(
                lfes.index,
                lfes,
                yerr=lfe_stds,
                marker="o",
                label=label,
            )

    def setup_axis(
        self,
        ax,
        ylabel=None,
        xlabel=None,
        ylim_bottom=None,
        ylim_top=None,
        xlim_right=None,
        title=None,
    ):
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_ylim(bottom=ylim_bottom, top=ylim_top)
        ax.set_xlim(right=xlim_right)
        ax.set_title(title, loc="left")


class LFEsFullDomainsFullyBoundStaplesPlot(Plot):
    """LFEs for both numfulldomains and numfullyboundstaples."""

    def plot_figure(self, axes):
        system = self._args["system"]
        varis = self._args["varis"]
        input_dir = self._args["input_dir"]
        post_lfes = self._args["post_lfes"]
        tags = ["numfullyboundstaples", "numfulldomains"]
        labels = ["Fully-bound staples", "Bound-domain pairs"]

        cmap = cm.get_cmap("tab10")
        for i, tag in enumerate(tags):
            if tag == "numfulldomains":
                ax = axes[1]

            else:
                ax = axes[0]

            vari = varis[i]
            post_lfe = post_lfes[i]
            if post_lfe != "":
                post_lfe = "-" + post_lfe

            inp_filebase = f"{input_dir}/{system}-{vari}_lfes{post_lfe}-{tag}"
            lfes = pd.read_csv(f"{inp_filebase}.aves", sep=" ", index_col=0)
            lfe_stds = pd.read_csv(f"{inp_filebase}.stds", sep=" ", index_col=0)
            temp = lfes.columns[0]
            lfes = lfes[temp]
            lfes = lfes - lfes[0]
            lfe_stds = lfe_stds[temp]

            ax.errorbar(
                lfes.index,
                lfes,
                yerr=lfe_stds,
                marker="o",
                label=labels[i],
                color=cmap(i),
            )

    def setup_axis(
        self,
        axes,
        ylabel=None,
        xlabel_bottom=None,
        xlabel_top=None,
        ylim_bottom=None,
        ylim_top=None,
        title=None,
    ):
        cmap = cm.get_cmap("tab10")
        ax = axes[0]
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel_bottom, color=cmap(0))
        ax.tick_params(axis="x", colors=cmap(0))
        ax.set_title(title, loc="left")

        ax = axes[1]
        ax.spines.top.set_visible(True)
        ax.spines.bottom.set_visible(False)
        ax.spines.left.set_visible(False)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=7))
        ax.set_ylim(bottom=ylim_bottom, top=ylim_top)
        ax.tick_params(axis="x", colors=cmap(1))
        ax.set_xlabel(xlabel_top, color=cmap(1))


class LFEsRepTempsPlot(Plot):
    """LFEs for numfullyboundstaples and numfulldomains across temperature range."""

    def plot_figure(self, axes, temp_indices=[0, -1], include_mean=True):
        filebase = self._args["filebase"]
        input_dir = self._args["input_dir"]
        post_lfes = self._args["post_lfes"]

        cmap = cm.get_cmap("tab10")
        markers = ["^", "s", "o"]
        tags = ["numfullyboundstaples", "numfulldomains"]
        labels = ["Fully-bound staples", "Bound-domain pairs"]

        for j, tag in enumerate(tags):
            if tag == "numfulldomains":
                ax = axes[1]
            else:
                ax = axes[0]

            post_lfe = post_lfes[j]
            if post_lfe != "":
                post_lfe = "-" + post_lfe

            replica_filebase = f"{input_dir}/{filebase}_lfes{post_lfe}-{tag}"
            replica_aves = pd.read_csv(f"{replica_filebase}.aves", sep=" ", index_col=0)
            replica_stds = pd.read_csv(f"{replica_filebase}.stds", sep=" ", index_col=0)

            temps = np.array(replica_aves.columns, dtype=float)
            # norm = mpl.colors.Normalize(vmin=temps[0], vmax=temps[-1])
            # cmap = mpl.cm.viridis
            # mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
            if type(temp_indices) is int:
                ax.errorbar(
                    replica_aves.index,
                    replica_aves.iloc[:, temp_indices],
                    yerr=replica_stds.iloc[:, temp_indices],
                    marker=markers[2],
                    color=cmap(j),
                    label=labels[j],
                )
                self._title = f"$T = {temps[temp_indices]:.3f}$"
            else:
                for i, k in enumerate(temp_indices):
                    if include_mean:
                        color = plotutils.darken_color(cmap(j)[:-1], 1.3)
                    else:
                        color = cmap(j)

                    ax.errorbar(
                        replica_aves.index,
                        replica_aves.iloc[:, k],
                        yerr=replica_stds.iloc[:, k],
                        marker=markers[i],
                        color=color,
                    )
                    # color=mappable.to_rgba(temps[i]))

            if include_mean:
                melting_filebase = f"{input_dir}/{filebase}_lfes-melting-{tag}"
                melting_aves = pd.read_csv(
                    f"{melting_filebase}.aves", sep=" ", index_col=0
                )
                melting_stds = pd.read_csv(
                    f"{melting_filebase}.stds", sep=" ", index_col=0
                )
                ax.errorbar(
                    melting_aves.index,
                    melting_aves.iloc[:, 0],
                    yerr=melting_stds.iloc[:, 0],
                    marker=markers[2],
                    color=cmap(j),
                    label=labels[j],
                )
                # color=mappable.to_rgba(temps[i]))

        # return mappable

    def setup_axis(
        self,
        axes,
        ylabel=None,
        xlabel_bottom=None,
        xlabel_top=None,
        ylim_bottom=-1,
        ylim_top=None,
        title=None,
    ):
        cmap = cm.get_cmap("tab10")
        ax = axes[0]
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel_bottom, color=cmap(0))
        ax.tick_params(axis="x", colors=cmap(0))
        if self._title is not None:
            ax.set_title(title + self._title, loc="left")
        else:
            ax.set_title(title, loc="left")

        ax = axes[1]
        ax.spines.top.set_visible(True)
        ax.spines.bottom.set_visible(False)
        ax.spines.left.set_visible(False)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=7))
        ax.tick_params(axis="x", colors=cmap(1))
        ax.set_xlabel(xlabel_top, color=cmap(1))

        ax.set_ylim()
        ax.set_ylim([ylim_bottom, ylim_top])


class MeansPlot(Plot):
    """Expectation value of order parameter from multiple simulations."""

    def plot_figure(self, ax, labels=None):
        systems = self._args["systems"]
        varis = self._args["varis"]
        input_dir = self._args["input_dir"]
        tag = self._args["tag"]
        assembled_values = self._args["assembled_values"]
        posts = self._args["posts"]
        nncurves = self._args["nncurves"]
        staple_M = self._args["staple_M"]
        if any(nncurves):
            binds = self._args["binds"]
            bindh = self._args["bindh"]
        else:
            binds = None
            bindh = None

        contins = self._args["continuous"]

        cmap = cm.get_cmap("tab10")

        lines = []

        if labels is None:
            labels = varis

        for i in range(len(systems)):
            system = systems[i]
            vari = varis[i]
            label = labels[i]
            assembled_value = assembled_values[i]
            if posts is not None:
                post = posts[i]
            else:
                post = ""

            if nncurves is not None:
                nncurve = nncurves[i]
            else:
                nncurve = False

            if contins is not None:
                contin = contins[i]
            else:
                contin = False

            if system in ["snodin", "16nt-halftile-3-a-0"]:
                ax.axhline(assembled_value, linestyle="--", color=cmap(i))
            elif system == "halfturn-2-9":
                ax.axhline(assembled_value, linestyle="--", color="0.4")

            inp_filebase = f"{input_dir}/{system}-{vari}{post}"
            all_aves, all_stds = files.read_expectations(inp_filebase)
            temps = all_aves["temp"]
            means = all_aves[tag]
            stds = all_stds[tag]
            if nncurve:
                fracs = nn.calc_excess_bound_fractions(bindh, binds, staple_M, 10)
                interpolated_temp = interpolate.interp1d(means, temps, kind="linear")
                halfway_temp = interpolated_temp(assembled_value / 2)
                occ_temps = np.linspace(halfway_temp - 10, halfway_temp + 10, 50)
                ax.plot(occ_temps, fracs * assembled_value, color="0.4")

            if contin:
                ax.fill_between(temps, means + stds, means - stds, color="0.8")
                lines.append(
                    ax.plot(temps, means, marker="None", label=label, color=cmap(i))[0]
                )

                # Plot the actual simulation temperature as a point
                inp_filebase = f"{input_dir}/{system}-{vari}"
                all_aves, all_stds = files.read_expectations(inp_filebase)
                mean = all_aves[tag]
                std = all_stds[tag]
                temp = all_aves["temp"]
                ax.errorbar(
                    temp, mean, yerr=std, marker="o", label=label, color=cmap(i)
                )
            else:
                lines.append(
                    ax.errorbar(
                        temps, means, yerr=stds, marker="o", label=label, color=cmap(i)
                    )[1][1]
                )

        return lines

    def setup_axis(self, ax, ylabel, title):
        ax.set_title(title)
        ax.set_xlabel(r"$T / K$")
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)

    def set_labels(self, ax):
        ax.set_axis_off()
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc="center", frameon=False, ncol=1)


class MeansStackPlot(Plot):
    """Expectation value of order parameter for multiple stacking energies."""

    def plot_figure(self, f, ax):
        system = self._args["system"]
        varis = self._args["varis"]
        input_dir = self._args["input_dir"]
        tag = self._args["tag"]
        assembled_value = self._args["assembled_value"]
        stacking_enes = self._args["stacking_enes"]

        stacking_enes = [abs(e) for e in stacking_enes]
        cmap = plotutils.create_truncated_colormap(0.2, 0.8, name="plasma")
        # mappable = plotutils.create_linear_mappable(
        #    cmap, abs(stacking_enes[0]), abs(stacking_enes[-1]))
        # colors = [mappable.to_rgba(abs(e)) for e in stacking_enes]
        increment = stacking_enes[1] - stacking_enes[0]
        cmap, norm, colors = plotutils.create_segmented_colormap(
            cmap, stacking_enes, increment
        )

        ax.axhline(assembled_value, linestyle="--", color="0.4")
        for (
            i,
            vari,
        ) in enumerate(varis):

            inp_filebase = f"{input_dir}/{system}-{vari}_temps"
            all_aves, all_stds = files.read_expectations(inp_filebase)
            temps = all_aves["temp"]
            means = all_aves[tag]
            stds = all_stds[tag]

            ax.fill_between(temps, means + stds, means - stds, color="0.8")
            ax.plot(temps, means, marker="None", color=colors[i])

            # Plot the actual simulation temperature as a point
            inp_filebase = f"{input_dir}/{system}-{vari}"
            all_aves, all_stds = files.read_expectations(inp_filebase)
            mean = all_aves[tag]
            std = all_stds[tag]
            temp = all_aves["temp"]
            ax.errorbar(temp, mean, yerr=std, marker="o", color="0.4")

        label = r"Stacking multiplier"
        tick_labels = [
            f"${stacking_enes[0]/1000:.1f}$",
            f"${stacking_enes[1]/1000:.2f}$",
            f"${stacking_enes[2]/1000:.1f}$",
            f"${stacking_enes[3]/1000:.2f}$",
            f"${stacking_enes[4]/1000:.1f}$",
        ]
        plotutils.plot_segmented_colorbar(
            f, ax, cmap, norm, label, tick_labels, "horizontal"
        )

    def setup_axis(self, ax, ylabel, title=None):
        ax.set_title(title, loc="left")
        ax.set_xlabel(r"$T / K$")
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)

    def set_labels(self, ax):
        ax.set_axis_off()
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc="center", frameon=False, ncol=1)


class NumFullyBoundStaplesFreqsPlot(Plot):
    """Plot combination of staple states along slices of numfullyboundstaples."""

    def plot_figure(self, axes):
        input_dir = self._args["input_dir"]
        filebase = self._args["filebase"]
        stapletypes = self._args["stapletypes"]
        slice_tag = self._args["slice_tag"]
        tagbase = self._args["tagbase"]
        mapfile = self._args["mapfile"]

        cmap = cm.get_cmap("viridis")

        tags = [f"{tagbase}{i + 1}" for i in range(stapletypes)]
        inp_filebase = f"{input_dir}/{filebase}-{slice_tag}"
        index_to_stapletype = np.loadtxt(mapfile, dtype=int)
        for i in range(stapletypes - 1):
            op_value = i + 1
            aves, stds = files.read_expectations(inp_filebase)
            if op_value not in aves[slice_tag].values:
                print("Missing value")
                sys.exit()

            ax = axes[i]
            reduced_aves = aves[aves[slice_tag] == op_value]
            freqs = [reduced_aves[t] for t in tags]
            freq_array = utility.fill_assembled_shape_array(freqs, index_to_stapletype)

            # Plot simulation melting points
            ax.imshow(freq_array, vmin=0, vmax=1, cmap=cmap)

    def setup_axes(self, axes, titles=None):
        for i, ax in enumerate(axes):
            ax.axis("off")
            if titles is not None:
                ax.set_title(titles[i], loc="left")

    def set_labels(self, f, axes, fraction=0.15, aspect=20, shrink=1):
        cmap = cm.get_cmap("viridis")
        mappable = plotutils.create_linear_mappable(cmap, 0, 1)
        cbar = f.colorbar(
            mappable,
            ax=axes,
            orientation="horizontal",
            fraction=fraction,
            aspect=aspect,
            shrink=1,
        )
        cbar.set_label("Expected staple state")


class NumFullyBoundStaplesBarriersPlot(Plot):
    """Plot forward and reverse barriers of numfullyboundstaples vs temprature."""

    def plot_figure(self, ax, include_reverse=False):
        input_dir = self._args["input_dir"]
        filebase = self._args["filebase"]

        s_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-temps-numfullyboundstaples.aves",
            sep=" ",
            index_col=0,
        )
        s_stds = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-temps-numfullyboundstaples.stds",
            sep=" ",
            index_col=0,
        )
        s_f_barriers = []
        s_f_stds = []
        s_r_barriers = []
        s_r_stds = []
        for temp in s_lfes.columns:
            s_lfe = np.array(s_lfes[temp])
            s_std = np.array(s_stds[temp])

            s_f_barrier, s_f_std = mbar_wrapper.calc_forward_barrier_error(s_lfe, s_std)
            s_f_barriers.append(s_f_barrier)
            s_f_stds.append(s_f_std)

            s_r_barrier, s_f_std = mbar_wrapper.calc_reverse_barrier_error(s_lfe, s_std)
            s_r_barriers.append(s_r_barrier)
            s_r_stds.append(s_f_std)

        s_f_barriers = np.array(s_f_barriers)
        s_f_stds = np.array(s_f_stds)
        s_r_barriers = np.array(s_r_barriers)
        s_r_stds = np.array(s_r_stds)

        temps = np.array(s_lfes.columns, dtype=float)

        lines = []
        lines.extend(ax.plot(temps, s_f_barriers))
        ax.fill_between(
            temps, s_f_barriers + s_f_stds, s_f_barriers - s_f_stds, color="0.8"
        )
        if include_reverse:
            lines.extend(ax.plot(temps, s_r_barriers))
            ax.fill_between(
                temps, s_r_barriers + s_r_stds, s_r_barriers - s_r_stds, color="0.8"
            )

        melting_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-melting-numfullyboundstaples.aves",
            sep=" ",
            index_col=0,
        )
        melting_temp = float(melting_lfes.columns[0])
        ax.set_xticks([353, melting_temp, 356])
        ax.set_xticklabels(["353", r"$T_\textrm{m}$", "356"])

        return lines

    def setup_axis(
        self, ax, ylabel=None, xlabel=None, ylim_bottom=None, ylim_top=None, title=None
    ):
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_ylim(bottom=ylim_bottom)
        ax.set_ylim(top=ylim_top)
        ax.set_title(title, loc="left")


class NumFullDomainsBarriersPlot(Plot):
    """Plot forward and reverse barriers of numfulldomains vs temprature."""

    def plot_figure(self, ax, include_reverse=False):
        input_dir = self._args["input_dir"]
        filebase = self._args["filebase"]

        d_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-temps-numfulldomains.aves",
            sep=" ",
            index_col=0,
        )
        d_stds = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-temps-numfulldomains.stds",
            sep=" ",
            index_col=0,
        )
        d_f_barriers = []
        d_f_stds = []
        d_r_barriers = []
        d_r_stds = []
        for temp in d_lfes.columns:
            d_lfe = np.array(d_lfes[temp])
            d_std = np.array(d_stds[temp])
            try:
                d_barrier_i = mbar_wrapper.find_barrier(d_lfe)
                d_f_barrier = d_lfe[d_barrier_i] - d_lfe[d_barrier_i - 1]
                d_f_std = np.sqrt(d_std[d_barrier_i] ** 2 + d_std[d_barrier_i - 1] ** 2)
                d_f_barriers.append(d_f_barrier)
                d_f_stds.append(d_f_std)

                d_r_barrier = d_lfe[d_barrier_i] - d_lfe[d_barrier_i + 2]
                d_r_std = np.sqrt(d_std[d_barrier_i] ** 2 + d_std[d_barrier_i + 2] ** 2)
                d_r_barriers.append(d_r_barrier)
                d_r_stds.append(d_r_std)
            except:
                d_f_barriers.append(np.nan)
                d_f_stds.append(np.nan)
                d_r_barriers.append(np.nan)
                d_r_stds.append(np.nan)

        temps = np.array(d_lfes.columns, dtype=float)

        d_f_barriers = np.array(d_f_barriers)
        d_f_stds = np.array(d_f_stds)
        d_r_barriers = np.array(d_r_barriers)
        d_r_stds = np.array(d_r_stds)

        lines = []
        lines.extend(ax.plot(temps, d_f_barriers))
        ax.fill_between(
            temps, d_f_barriers + d_f_stds, d_f_barriers - d_f_stds, color="0.8"
        )
        if include_reverse:
            lines.extend(ax.plot(temps, d_r_barriers))
            ax.fill_between(
                temps, d_r_barriers + d_r_stds, d_r_barriers - d_r_stds, color="0.8"
            )

        melting_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-melting-numfulldomains.aves",
            sep=" ",
            index_col=0,
        )
        melting_temp = float(melting_lfes.columns[0])
        ax.set_xticks([350, melting_temp, 360])
        ax.set_xticklabels(["350", r"$T_\textrm{m}$", "360"])

        return lines

    def setup_axis(
        self, ax, ylabel=None, xlabel=None, ylim_bottom=None, ylim_top=None, title=None
    ):
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_ylim(bottom=ylim_bottom)
        ax.set_ylim(top=ylim_top)
        ax.set_title(title, loc="left")


class NumFullyBoundStaplesBarrierLocationPlot(Plot):
    """Barrier peak location of number of fully bound staples"""

    def plot_figure(self, ax):
        input_dir = self._args["input_dir"]
        filebase = self._args["filebase"]

        s_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-temps-numfullyboundstaples.aves",
            sep=" ",
            index_col=0,
        )
        s_barrier_is = []
        for temp in s_lfes.columns:
            s_lfe = np.array(s_lfes[temp])
            try:
                s_barrier_is.append(mbar_wrapper.find_barrier(s_lfe))
            except:
                s_barrier_is.append(np.nan)

        temps = np.array(s_lfes.columns, dtype=float)
        ax.plot(temps, s_barrier_is, color="0.4")

        melting_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-melting-numfullyboundstaples.aves",
            sep=" ",
            index_col=0,
        )
        melting_temp = float(melting_lfes.columns[0])
        ax.set_xticks([353, melting_temp, 356])
        ax.set_xticklabels(["353", r"$T_\textrm{m}$", "356"])

    def setup_axis(self, ax, xlabel=None, ylim_top=None):
        ax.set_ylabel("Num. staples")
        ax.set_xlabel(xlabel)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5, integer=True))
        ax.set_ylim(bottom=0)
        ax.set_ylim(top=ylim_top)
        # ax.set_yticks([0, ylim_top])
        # ax.set_yticklabels(["0", f"{ylim_top}"])
        ax.axhline(9, linestyle="--", color="0.4")


class NumFullDomainsBarrierLocationPlot(Plot):
    """Barrier peak location of number of bound domains"""

    def plot_figure(self, ax):
        input_dir = self._args["input_dir"]
        filebase = self._args["filebase"]

        d_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-temps-numfulldomains.aves",
            sep=" ",
            index_col=0,
        )
        d_barrier_is = []
        for temp in d_lfes.columns:
            d_lfe = np.array(d_lfes[temp])
            try:
                d_barrier_i = mbar_wrapper.find_barrier(d_lfe)
                d_barrier_is.append(d_barrier_i)
            except:
                d_barrier_is.append(np.nan)

        temps = np.array(d_lfes.columns, dtype=float)
        ax.plot(temps, d_barrier_is, color="0.4")
        ax.axhline(27, linestyle="--", color="0.4")

        melting_lfes = pd.read_csv(
            f"{input_dir}/{filebase}_lfes-melting-numfulldomains.aves",
            sep=" ",
            index_col=0,
        )
        melting_temp = float(melting_lfes.columns[0])
        ax.set_xticks([350, melting_temp, 360])
        ax.set_xticklabels(["350", r"$T_\textrm{m}$", "360"])

    def setup_axis(self, ax, xlabel=None, ylim_top=None):
        ax.set_ylabel("Num. domain pairs")
        ax.set_xlabel(xlabel)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5, integer=True))
        ax.set_ylim(bottom=0)
        ax.set_ylim(top=ylim_top)
        # ax.set_yticks([0, ylim_top])
        # ax.set_yticklabels(["0", f"{ylim_top}"])
