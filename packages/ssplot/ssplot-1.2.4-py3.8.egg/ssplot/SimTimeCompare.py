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

import numpy
import handycsv

import ssplot

class SimTimeCompare(ssplot.CommandLine):
  """
  This class is a command line interface to generate a bar graph
  showing comparison of simulated times.
  """

  NAME = 'simtime-compare'
  ALIASES = ['simtimecomp', 'stc']
  _SKIP = ()#('xlabel', 'ylabel')

  DATA_MODES = ['straight', 'set_normalize', 'label_normalize']

  @staticmethod
  def create_parser(subparser):
    sp = subparser.add_parser(SimTimeCompare.NAME,
                              aliases=SimTimeCompare.ALIASES,
                              help='Generate a simulated time bar graph')
    sp.set_defaults(func=SimTimeCompare.run_command)

    sp.add_argument('plotfile', type=str,
                    help='output plot file')
    sp.add_argument('data_set_size', type=int,
                    help='size of each data set')
    sp.add_argument('num_data_sets', type=int,
                    help='number of data sets')
    sp.add_argument('--scalar', type=float, default=1.0,
                    help='scalar for each data point to be multiplied by')
    sp.add_argument('--data_mode', type=str,
                    default=SimTimeCompare.DATA_MODES[0],
                    choices=SimTimeCompare.DATA_MODES,
                    help='set the mode for data manipulation')
    sp.add_argument('--data_set_labels', type=str, action='append',
                    help='labels for the data sets')
    sp.add_argument('stats', metavar='F', type=str, nargs='+',
                    help='simulation info stats to parse')

    ssplot.MultibarPlot.add_args(sp, *SimTimeCompare._SKIP)

  @staticmethod
  def run_command(args, plt):
    # check inputs
    if len(args.stats) != (args.data_set_size * args.num_data_sets):
      print('invalid number of stats, expected {}'.format(
        args.data_set_size * args.num_data_sets))
      return -1
    if (args.data_set_labels is not None and
        len(args.data_set_labels) != args.num_data_sets):
      print('invalid number of data set labels {}, expected {}'.format(
        len(args.data_set_labels), args.num_data_sets))
      return -1

    # read in all stats
    ydatas = [[float('NaN')] * args.num_data_sets
              for x in range(args.data_set_size)]
    for idx, stat in enumerate(args.stats):
      # parse the data
      cstats = handycsv.ColumnStats.read(stat)
      simtime = cstats.get('Total sim units')

      # scale the data
      simtime *= args.scalar

      # place the data
      block = idx // args.num_data_sets
      offset = idx % args.num_data_sets
      ydatas[block][offset] = simtime

    # manipulate the data based on the mode
    if args.data_mode == 'straight':
      # do nothing
      pass
    elif args.data_mode == 'set_normalize':
      # normalize each set to the set's maximum value
      for offset in range(args.num_data_sets):
        max_value = max([ydatas[block][offset]
                         for block in range(args.data_set_size)])
        for block in range(args.data_set_size):
          ydatas[block][offset] = ydatas[block][offset] / max_value * 100.0
    elif args.data_mode == 'label_normalize':
      # normalize each value relative to the set label
      if len(args.data_set_labels) != args.num_data_sets:
        print('data set labels must be given for label normalize mode')
        return -1
      for offset in range(args.num_data_sets):
        try:
          div = float(args.data_set_labels[offset])
        except TypeError as ex:
          print('numeric data set labels must be given for label normalize '
                'mode')
          print(ex)
          return -1
        for block in range(args.data_set_size):
          ydatas[block][offset] = ydatas[block][offset] / div
    else:
      assert False, 'programmer error :('

    # use MultibarPlot
    if args.data_set_labels == None:
      xdata = [''] * args.num_data_sets
    else:
      xdata = args.data_set_labels
    mbp = ssplot.MultibarPlot(plt, xdata, ydatas)
    mbp.apply_args(args, *SimTimeCompare._SKIP)
    mbp.plot(args.plotfile)

    return 0


ssplot.CommandLine.register(SimTimeCompare)
