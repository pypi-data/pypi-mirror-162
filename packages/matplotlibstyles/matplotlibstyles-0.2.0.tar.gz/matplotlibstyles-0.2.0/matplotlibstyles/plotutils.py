"""Helper functions for creating plots with matplotlib."""

import colorsys

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
import numpy as np


def set_constrained_layout_pads(h_pad=0.04167, w_pad=0.04167, hspace=0.02, wspace=0.02):
    plt.rcParams["figure.constrained_layout.h_pad"] = h_pad
    plt.rcParams["figure.constrained_layout.w_pad"] = w_pad
    plt.rcParams["figure.constrained_layout.hspace"] = hspace
    plt.rcParams["figure.constrained_layout.wspace"] = wspace


def setup_shared_axis(ax):
    """Setup an axis with no visible markings."""
    ax.spines["top"].set_color("none")
    ax.spines["bottom"].set_color("none")
    ax.spines["left"].set_color("none")
    ax.spines["right"].set_color("none")
    ax.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)

    # The above does not work with pgf backend
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def cm_to_inches(cm):
    return cm / 2.54


def pt_to_inches(pt):
    return pt * 0.01389


def create_truncated_colormap(left, right, name="viridis", N=256):
    """Return a narrowed colormap.

    This is useful when plotting lines with a colour map that has extreme values that
    are too close to white or black.

    Args:
        left: defines lower end of new range; must be >= 0 and < right
        right: defines the upper end of the new range; must be <= 1
    """
    cmap = cm.get_cmap(name, 2 * N)

    return colors.ListedColormap(cmap(np.linspace(left, right, N)))


def create_log_mappable(cmap, vmin, vmax):
    """Create an object that logrithimically converts between a value and a colour.

    Args:
        cmap: Color map
        vmin: Minimum value of quantity
        vmax: Maximum value of quantity
    """
    norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)

    return mappable


def create_linear_mappable(cmap, vmin, vmax):
    """Create an object that linearly converts between a value and a colour.

    Args:
        cmap: Color map
        vmin: Minimum value of quantity
        vmax: Maximum value of quantity
    """
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)

    return mappable


def create_segmented_colormap(cmap, values, increment):
    """Create colormap with discretized colormap.

    This was created mainly to plot a colorbar that has discretized values.

    Args:
        cmap: matplotlib colormap
        values: A list of the quantities being plotted
        increment: The increment used to bin the values

    Returns:
        A tuple with the cmap, the norm, and the colors.
    """
    bmin = values[0] - increment / 2
    bmax = values[-1] + 3 * increment / 2
    boundaries = np.arange(bmin, bmax, increment)
    norm = mpl.colors.BoundaryNorm(boundaries, len(values) + 1)
    norm2 = mpl.colors.Normalize(vmin=0, vmax=len(values))
    norm3 = mpl.colors.BoundaryNorm(
        np.arange(-0.5, len(values) + 0.5, 1), len(values) + 1
    )
    colors = cmap(norm2(norm(values + [values[-1] + increment])))
    cmap = mpl.colors.ListedColormap(colors, "hate")

    return cmap, norm3, colors


def plot_segmented_colorbar(f, ax, cmap, norm, label, ticklabels, orientation):
    """Plot a colorbar with discretized colors.

    Args:
        f: figure object
        ax: axis object
        cmap: colormap
        norm: norm used for colormap
        label: label for bar
        ticklabels: ticklabels
        orientation: vertical or horizontal
    """
    mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = f.colorbar(
        mappable,
        ax=ax,
        orientation=orientation,
        ticks=list(range(0, len(ticklabels) + 1)),
        aspect=40,
    )
    cbar.set_label(label)
    ticklabels += ["0.0"]
    cbar.set_ticklabels(ticklabels)


# def plot_segmented_colorbar(f, mappable, ncolors, vmin, vmax):
#    mappable.set_clim(0, ncolors)
#    colorbar = f.colorbar(mappable)
#    colorbar.set_ticks(np.linspace(0.5, ncolors - 0.5, ncolors))
#    colorbar.set_ticklabels(range(vmin, vmax + 1))
#
#    return colorbar


def darken_color(color, factor):
    """Modify an RGB colour by multiplying its luminance by a given factor."""
    darkcolor = colorsys.rgb_to_hls(*color)
    darkcolor = (darkcolor[0], darkcolor[1] * factor, darkcolor[2])

    return colorsys.hls_to_rgb(*darkcolor)


def set_line_labels_by_pos(line, ax, xpos, ha, va, label, ypos=None, yshift=0, **kwargs):
    """Set label for line by x position.

    It will get the y position for the given x position and plot the label there.

    Args:
        line: line output from plotting
        ax: axis object
        xpos: position on x axis
        ha: horizontal alignment (left, right)
        va: vertial alignemtn (top, bottom)
        label: the label
        ypos: overide y position
        yshift: shift the calculated ypos
    """
    xdata = line.get_xdata()
    if ypos is None:
        ypos = line.get_ydata()[np.abs(xdata - xpos).argmin()]
    ax.text(
        xpos,
        ypos + yshift,
        label,
        color=line.get_color(),
        horizontalalignment=ha,
        verticalalignment=va,
        **kwargs
    )


def set_line_labels_by_index(line, ax, index, ha, va, label, xshift=0, yshift=0, **kwargs):
    """Set label for line by x index.

    It will get the xy position for the given index and plot the label there.

    Args:
        line: line output from plotting
        ax: axis object
        index: index into line data
        ha: horizontal alignment (left, right)
        va: vertial alignemtn (top, bottom)
        label: the label
        xshift: shift the obtained xpos
        yshift: shift the obtained ypos
    """
    xpos = line.get_xdata()[index]
    ypos = line.get_ydata()[index]
    ax.text(
        xpos + xshift,
        ypos + yshift,
        label,
        color=line.get_color(),
        horizontalalignment=ha,
        verticalalignment=va,
        **kwargs
    )
