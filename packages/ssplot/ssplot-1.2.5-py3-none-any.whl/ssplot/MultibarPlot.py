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
import matplotlib.ticker
import math
import numpy
import ssplot

class MultibarPlot(object):
  """
  This class create plots with multiple bar from similar data.
  """

  _kwargs = {}

  def __init__(self, plt, xdata, ydatas):
    """
    This constructs default plot information
    """

    self._num_sets = len(xdata)
    assert self._num_sets > 0, 'must have at least one bar set'
    self._num_bars = len(ydatas)
    assert self._num_bars > 0, 'each bar set must have at least one bar'
    for ydata in ydatas[1:]:
      assert len(ydata) == self._num_sets, 'improper ydata length of {}'.format(
        len(ydata))

    self._plt = plt
    self._xdata = xdata
    self._ydatas = ydatas

    self._plot_style = ssplot.PlotBarStyle.default()
    self._figure_size = ssplot.FigureSize.parse(ssplot.FigureSize.default())
    self._title = None
    self._xlabel = None
    self._ylabel = None
    self._data_labels = None
    self._label_bars = True
    self._bar_label_precision = 2
    self._ymin = None
    self._ymax = None
    self._yauto_frame = 0.0
    self._ygrid = True
    self._grid_style = ssplot.GridStyle.default()
    self._ymajor_ticks = None
    self._yminor_ticks = None
    self._legend_location = 'upper left'
    self._legend_columns = 1
    self._legend_title = None
    self._yscale = None
    self._yticklabels_verbose = False

  def set_plot_style(self, value):
    assert value in ssplot.PlotBarStyle.styles(), \
      'plot bar style "{}" not found'.format(value)
    self._plot_style = value

  def set_figure_size(self, value):
    self._figure_size = ssplot.FigureSize.parse(value)

  def set_title(self, value):
    self._title = value

  def set_xlabel(self, value):
    self._xlabel = value

  def set_ylabel(self, value):
    self._ylabel = value

  def set_data_labels(self, value):
    assert len(value) == self._num_bars
    self._data_labels = value

  def set_label_bars(self, value):
    self._label_bars = bool(value)

  def set_bar_label_precision(self, value):
    assert value >= 0, 'bar label precision must be >= 0'
    self._bar_label_precision = value

  def set_ymin(self, value):
    self._ymin = value

  def set_ymax(self, value):
    self._ymax = value

  def set_yauto_frame(self, value):
    self._yauto_frame = value

  def set_ygrid(self, value):
    self._ygrid = bool(value)

  def set_grid_style(self, value):
    assert value in ssplot.GridStyle.styles()
    self._grid_style = value

  def set_ymajor_ticks(self, value):
    if value == None:
      self._ymajor_ticks = None
    else:
      assert value > 0
      self._ymajor_ticks = value

  def set_yminor_ticks(self, value):
    if value == None:
      self._yminor_ticks = None
    else:
      assert value > 0
      self._yminor_ticks = value

  def set_legend_location(self, value):
    self._legend_location = value

  def set_legend_columns(self, value):
    assert isinstance(value, int) and value > 0
    self._legend_columns = value

  def set_legend_title(self, value):
    self._legend_title = value

  def set_yscale(self, value):
    self._yscale = value

  def set_yticklabels_verbose(self, value):
    self._yticklabels_verbose = bool(value)

  def set(self, **kwargs):
    for k in kwargs:
      value = kwargs[k]
      func = MultibarPlot._kwargs[k]
      func(self, value)

  @staticmethod
  def add_args(parser, *skip):
    for s in skip:
      assert s in MultibarPlot._kwargs.keys(), 'bad skip: {}'.format(s)
    if 'plot_style' not in skip:
      parser.add_argument('--plot_style', type=str,
                          choices=ssplot.PlotBarStyle.styles(),
                          help='the style of the plot bars')
    if 'figure_size' not in skip:
      parser.add_argument('--figure_size',
                          type=ssplot.FigureSize.parse,
                          help='the size of the figure (e.g., \'12x6\')')
    if 'title' not in skip:
      parser.add_argument('--title', type=str,
                          help='the title of the plot')
    if 'xlabel' not in skip:
      parser.add_argument('--xlabel', type=str,
                          help='the label of the x-axis')
    if 'ylabel' not in skip:
      parser.add_argument('--ylabel', type=str,
                          help='the label of the y-axis')
    if 'data_labels' not in skip:
      parser.add_argument('--data_labels', type=str, action='append',
                          help='the label of the data (give all or no labels)')
    if 'label_bars' not in skip:
      parser.add_argument('--label_bars', type=ssplot.str_to_bool,
                          help='whether or not to label bars')
    if 'bar_label_precision' not in skip:
      parser.add_argument('--bar_label_precision', type=int,
                          help='set bar label precision')
    if 'ymin' not in skip:
      parser.add_argument('--ymin', type=float, default=None,
                          help='the minimum value of the y-axis')
    if 'ymax' not in skip:
      parser.add_argument('--ymax', type=float, default=None,
                          help='the maximum value of the y-axis')
    if 'yauto_frame' not in skip:
      parser.add_argument('--yauto_frame', type=float,
                          help='percent of area to frame the y-axis')
    if 'ygrid' not in skip:
      parser.add_argument('--ygrid', type=ssplot.str_to_bool,
                          help='whether or not to enable the y-axis grid')
    if 'grid_style' not in skip:
      parser.add_argument('--grid_style', type=str,
                          choices=ssplot.GridStyle.styles(),
                          help='the style of the grid')
    if 'ymajor_ticks' not in skip:
      parser.add_argument('--ymajor_ticks', type=int,
                          help='number of y-axis major ticks')
    if 'yminor_ticks' not in skip:
      parser.add_argument('--yminor_ticks', type=int,
                          help='number of y-axis minor ticks')
    if 'legend_location' not in skip:
      parser.add_argument('--legend_location', type=str,
                          help='location of legend (see Matplotlib docs)')
    if 'legend_columns' not in skip:
      parser.add_argument('--legend_columns', type=int,
                          help='number of legend columns')
    if 'legend_title' not in skip:
      parser.add_argument('--legend_title', type=str,
                          help='the title of the legend')
    if 'yscale' not in skip:
      parser.add_argument('--yscale', type=str,
                          help='the scale of the y-axis')
    if 'yticklabels_verbose' not in skip:
      parser.add_argument('--yticklabels_verbose', type=ssplot.str_to_bool,
                          help='whether or not to turn y-axis ticklabels '
                          'verbose')

  def apply_args(self, args, *skip):
    for s in skip:
      assert s in MultibarPlot._kwargs.keys()
    if 'plot_style' not in skip and args.plot_style != None:
      self.set_plot_style(args.plot_style)
    if 'figure_size' not in skip and args.figure_size != None:
      self.set_figure_size(args.figure_size)
    if 'title' not in skip and args.title != None:
      self.set_title(args.title)
    if 'xlabel' not in skip and args.xlabel != None:
      self.set_xlabel(args.xlabel)
    if 'ylabel' not in skip and args.ylabel != None:
      self.set_ylabel(args.ylabel)
    if 'data_labels' not in skip and args.data_labels != None:
      self.set_data_labels(args.data_labels)
    if 'label_bars' not in skip and args.label_bars != None:
      self.set_label_bars(args.label_bars)
    if ('bar_label_precision' not in skip and
        args.bar_label_precision != None):
      self.set_bar_label_precision(args.bar_label_precision)
    if 'ymin' not in skip and args.ymin != None:
      self.set_ymin(args.ymin)
    if 'ymax' not in skip and args.ymax != None:
      self.set_ymax(args.ymax)
    if 'yauto_frame' not in skip and args.yauto_frame != None:
      self.set_yauto_frame(args.yauto_frame)
    if 'ygrid' not in skip and args.ygrid != None:
      self.set_ygrid(args.ygrid)
    if 'grid_style' not in skip and args.grid_style != None:
      self.set_grid_style(args.grid_style)
    if 'ymajor_ticks' not in skip and args.ymajor_ticks != None:
      self.set_ymajor_ticks(args.ymajor_ticks)
    if 'yminor_ticks' not in skip and args.yminor_ticks != None:
      self.set_yminor_ticks(args.yminor_ticks)
    if 'legend_location' not in skip and args.legend_location != None:
      self.set_legend_location(args.legend_location)
    if 'legend_columns' not in skip and args.legend_columns != None:
      self.set_legend_columns(args.legend_columns)
    if 'legend_title' not in skip and args.legend_title != None:
      self.set_legend_title(args.legend_title)
    if 'yscale' not in skip and args.yscale != None:
      self.set_yscale(args.yscale)
    if ('yticklabels_verbose' not in skip and
        args.yticklabels_verbose != None):
      self.set_yticklabels_verbose(args.yticklabels_verbose)

  def plot(self, plotfile):
    # create figure
    fig = self._plt.figure(figsize=self._figure_size)
    ax = fig.add_subplot(1, 1, 1)

    # create a PlotBarStyle object
    ps = ssplot.PlotBarStyle(self._plot_style, self._plt, self._num_bars)

    # compute plot bounds
    ymin = self._ymin
    ymax = self._ymax
    if ymin == None:
      ymin = min(map(min, self._ydatas))
    if ymax == None:
      ymax = max(map(max, self._ydatas))

    yspan = ymax - ymin
    ymin -= (yspan * self._yauto_frame)
    ymax += (yspan * self._yauto_frame)
    yspan = ymax - ymin

    # determine base locations
    set_locs = numpy.arange(self._num_sets)
    if self._num_bars == 1 or self._num_sets == 1:
      # butt bars against each other
      span = 1.0
    else:
      # provide a spacing between sets
      span = self._num_bars / (self._num_bars + 1)
    bar_width = span / self._num_bars

    # set bar set ticks and labels
    ax.set_xticks(set_locs)
    ax.set_xticklabels([str(x) for x in self._xdata])

    # plot the bars
    bar_sets = []
    for idx, ydata in enumerate(self._ydatas):
      # retrieve the plot style info
      style = ps[idx]

      # create bars for this set
      bar_sets.append(ax.bar(
        set_locs - ((bar_width * self._num_bars) / 2) + (idx * bar_width),
        ydata,
        bar_width,
        align='edge',
        color=style['color'],
        edgecolor=style['edgecolor'],
        ecolor=style['ecolor'],
        hatch=style['hatch']))

    # set title
    if self._title != None:
      ax.set_title(self._title, fontsize=ssplot.PLOT_TITLE_FONTSIZE)

    # set axis labels
    if self._xlabel != None:
      ax.set_xlabel(self._xlabel)
    if self._ylabel != None:
      ax.set_ylabel(self._ylabel)

    # create legend
    if self._data_labels != None:
      ax.legend((bar_set[0] for bar_set in bar_sets), self._data_labels,
                loc=self._legend_location, ncol=self._legend_columns,
                title=self._legend_title, fancybox=True, facecolor='white',
                edgecolor='black', framealpha=1.0)

    # determine if the bar labels can be int or need to be float
    use_int = True
    for bar_set in bar_sets:
      for bar in bar_set:
        height = bar.get_height()
        if isinstance(height, numpy.int64) or isinstance(height, int):
          continue
        elif isinstance(height, numpy.int64) or isinstance(height, float):
          if not height.is_integer():
            use_int = False
            break
        else:
          assert False, f'New type detected: {type(height)}'

    # add value labels
    if self._label_bars:
      for bar_set in bar_sets:
        for bar in bar_set:
          height = bar.get_height()
          if use_int:
            bar_label = '{}'.format(int(height))
          else:
            fmt = '{{:.{}f}}'.format(self._bar_label_precision)
            bar_label = fmt.format(float(height))
          ax.text(bar.get_x() + bar.get_width() / 2.0, height,
                  bar_label, ha='center', va='bottom')

    # set plot bounds
    ax.set_ylim(ymin, ymax)

    # grid
    grid_kwargs = ssplot.GridStyle.style(self._grid_style)
    if self._ygrid:
      ax.yaxis.grid(True, **grid_kwargs)
    else:
      ax.yaxis.grid(False)
    ax.set_axisbelow(True)

    # set axis scales
    ylog = False
    if self._yscale != None:
      if self._yscale == 'log':
        ylog = True
        ax.set_yscale('log')
      elif self._yscale.startswith('log'):
        ylog = True
        ax.set_yscale('log', base=int(self._yscale[3:]))
      else:
        ax.set_yscale(self._yscale)

    # default ticks
    if self._ymajor_ticks is None and not ylog:
      self._ymajor_ticks = 10
    if self._yminor_ticks is None and not ylog:
      self._yminor_ticks = 20

    # set ticks
    if self._ymajor_ticks != None:
      if ylog:
        raise ValueError('you can\'t set ymajor ticks with a logarithmic '
                         'y-axis')
      ax.yaxis.set_major_locator(
        matplotlib.ticker.MaxNLocator(self._ymajor_ticks))
    if self._yminor_ticks != None:
      if ylog:
        raise ValueError('you can\'t set yminor ticks with a logarithmic '
                         'y-axis')
      ax.yaxis.set_minor_locator(
        matplotlib.ticker.MaxNLocator(self._yminor_ticks))

    # verbose tick labels
    if self._yticklabels_verbose:
      ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
      ax.ticklabel_format(axis='y', style='plain', useOffset=False)

    # generate the plot
    fig.tight_layout()
    fig.savefig(plotfile)
    self._plt.close(fig)


MultibarPlot._kwargs = {
  'plot_style': MultibarPlot.set_plot_style,
  'figure_size': MultibarPlot.set_figure_size,
  'title': MultibarPlot.set_title,
  'xlabel': MultibarPlot.set_xlabel,
  'ylabel': MultibarPlot.set_ylabel,
  'data_labels': MultibarPlot.set_data_labels,
  'label_bars': MultibarPlot.set_label_bars,
  'bar_label_precision': MultibarPlot.set_bar_label_precision,
  'ymin': MultibarPlot.set_ymin,
  'ymax': MultibarPlot.set_ymax,
  'yauto_frame': MultibarPlot.set_yauto_frame,
  'ygrid': MultibarPlot.set_ygrid,
  'grid_style': MultibarPlot.set_grid_style,
  'ymajor_ticks': MultibarPlot.set_ymajor_ticks,
  'yminor_ticks': MultibarPlot.set_yminor_ticks,
  'legend_location': MultibarPlot.set_legend_location,
  'legend_columns': MultibarPlot.set_legend_columns,
  'legend_title': MultibarPlot.set_legend_title,
  'yscale': MultibarPlot.set_yscale,
  'yticklabels_verbose': MultibarPlot.set_yticklabels_verbose
}
