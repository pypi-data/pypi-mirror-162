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

import handycsv
import numpy

import ssplot

class LoadRatePercent(ssplot.CommandLine):
  """
  This class is a command line interface to generate a load vs. percent rate
  plot.
  """

  NAME = 'load-rate-percent'
  ALIASES = ['loadrateper', 'lrp']

  _SKIP = ('xlabel', 'ylabel', 'data_labels')

  @staticmethod
  def create_parser(subparser):
    sp = subparser.add_parser(LoadRatePercent.NAME,
                              aliases=LoadRatePercent.ALIASES,
                              help=('Generate a load vs. rate plot'))
    sp.set_defaults(func=LoadRatePercent.run_command)

    sp.add_argument('plotfile', type=str,
                    help='output plot file')
    sp.add_argument('start', type=float,
                    help='starting load value')
    sp.add_argument('stop', type=float,
                    help='stopping load value (exclusive)')
    sp.add_argument('step', type=float,
                    help='load step size')

    sp.add_argument('--rate_stats', metavar='F', type=str, nargs='+',
                    help='rate stats file to parse')
    sp.add_argument('--hops_stats', metavar='F', type=str, nargs='+',
                    help='hops stats file to parse')
    sp.add_argument('--load_units', type=str, default='%',
                    help='load units')

    ssplot.MultilinePlot.add_args(sp, *LoadRatePercent._SKIP)

  @staticmethod
  def run_command(args, plt):
    # read in all rate stats
    rate_stats = []
    for stat in args.rate_stats:
      gs = handycsv.GridStats.read(stat)
      rate_stats.append(gs)

    # create LoadRate stats object
    lrstats = ssplot.LoadRateStats(
      args.start, args.stop, args.step, rate_stats)

    # read in all hops stats
    hops_stats = []
    for stat in args.hops_stats:
      gs = handycsv.GridStats.read(stat)
      hops_stats.append(gs)

    # create LoadHops stats object
    lhstats = ssplot.LoadHopsStats(
      args.start, args.stop, args.step, hops_stats)

    # determine the fields and data labels to plot
    fields = ['Mean', 'Minimal', 'NonMinimal']
    labels = ['Mean', 'Minimal', 'Non-Minimal']

    # gather data
    xdata = lhstats.data['Load']
    mean_rate = lrstats.data['Mean']
    min_percent = lhstats.data['PerMinimal']
    nmin_percent = lhstats.data['PerNonMinimal']
    ydatas = []
    ydatas.append(mean_rate)
    ydatas.append(numpy.multiply(mean_rate, min_percent))
    ydatas.append(numpy.multiply(mean_rate, nmin_percent))

    # create x and y axis labels
    xlabel = 'Injected Rate ({0})'.format(args.load_units)
    ylabel = 'Delivered Rate ({0})'.format(args.load_units)

    # plot
    mlp = ssplot.MultilinePlot(plt, xdata, ydatas)
    mlp.set_xlabel(xlabel)
    mlp.set_ylabel(ylabel)
    mlp.set_data_labels(labels)
    mlp.apply_args(args, *LoadRatePercent._SKIP)
    mlp.plot(args.plotfile)

    return 0


ssplot.CommandLine.register(LoadRatePercent)
