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

class LoadLatencyCompare(ssplot.CommandLine):
  """
  This class is a command line interface to generate a load vs. latency
  comparison plot.
  """

  NAME = 'load-latency-compare'
  ALIASES = ['loadlatcomp', 'llc']
  _SKIP = ('xlabel', 'ylabel')

  @staticmethod
  def create_parser(subparser):
    sp = subparser.add_parser(LoadLatencyCompare.NAME,
                              aliases=LoadLatencyCompare.ALIASES,
                              help=('Generate a load vs. latency comparison '
                                    'plot'))
    sp.set_defaults(func=LoadLatencyCompare.run_command)

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

    sp.add_argument('--field', default='Mean',
                    help='the field to be plotted')
    sp.add_argument('--latency_units', default=None,
                    help='latency units')
    sp.add_argument('--load_units', type=str, default='%',
                    help='load units')
    sp.add_argument('--row', default='Packet',
                    choices=['Packet', 'Message', 'Transaction'],
                    help='chooses whether to analyze packets, messages, or'
                    'transactions')

    ssplot.MultilinePlot.add_args(sp, *LoadLatencyCompare._SKIP)

  @staticmethod
  def run_command(args, plt):
    # check inputs
    assert args.start <= args.stop, 'start must be <= stop'
    assert args.step > 0, 'step must be > 0.0'
    gridsPerSet = len(numpy.arange(args.start, args.stop, args.step))
    if len(args.stats) % gridsPerSet != 0:
      print(('The number of stats file for data set is {0},\n'
             'yet you specified {1} stats files. What gives?')
            .format(gridsPerSet, len(args.stats)))
      return -1
    dataSets = len(args.stats) // gridsPerSet

    # read in all stats
    stats = []
    for stat in args.stats:
      gs = handycsv.GridStats.read(stat)
      stats.append(gs)

    # create LoadLatency stats objects
    llstats = []
    for idx in range(dataSets):
      # create the LoadLatencyStats object
      llstat = ssplot.LoadLatencyStats(
        args.start, args.stop, args.step,
        stats[idx * gridsPerSet : (idx + 1) * gridsPerSet],
        row=args.row)

      # save the object
      llstats.append(llstat)

    # make sure the loads are all the same, gather data
    xdata = llstats[0].data['Load']
    ydatas = []
    assert args.field in ssplot.LoadLatencyStats.FIELDS
    for stat in llstats:
      assert len(xdata) == len(set(xdata).intersection(stat.data['Load'])), \
        '{0} != {1}'.format(mload, stat.data['Load'])
      ydatas.append(stat.data[args.field])

    # create x and y labels
    xlabel = 'Load ({0})'.format(args.load_units)
    ylabel = '{0} Latency'.format(args.field)
    if args.latency_units:
      ylabel += ' ({0})'.format(args.latency_units)

    # plot
    mlp = ssplot.MultilinePlot(plt, xdata, ydatas)
    mlp.set_xlabel(xlabel)
    mlp.set_ylabel(ylabel)
    mlp.apply_args(args, *LoadLatencyCompare._SKIP)
    mlp.plot(args.plotfile)

    return 0


ssplot.CommandLine.register(LoadLatencyCompare)
