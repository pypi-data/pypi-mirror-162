"""Styles for creating plots with matplotlib."""

import matplotlib as mpl
from matplotlib import pyplot as plt

SHARE_PGF_PREAMBLE = "\n".join(
    [
        r"\usepackage[RGB]{xcolor}",
        r"\usepackage{nicefrac}",
        r"\usepackage{siunitx}",
        r"\DeclareSIUnit{\molar}{M}",
        r"\DeclareSIUnit{\kb}{\ensuremath{\mathit{k_\textsf{B}}}}",
        r"\DeclareSIUnit{\kbT}{\ensuremath{\mathit{k_\textsf{B} T}}}",
    ]
)

SERIF_FONT_PGF_PREAMBLE = "\n".join(
    [
        r"\usepackage{fontspec}",
        r"\usepackage{unicode-math}",
        r"\setmainfont{STIX Two Text}",
        r"\setmathfont{STIX Two Math}",
    ]
)

FIRASANS_FONT_PGF_PREAMBLE = "\n".join(
    [
        r"\usepackage{fontspec}",
        r"\usepackage{unicode-math}",
        r"\setmainfont{Fira Sans}",
        r"\setmathfont{Fira Math}",
        r"\setsansfont{Fira Sans}",
    ]
)

DEJAVUSANS_FONT_PGF_PREAMBLE = "\n".join(
    [
        r"\usepackage[no-math]{fontspec}",
        r"\setmainfont{DejaVu Sans}",
        r"\setsansfont{DejaVu Sans}",
        r"\usepackage[italic]{mathastext}",
    ]
)

AREVSANS_FONT_PGF_PREAMBLE = "\n".join(
    [
        r"\usepackage{fontspec}",
        r"\usepackage{unicode-math}",
        r"\setmainfont{Arev Sans}",
        r"\setmathfont{Arev Sans}",
        r"\setsansfont{Arev Sans}",
    ]
)

HEROS_FONT_PGF_PREAMBLE = "\n".join(
    [
        r"\usepackage[no-math]{fontspec}",
        r"\setmainfont{TeX Gyre Heros}",
        r"\setsansfont{TeX Gyre Heros}",
        r"\usepackage[italic]{mathastext}",
    ]
)

TEXTBLACK = "0.125"


def set_default_style():

    # Lines
    plt.rcParams["lines.linewidth"] = 1.0
    plt.rcParams["lines.markeredgewidth"] = 1.0
    plt.rcParams["lines.markersize"] = 5

    # Fonts and symbols
    plt.rcParams["text.usetex"] = False
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["STIX Two Text"]
    plt.rcParams["font.weight"] = "normal"
    plt.rcParams["mathtext.fontset"] = "stix"
    plt.rcParams["mathtext.rm"] = "serif"
    plt.rcParams["mathtext.it"] = "serif:italic"
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.titlesize"] = 8
    plt.rcParams["axes.labelsize"] = 8
    plt.rcParams["xtick.labelsize"] = 8
    plt.rcParams["ytick.labelsize"] = 8
    plt.rcParams["legend.fontsize"] = 8

    # Axes
    plt.rcParams["axes.edgecolor"] = "black"
    plt.rcParams["axes.labelcolor"] = "black"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.titlepad"] = 6.0
    plt.rcParams["axes.labelpad"] = 4.0

    # Ticks
    plt.rcParams["xtick.color"] = "black"
    plt.rcParams["xtick.major.size"] = 3.5
    plt.rcParams["xtick.major.width"] = 0.8
    plt.rcParams["xtick.major.pad"] = 3.5
    plt.rcParams["ytick.color"] = "black"
    plt.rcParams["ytick.major.size"] = 3.5
    plt.rcParams["ytick.major.width"] = 0.8
    plt.rcParams["ytick.major.pad"] = 3.5

    # Errorbar plots
    plt.rcParams["errorbar.capsize"] = 2

    # Legend
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 0.0

    # Figure
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.w_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.hspace"] = 0.02
    plt.rcParams["figure.constrained_layout.wspace"] = 0.02


def set_thin_style():

    # Lines
    plt.rcParams["lines.linewidth"] = 0.5
    plt.rcParams["lines.markeredgewidth"] = 0.7
    plt.rcParams["lines.markersize"] = 2.5

    # Fonts and symbols
    plt.rcParams["text.usetex"] = False
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["STIX Two Text"]
    plt.rcParams["font.weight"] = "normal"
    plt.rcParams["mathtext.fontset"] = "stix"
    plt.rcParams["mathtext.rm"] = "serif"
    plt.rcParams["mathtext.it"] = "serif:italic"
    plt.rcParams["text.color"] = TEXTBLACK
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.titlesize"] = 8
    plt.rcParams["axes.labelsize"] = 7
    plt.rcParams["xtick.labelsize"] = 7
    plt.rcParams["ytick.labelsize"] = 7
    plt.rcParams["legend.fontsize"] = 7

    # Axes
    plt.rcParams["axes.edgecolor"] = TEXTBLACK
    plt.rcParams["axes.labelcolor"] = TEXTBLACK
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.titlepad"] = 6.0
    plt.rcParams["axes.labelpad"] = 3.0

    # Ticks
    plt.rcParams["xtick.color"] = TEXTBLACK
    plt.rcParams["xtick.major.size"] = 3.0
    plt.rcParams["xtick.major.width"] = 0.5
    plt.rcParams["xtick.major.pad"] = 3.0
    plt.rcParams["ytick.color"] = TEXTBLACK
    plt.rcParams["ytick.major.size"] = 3.0
    plt.rcParams["ytick.major.width"] = 0.5
    plt.rcParams["ytick.major.pad"] = 3.0

    # Errorbar plots
    plt.rcParams["errorbar.capsize"] = 1.0

    # Legend
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 0.0

    # Figure
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.w_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.hspace"] = 0.02
    plt.rcParams["figure.constrained_layout.wspace"] = 0.02


def set_thin_sans_style():

    # Lines
    plt.rcParams["lines.linewidth"] = 0.5
    plt.rcParams["lines.markeredgewidth"] = 0.7
    plt.rcParams["lines.markersize"] = 2.5

    # Fonts and symbols
    plt.rcParams["text.usetex"] = False
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["TeX Gyre Heros"]
    plt.rcParams["font.weight"] = "normal"
    #    plt.rcParams["mathtext.fontset"] = "stix"
    #    plt.rcParams["mathtext.rm"] = "serif"
    #    plt.rcParams["mathtext.sf"] = "serif"
    #    plt.rcParams["mathtext.it"] = "serif:italic"
    plt.rcParams["text.color"] = TEXTBLACK
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.titlesize"] = 8
    plt.rcParams["axes.labelsize"] = 7
    plt.rcParams["xtick.labelsize"] = 7
    plt.rcParams["ytick.labelsize"] = 7
    plt.rcParams["legend.fontsize"] = 7
    plt.rcParams["text.usetex"] = False

    # Axes
    plt.rcParams["axes.edgecolor"] = TEXTBLACK
    plt.rcParams["axes.labelcolor"] = TEXTBLACK
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.titlepad"] = 6.0
    plt.rcParams["axes.labelpad"] = 3.0

    # Ticks
    plt.rcParams["xtick.color"] = TEXTBLACK
    plt.rcParams["xtick.major.size"] = 3.0
    plt.rcParams["xtick.major.width"] = 0.5
    plt.rcParams["xtick.major.pad"] = 3.0
    plt.rcParams["ytick.color"] = TEXTBLACK
    plt.rcParams["ytick.major.size"] = 3.0
    plt.rcParams["ytick.major.width"] = 0.5
    plt.rcParams["ytick.major.pad"] = 3.0

    # Errorbar plots
    plt.rcParams["errorbar.capsize"] = 1.0

    # Legend
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 0.0

    # Figure
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.w_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.hspace"] = 0.02
    plt.rcParams["figure.constrained_layout.wspace"] = 0.02


def set_default_latex_style():

    # Backend
    mpl.use("pgf")
    plt.rcParams["pgf.texsystem"] = "xelatex"
    plt.rcParams["pgf.rcfonts"] = False
    plt.rcParams["pgf.preamble"] = "\n".join(
        [SHARE_PGF_PREAMBLE, SERIF_FONT_PGF_PREAMBLE]
    )

    # Lines
    plt.rcParams["lines.linewidth"] = 1.0
    plt.rcParams["lines.markeredgewidth"] = 1.0
    plt.rcParams["lines.markersize"] = 2.5

    # Fonts and all text
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.color"] = "black"
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.titlesize"] = 8
    plt.rcParams["axes.labelsize"] = 8
    plt.rcParams["xtick.labelsize"] = 8
    plt.rcParams["ytick.labelsize"] = 8
    plt.rcParams["legend.fontsize"] = 8

    # Axes
    plt.rcParams["axes.edgecolor"] = "black"
    plt.rcParams["axes.labelcolor"] = "black"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.titlepad"] = 6.0
    plt.rcParams["axes.labelpad"] = 4.0

    # Ticks
    plt.rcParams["xtick.color"] = "black"
    plt.rcParams["xtick.major.size"] = 3.5
    plt.rcParams["xtick.major.width"] = 0.8
    plt.rcParams["xtick.major.pad"] = 3.5
    plt.rcParams["ytick.color"] = "black"
    plt.rcParams["ytick.major.size"] = 3.5
    plt.rcParams["ytick.major.width"] = 0.8
    plt.rcParams["ytick.major.pad"] = 3.5

    # Errorbar plots
    plt.rcParams["errorbar.capsize"] = 2

    # Legend
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 0.0

    # Figure
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.w_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.hspace"] = 0.02
    plt.rcParams["figure.constrained_layout.wspace"] = 0.02


def set_thin_latex_style():

    # Backend
    mpl.use("pgf")
    plt.rcParams["pgf.texsystem"] = "xelatex"
    plt.rcParams["pgf.rcfonts"] = False
    plt.rcParams["pgf.preamble"] = "\n".join(
        [SHARE_PGF_PREAMBLE, SERIF_FONT_PGF_PREAMBLE]
    )

    plt.rcParams["lines.linewidth"] = 0.5
    plt.rcParams["lines.markeredgewidth"] = 0.7
    plt.rcParams["lines.markersize"] = 2.5

    # Fonts and all text
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.color"] = TEXTBLACK
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.titlesize"] = 8
    plt.rcParams["axes.labelsize"] = 7
    plt.rcParams["xtick.labelsize"] = 7
    plt.rcParams["ytick.labelsize"] = 7
    plt.rcParams["legend.fontsize"] = 7

    # Axes
    plt.rcParams["axes.edgecolor"] = TEXTBLACK
    plt.rcParams["axes.labelcolor"] = TEXTBLACK
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.titlepad"] = 6.0
    plt.rcParams["axes.labelpad"] = 3.0

    # Ticks
    plt.rcParams["xtick.color"] = TEXTBLACK
    plt.rcParams["xtick.major.size"] = 3.0
    plt.rcParams["xtick.major.width"] = 0.5
    plt.rcParams["xtick.major.pad"] = 3.0
    plt.rcParams["ytick.color"] = TEXTBLACK
    plt.rcParams["ytick.major.size"] = 3.0
    plt.rcParams["ytick.major.width"] = 0.5
    plt.rcParams["ytick.major.pad"] = 3.0

    # Errorbar plots
    plt.rcParams["errorbar.capsize"] = 1.0

    # Legend
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 0.0

    # Figure
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.w_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.hspace"] = 0.02
    plt.rcParams["figure.constrained_layout.wspace"] = 0.02


def set_thin_sans_latex_style():

    # Backend
    mpl.use("pgf")
    plt.rcParams["pgf.texsystem"] = "xelatex"
    plt.rcParams["pgf.rcfonts"] = False
    plt.rcParams["pgf.preamble"] = "\n".join(
        [SHARE_PGF_PREAMBLE, HEROS_FONT_PGF_PREAMBLE]
    )

    plt.rcParams["lines.linewidth"] = 0.5
    plt.rcParams["lines.markeredgewidth"] = 0.7
    plt.rcParams["lines.markersize"] = 2.5

    # Fonts and symbols
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["text.color"] = TEXTBLACK
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.titlesize"] = 8
    plt.rcParams["axes.labelsize"] = 7
    plt.rcParams["xtick.labelsize"] = 7
    plt.rcParams["ytick.labelsize"] = 7
    plt.rcParams["legend.fontsize"] = 7

    # Axes
    plt.rcParams["axes.edgecolor"] = TEXTBLACK
    plt.rcParams["axes.labelcolor"] = TEXTBLACK
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.titlepad"] = 6.0
    plt.rcParams["axes.labelpad"] = 3.0

    # Ticks
    plt.rcParams["xtick.color"] = TEXTBLACK
    plt.rcParams["xtick.major.size"] = 3.0
    plt.rcParams["xtick.major.width"] = 0.5
    plt.rcParams["xtick.major.pad"] = 3.0
    plt.rcParams["ytick.color"] = TEXTBLACK
    plt.rcParams["ytick.major.size"] = 3.0
    plt.rcParams["ytick.major.width"] = 0.5
    plt.rcParams["ytick.major.pad"] = 3.0

    # Errorbar plots
    plt.rcParams["errorbar.capsize"] = 1.0

    # Legend
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["legend.framealpha"] = 0.0

    # Figure
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.w_pad"] = 0.04167
    plt.rcParams["figure.constrained_layout.hspace"] = 0.02
    plt.rcParams["figure.constrained_layout.wspace"] = 0.02
