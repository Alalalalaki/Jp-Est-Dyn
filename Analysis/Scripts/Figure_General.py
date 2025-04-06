"""
General tools used to draw figures in data analysis
"""

import numpy as np
import matplotlib as mpl
from cycler import cycler
import matplotlib.pyplot as plt
import seaborn as sns


input_path = "../../Data/Output/"
output_path = "../Figures/"


def set_style(color_order=None,
              tick_direction="in", ticksize=3, tickwidth=0.7,
              half_spine=False, full_tick=True, full_axis_label=False,
              grid_axis="both", grid_which='major', grid_alpha=0.2, grid_color='b',
              marker_cycle=False
              ):
    # style
    sns.set_style("ticks")  # "white", "whitegrid", "ticks"
    sns.set_context("paper")

    # font
    nice_fonts = {
        # "font.family": "sans-serif",
        "font.family": "serif",
        "font.serif": ["Palatino", "Adobe Garamond Pro"],
        "font.sans-serif": ["Helvetica", "Arial"],  #
        # "text.usetex": True,
        'pdf.fonttype': 42,  # default Type 3, does not support for some fonts
    }
    mpl.rcParams.update(nice_fonts)

    # font size
    nice_fonts = {
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }
    mpl.rcParams.update(nice_fonts)

    # lines
    nice_lines = {
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.2,
        "lines.markersize": 4,
        "grid.linewidth": 0.7
    }
    mpl.rcParams.update(nice_lines)

    # ticks
    plt.rc('xtick', direction=tick_direction)
    plt.rc('xtick.major', size=ticksize, width=tickwidth)
    plt.rc('ytick', direction=tick_direction)
    plt.rc('ytick.major', size=ticksize, width=tickwidth)
    if full_tick:
        plt.rcParams['xtick.top'] = True
        plt.rcParams['ytick.right'] = True
    if full_axis_label:
        plt.rcParams['xtick.labeltop'] = True
        plt.rcParams['ytick.labelright'] = True

    # spine
    if half_spine:
        plt.rc('axes.spines', top=False, right=False)

    # grid
    plt.rcParams['axes.grid'] = True
    plt.rc('axes.grid', axis=grid_axis, which=grid_which)
    plt.rc('grid', color=grid_color, alpha=grid_alpha)

    # color
    color_cycle = cycler('color', get_colors(color_order))
    plt.rcParams['axes.prop_cycle'] = color_cycle  # plt.cycler(color=get_colors(color_order))

    # marker
    if marker_cycle:
        # can use plt.cycler then no need to import cycler
        # plt.cycler(color=get_colors(color_order)), marker=get_markerstyle())
        plt.rcParams['axes.prop_cycle'] = (color_cycle + cycler('marker', get_markerstyle()))

    # layout
    # plt.rcParams['figure.constrained_layout.use'] = True

    # latex
    # nice_latex = {
    # "pgf.texsystem": "pdflatex",
    # }
    # mpl.rcParams.update(nice_latex)


def get_colors(order=None, color=True):
    if color:
        colors = np.array([
            "#eb4d55",  # red
            # '#E24A33',  # red
            "#5f6caf",  # blue
            # '#348ABD',  # blue
            "#32afa9",  # green
            # '#8EBA42',  # green
            '#FBC15E',  # yellow
            # "#ffd369",  # yellow
            '#FFB5B8',  # pink
            # '#988ED5',  # purple
            "#916dd5",  # purple
            '#777777',  # grey
            # "#333333",  # black
        ])
        if order:
            colors = [colors[i] for i in order]
    else:
        colors = "black"
    return colors


def get_greys(n, reverse=True, start=False, ):
    greys = [str(g) for g in np.linspace(0.1, 0.9, n)]
    if reverse:
        greys.reverse()
    if start:
        greys = [str(g) for g in np.linspace(0.1, 0.9, n-1)]
        greys = get_colors()[0] + greys
    return greys


def get_linestyle(dot_line=False, marker=True, same_marker=False, same_marker_type=0):
    if dot_line:
        linestyle = ['-', '--', '-.', ':', ]
    else:
        linestyle = ['-'] * 4
    if marker:
        if same_marker:
            markerstyle = get_markerstyle()[same_marker_type:same_marker_type+1] * 4
        else:
            markerstyle = get_markerstyle()[:len(linestyle)]
        linestyle = [l+m for l, m in zip(linestyle, markerstyle)]
    return linestyle


def get_markerstyle():
    markers = ['o', '^', 's', 'd', 'x', '+', '*']
    return markers


def set_axes(axes, half_spine=False, full_tick=True, xgrid=True, grid_alpha=0.2, grid_color='b'):
    # all can be set in set_style, here only leave the option
    for ax in axes:
        if half_spine:
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
        if full_tick:
            ax.tick_params(top=True, right=True)
        ax.grid(axis='y', color=grid_color, alpha=grid_alpha,)
        if xgrid:
            ax.grid(axis='x', color=grid_color, alpha=grid_alpha,)


def add_super_label_for_multi_axes(fig, ylabel=None, xlabel=None):
    ax = fig.add_subplot(111, frameon=False)
    ax.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
    ax.grid(False)
    ax.set_ylabel(ylabel,)
    ax.set_xlabel(xlabel)


def set_size(fig, fraction=0.7, row=1, h_pad=None, w_pad=None, rect=None):
    """
    fraction: fraction of textwidth
    row: level of height, when 1 perfect for 1x1 figure, for other shapes, need some arts
    """
    width = 469.75502  # wp \the\textwidth in latex
    fig_width_pt = width * fraction
    inches_per_pt = 1 / 72.27
    golden_ratio = (5**.5 - 1) / 2  # 0.618 = 1 / 1.618
    fig_width_in = fig_width_pt * inches_per_pt
    fig_height_in = fig_width_in * golden_ratio * row  # (shape[0]/shape[1])

    fig.set_size_inches(fig_width_in, fig_height_in)
    fig.tight_layout(h_pad=h_pad, w_pad=w_pad, rect=rect)


def save_fig(fig, name):
    # alternatively saving in eps
    # transparent=Ture
    # pad_inches=0
    fig.savefig(output_path+name, format='pdf', bbox_inches='tight')
