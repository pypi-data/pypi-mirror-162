"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

import math
import numpy

import ssplot

class LatencyPlot(object):
  """
  This class generates latency plots and is explicitly designed to work with the
  'SampleStats' class.
  """

  __PLOT_TYPES = ['time-latency-scatter', 'latency-pdf', 'latency-cdf',
                  'latency-percentile']

  @staticmethod
  def add_args(plot_type, parser):
    """
    This adds arguments to the specified command line parser.
    """
    assert plot_type in LatencyPlot.__PLOT_TYPES, 'invalid plot type'

    parser.add_argument('--title', type=str,
                        default=None,
                        help='the title of the plot')
    parser.add_argument('--latency_units', type=str,
                        default=None,
                        help='the units of latency samples')
    parser.add_argument('--figure_size',
                        type=ssplot.FigureSize.parse,
                        default=ssplot.FigureSize.default(),
                        help='the size of the figure (e.g., \'12x6\')')
    parser.add_argument('--xgrid', type=ssplot.str_to_bool,
                        default='y',
                        help='whether or not to enable the x-axis grid')
    parser.add_argument('--ygrid', type=ssplot.str_to_bool,
                        default='y',
                        help='whether or not to enable the y-axis grid')
    parser.add_argument('--grid_style', type=str,
                        default=ssplot.GridStyle.default(),
                        help='the style of the grid')
    parser.add_argument('--gray', type=ssplot.str_to_bool,
                        default='n',
                        help='whether or not to use grayscale colors')

    if plot_type == 'time-latency-scatter':
      parser.add_argument('--xmin', type=float,
                          default=None,
                          help='plot X-axis minimum')
      parser.add_argument('--xmax', type=float,
                          default=None,
                          help='plot X-axis maximum')
      parser.add_argument('--ymin', type=float,
                          default=None,
                          help='plot Y-axis minimum')
      parser.add_argument('--ymax', type=float,
                          default=None,
                          help='plot Y-axis maximum')
      parser.add_argument('--show_percentiles', type=ssplot.str_to_bool,
                          default='yes',
                          help='show percentile lines')
      parser.add_argument('--show_legend', type=ssplot.str_to_bool,
                          default='yes',
                          help='show legend of percentile lines')
      parser.add_argument('--legend_location', type=str,
                          default='upper right',
                          help='location of legend (see Matplotlib docs)')
      parser.add_argument('--legend_columns', type=int,
                          default=1,
                          help='number of legend columns')
    elif plot_type == 'latency-pdf':
      parser.add_argument('--xmin', type=float,
                          default=None,
                          help='plot X-axis minimum')
      parser.add_argument('--xmax', type=float,
                          default=None,
                          help='plot X-axis maximum')
      parser.add_argument('--ymin', type=float,
                          default=None,
                          help='plot Y-axis minimum')
      parser.add_argument('--ymax', type=float,
                          default=None,
                          help='plot Y-axis maximum')
      parser.add_argument('--show_percentiles', type=ssplot.str_to_bool,
                          default='yes',
                          help='show percentile lines')
      parser.add_argument('--show_legend', type=ssplot.str_to_bool,
                          default='yes',
                          help='show legend of percentile lines')
      parser.add_argument('--legend_location', type=str,
                          default='upper right',
                          help='location of legend (see Matplotlib docs)')
      parser.add_argument('--legend_columns', type=int,
                          default=1,
                          help='number of legend columns')
    elif plot_type == 'latency-cdf':
      parser.add_argument('--xmin', type=float,
                          default=None,
                          help='plot X-axis minimum')
      parser.add_argument('--xmax', type=float,
                          default=None,
                          help='plot X-axis maximum')
      parser.add_argument('--ymin', type=float,
                          default=None,
                          help='plot Y-axis minimum')
      parser.add_argument('--ymax', type=float,
                          default=None,
                          help='plot Y-axis maximum')
      parser.add_argument('--show_percentiles', type=ssplot.str_to_bool,
                          default='yes',
                          help='show percentile lines')
      parser.add_argument('--show_legend', type=ssplot.str_to_bool,
                          default='yes',
                          help='show legend of percentile lines')
      parser.add_argument('--legend_location', type=str,
                          default='upper right',
                          help='location of legend (see Matplotlib docs)')
      parser.add_argument('--legend_columns', type=int,
                          default=1,
                          help='number of legend columns')
    elif plot_type == 'latency-percentile':
      parser.add_argument('--xmin', type=float,
                          default=None,
                          help='plot X-axis minimum')
      parser.add_argument('--xmax', type=float,
                          default=None,
                          help='plot X-axis maximum')
      parser.add_argument('--nines', type=int,
                          default=None,
                          help='number of percentile nines to plot')
    else:
      assert False

  def __init__(self, plt, plot_type, stats):
    """
    This constructs a latency plotting object
    """
    self._plt = plt
    assert plot_type in LatencyPlot.__PLOT_TYPES, 'invalid plot type'
    self._plot_type = plot_type
    self._stats = stats


  def plot(self, plotfile, args):
    """
    This generates the specified plot.
    """
    if self._plot_type == 'time-latency-scatter':
      self._plot_time_latency_scatter(plotfile, args)
    elif self._plot_type == 'latency-pdf':
      self._plot_latency_pdf(plotfile, args)
    elif self._plot_type == 'latency-cdf':
      self._plot_latency_cdf(plotfile, args)
    elif self._plot_type == 'latency-percentile':
      self._plot_latency_percentile(plotfile, args)
    elif self._plot_type == 'latency-quad':
      self._plot_latency_quad(plotfile, args)
    else:
      assert False

  def _plot_time_latency_scatter(self, plotfile, args):
    fig = self._plt.figure(figsize=args.figure_size)
    ax1 = fig.add_subplot(1, 1, 1)
    self._gen_time_latency_scatter(ax1, args)
    fig.tight_layout()
    fig.savefig(plotfile)

  def _plot_latency_pdf(self, plotfile, args):
    fig = self._plt.figure(figsize=args.figure_size)
    ax1 = fig.add_subplot(1, 1, 1)
    self._gen_latency_pdf(ax1, args)
    fig.tight_layout()
    fig.savefig(plotfile)

  def _plot_latency_cdf(self, plotfile, args):
    fig = self._plt.figure(figsize=args.figure_size)
    ax1 = fig.add_subplot(1, 1, 1)
    self._gen_latency_cdf(ax1, args)
    fig.tight_layout()
    fig.savefig(plotfile)

  def _plot_latency_percentile(self, plotfile, args):
    fig = self._plt.figure(figsize=args.figure_size)
    ax1 = fig.add_subplot(1, 1, 1)
    self._gen_latency_percentile(ax1, args)
    fig.tight_layout()
    fig.savefig(plotfile)

  def _gen_time_latency_scatter(self, axes, args):
    # format axes
    if args.title:
      axes.set_title(args.title, fontsize=ssplot.PLOT_TITLE_FONTSIZE)
    if args.latency_units:
      axes.set_xlabel('Time ({0})'.format(args.latency_units))
      axes.set_ylabel('Latency ({0})'.format(args.latency_units))
    else:
      axes.set_xlabel('Time')
      axes.set_ylabel('Latency')

    # plot bounds
    if self._stats.size > 0:
      spxmin = self._stats.tmin
      spxmax = self._stats.tmax
      yspan = self._stats.smax - self._stats.smin
      spymin = self._stats.smin
      spymax = self._stats.smax + (yspan * 0.02)
    else:
      spxmin = 0
      spxmax = 1
      spymin = 0
      spymax = 1
    if args.xmin is not None:
      spxmin = args.xmin
    if args.xmax is not None:
      spxmax = args.xmax
    if args.ymin is not None:
      spymin = args.ymin
    if args.ymax is not None:
      spymax = args.ymax
    axes.set_xlim(spxmin, spxmax)
    if spymin == spymax:
      axes.set_ylim(spymin-1, spymax+1)
    else:
      axes.set_ylim(spymin, spymax)

    # grid
    grid_style = ssplot.GridStyle.style(args.grid_style)
    if args.xgrid:
      axes.xaxis.grid(True, **grid_style)
    if args.ygrid:
      axes.yaxis.grid(True, **grid_style)
    axes.set_axisbelow(True)

    # detect non-empty data set
    if self._stats.size > 0:
      # scatter plot
      dotsize = 1 if args.figure_size[1] < 8 else 2
      color = '0.5' if args.gray else 'b'
      axes.scatter(self._stats.times, self._stats.samples, c=color,
                   s=dotsize)

      # percentile lines
      if args.show_percentiles:
        pstats = [self._stats.p50, self._stats.p90, self._stats.p99,
                  self._stats.p999, self._stats.p9999]
        labels = ['50th', '90th', '99th', '99.9th', '99.99th']
        color = 'black' if args.gray else 'red'
        ps = ssplot.PlotLineStyle(color, self._plt, len(pstats))
        lines = []
        for idx, perc in enumerate(pstats):
          lines.append(
            axes.plot(numpy.linspace(spxmin, spxmax, 10),
                      numpy.linspace(perc, perc, 10),
                      color=ps[idx]['color'],
                      linestyle=ps[idx]['line_style'],
                      linewidth=ps[idx]['line_width'],
                      marker=ps[idx]['marker_style'],
                      markersize=ps[idx]['marker_size'] * 1.5)[0])

        # legend
        if args.show_legend:
          unitstr = ' ' + args.latency_units if args.latency_units else ''
          for idx in range(len(labels)):
            labels[idx] += ' ({0:.3f}{1})'.format(pstats[idx], unitstr)
          axes.legend(lines, labels,
                      loc=args.legend_location,
                      ncol=args.legend_columns,
                      title=r'$\bf{{{}}}$'.format('Percentiles'),
                      fancybox=True, facecolor='white', edgecolor='black',
                      framealpha=1.0)

    else:
      ssplot.empty_text(axes, (spxmax - spxmin) / 2, (spymax - spymin) / 2)

  def _gen_latency_pdf(self, axes, args):
    # format axes
    if args.title:
      axes.set_title(args.title, fontsize=ssplot.PLOT_TITLE_FONTSIZE)
    if args.latency_units:
      axes.set_xlabel('Latency ({0})'.format(args.latency_units))
    else:
      axes.set_xlabel('Latency')
    axes.set_ylabel('Probability')

    # plot bounds
    if self._stats.size > 0:
      ppxmin = self._stats.smin
      ppxmax = self._stats.smax
      yspan = max(self._stats.pdfy)
      ppymin = 0 - (yspan * 0.02)
      ppymax = max(self._stats.pdfy) + (yspan * 0.02)
    else:
      ppxmin = 0
      ppxmax = 1
      ppymin = 0
      ppymax = 1
    if args.xmin is not None:
      ppxmin = args.xmin
    if args.xmax is not None:
      ppxmax = args.xmax
    if args.ymin is not None:
      ppymin = max(0, args.ymin)
    if args.ymax is not None:
      ppymax = min(1, args.ymax)
    if ppxmin == ppxmax:
      axes.set_xlim(ppxmin-1, ppxmax+1)
    else:
      axes.set_xlim(ppxmin, ppxmax)
    axes.set_ylim(ppymin, ppymax)

    # grid
    grid_style = ssplot.GridStyle.style(args.grid_style)
    if args.xgrid:
      axes.xaxis.grid(True, **grid_style)
    if args.ygrid:
      axes.yaxis.grid(True, **grid_style)
    axes.set_axisbelow(True)

    # detect non-empty data set
    if self._stats.size > 0:
      # percentile lines
      if args.show_percentiles:
        pstats = [self._stats.p50, self._stats.p90, self._stats.p99,
                  self._stats.p999, self._stats.p9999]
        labels = ['50th', '90th', '99th', '99.9th', '99.99th']
        color = 'gray' if args.gray else 'red'
        ps = ssplot.PlotLineStyle(color, self._plt, len(pstats))
        lines = []
        for idx, perc in enumerate(pstats):
          lines.append(
            axes.plot(numpy.linspace(perc, perc, 5),
                      numpy.linspace(ppymin, ppymax, 5),
                      color=ps[idx]['color'],
                      linestyle=ps[idx]['line_style'],
                      linewidth=ps[idx]['line_width'],
                      marker=ps[idx]['marker_style'],
                      markersize=ps[idx]['marker_size'] * 1.5)[0])

        # legend
        if args.show_legend:
          unitstr = ' ' + args.latency_units if args.latency_units else ''
          for idx in range(len(labels)):
            labels[idx] += ' ({0:.3f}{1})'.format(pstats[idx], unitstr)
          axes.legend(lines, labels,
                      loc=args.legend_location,
                      ncol=args.legend_columns,
                      title=r'$\bf{{{}}}$'.format('Percentiles'),
                      fancybox=True, facecolor='white', edgecolor='black',
                      framealpha=1.0)

      # PDF line
      color = 'k' if args.gray else 'b'
      axes.plot(self._stats.pdfx[:-1], self._stats.pdfy, c=color, linewidth=1.5)
    else:
      ssplot.empty_text(axes, (ppxmax - ppxmin) / 2, (ppymax - ppymin) / 2)

  def _gen_latency_cdf(self, axes, args):
    # format axes
    if args.title:
      axes.set_title(args.title, fontsize=ssplot.PLOT_TITLE_FONTSIZE)
    if args.latency_units:
      axes.set_xlabel('Latency ({0})'.format(args.latency_units))
    else:
      axes.set_xlabel('Latency')
    axes.set_ylabel('Probability')

    # plot bounds
    if self._stats.size > 0:
      xspan = self._stats.smax - self._stats.smin
      cpxmin = self._stats.smin - (xspan * 0.01)
      cpxmax = self._stats.smax
      cpymin = -0.02
      cpymax = 1.02
    else:
      cpxmin = 0
      cpxmax = 1
      cpymin = -0.02
      cpymax = 1.02
    if args.xmin is not None:
      cpxmin = args.xmin
    if args.xmax is not None:
      cpxmax = args.xmax
    if args.ymin is not None:
      cpymin = max(0, args.ymin)
    if args.ymax is not None:
      cpymax = min(1, args.ymax)
    if cpxmin == cpxmax:
      axes.set_xlim(cpxmin-1, cpxmax+1)
    else:
      axes.set_xlim(cpxmin, cpxmax)
    axes.set_ylim(cpymin, cpymax)

    # grid
    grid_style = ssplot.GridStyle.style(args.grid_style)
    if args.xgrid:
      axes.xaxis.grid(True, **grid_style)
    if args.ygrid:
      axes.yaxis.grid(True, **grid_style)
    axes.set_axisbelow(True)

    # detect non-empty data set
    if self._stats.size > 0:
      # percentile lines
      if args.show_percentiles:
        pstats = [self._stats.p50, self._stats.p90, self._stats.p99,
                  self._stats.p999, self._stats.p9999]
        percents = [0.50, 0.90, 0.99, 0.999, 0.9999]
        labels = ['50th', '90th', '99th', '99.9th', '99.99th']
        color = 'gray' if args.gray else 'red'
        ps = ssplot.PlotLineStyle(color, self._plt, len(pstats))
        lines = []
        for idx, percentile in enumerate(pstats):
          # vertical line
          markers = math.ceil((5 * percents[idx]) / (cpymax - cpymin))
          lines.append(
            axes.plot(numpy.linspace(percentile, percentile, markers),
                      numpy.linspace(0, percents[idx], markers),
                      color=ps[idx]['color'],
                      linestyle=ps[idx]['line_style'],
                      linewidth=ps[idx]['line_width'],
                      marker=ps[idx]['marker_style'],
                      markersize=ps[idx]['marker_size'] * 1.5)[0])

        # legend
        if args.show_legend:
          unitstr = ' ' + args.latency_units if args.latency_units else ''
          for idx in range(len(labels)):
            labels[idx] += ' ({0:.3f}{1})'.format(pstats[idx], unitstr)
          axes.legend(lines, labels,
                      loc=args.legend_location,
                      ncol=args.legend_columns,
                      title=r'$\bf{{{}}}$'.format('Percentiles'),
                      fancybox=True, facecolor='white', edgecolor='black',
                      framealpha=1.0)

      # CDF line
      color = 'k' if args.gray else 'b'
      axes.plot(self._stats.cdfx, self._stats.cdfy, c=color, linewidth=1.5)
    else:
      ssplot.empty_text(axes, (cpxmax - cpxmin) / 2, (cpymax - cpymin) / 2)

  def _gen_latency_percentile(self, axes, args):
    # format axes
    if args.title:
      axes.set_title(args.title, fontsize=ssplot.PLOT_TITLE_FONTSIZE)
    if args.latency_units:
      axes.set_xlabel('Latency ({0})'.format(args.latency_units))
    else:
      axes.set_xlabel('Latency')
    axes.set_ylabel('Percentile')
    if self._stats.size == 0:
      nines = 5
    elif args.nines:
      nines = args.nines
    else:
      nines = self._stats.nines()
    axes.set_yscale('percentile', nines=nines)

    # plot bounds
    if self._stats.size > 0:
      xspan = self._stats.smax - self._stats.smin
      lpxmin = self._stats.smin - (xspan * 0.001)
      lpxmax = self._stats.smax + (xspan * 0.001)
    else:
      lpxmin = 0
      lpxmax = 1
    if args.xmin is not None:
      lpxmin = args.xmin
    if args.xmax is not None:
      lpxmax = args.xmax
    axes.set_xlim(lpxmin, lpxmax)
    axes.set_ylim(0, 1.0-10**(-nines))

    # grid
    grid_style = ssplot.GridStyle.style(args.grid_style)
    if args.xgrid:
      axes.xaxis.grid(True, **grid_style)
    if args.ygrid:
      axes.yaxis.grid(True, **grid_style)
    axes.set_axisbelow(True)

    # detect non-empty data set
    if self._stats.size > 0:
      # create the plot
      color = 'k' if args.gray else 'b'
      axes.scatter(self._stats.cdfx, self._stats.cdfy, c=color, s=2)
    else:
      ssplot.empty_text(axes, (lpxmax - lpxmin) / 2, 0.9965)
