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

class LoadAverageHops(ssplot.CommandLine):
  """
  This class is a command line interface to generate a load vs. average hops
  plot.
  """

  NAME = 'load-average-hops'
  ALIASES = ['loadavehops', 'lah']
  _SKIP = ('xlabel', 'ylabel', 'data_labels')

  @staticmethod
  def create_parser(subparser):
    sp = subparser.add_parser(LoadAverageHops.NAME,
                              aliases=LoadAverageHops.ALIASES,
                              help=('Generate a load vs. average hops plot'))
    sp.set_defaults(func=LoadAverageHops.run_command)

    sp.add_argument('plotfile', type=str,
                    help='output plot file')
    sp.add_argument('start', type=float,
                    help='starting load value')
    sp.add_argument('stop', type=float,
                    help='stopping load value (exclusive)')
    sp.add_argument('step', type=float,
                    help='load step size')
    sp.add_argument('stats', metavar='F', type=str, nargs='+',
                    help='stats file to parse')

    sp.add_argument('--load_units', type=str, default='%',
                    help='load units')
    sp.add_argument('--non_minimal', type=ssplot.str_to_bool, default='y',
                    help='whether or not to plot non-minimal hops')

    ssplot.MultilinePlot.add_args(sp, *LoadAverageHops._SKIP)

  @staticmethod
  def run_command(args, plt):
    # read in all stats
    stats = []
    for stat in args.stats:
      gs = handycsv.GridStats.read(stat)
      stats.append(gs)

    # create LoadHops stats object
    lhstats = ssplot.LoadHopsStats(
      args.start, args.stop, args.step, stats)

    # determine the fields and data labels to plot
    fields = ['AveMinHops', 'AveHops', 'AveNonMinHops']
    labels = ['Minimal Hops', 'Total Hops', 'Non-Minimal Hops']
    if not args.non_minimal:
      fields = fields[:-1]
      labels = labels[:-1]

    # gather data
    xdata = lhstats.data['Load']
    ydatas = []
    for field in fields:
      ydatas.append(lhstats.data[field])

    # create x and y axis labels
    xlabel = 'Load ({0})'.format(args.load_units)
    ylabel = 'Average Hops'

    # plot
    mlp = ssplot.MultilinePlot(plt, xdata, ydatas)
    mlp.set_xlabel(xlabel)
    mlp.set_ylabel(ylabel)
    mlp.set_data_labels(labels)
    mlp.apply_args(args, *LoadAverageHops._SKIP)
    mlp.plot(args.plotfile)

    return 0


ssplot.CommandLine.register(LoadAverageHops)
