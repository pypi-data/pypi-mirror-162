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

class TimeLatency(ssplot.CommandLine):
  """
  This class is a command line interface to generate a time vs. latency stats.
  """

  NAME = 'time-latency'
  ALIASES = ['timelat', 'tl']
  _SKIP = ('xlabel', 'ylabel')

  @staticmethod
  def create_parser(subparser):
    sp = subparser.add_parser(TimeLatency.NAME,
                              aliases=TimeLatency.ALIASES,
                              help=('Generate a time vs. latency plot'))
    sp.set_defaults(func=TimeLatency.run_command)

    sp.add_argument('ifile',
                    help='input latency file')
    sp.add_argument('plotfile',
                    help='output plot file')

    sp.add_argument('--latency_units', default=None,
                    help='latency units')
    sp.add_argument('--minimum', type=ssplot.str_to_bool, default='y',
                    help='whether or not to plot minimum latency')

    ssplot.MultilinePlot.add_args(sp, *TimeLatency._SKIP)

  @staticmethod
  def run_command(args, plt):
    # create a sample stats object of latencies
    stats = handycsv.GridStats.read(args.ifile)

    # determine the fields and data labels to plot
    fields = ssplot.LoadLatencyStats.FIELDS
    if not args.minimum:
      fields.remove('Minimum')
    fields = list(reversed(fields))

    # gather data
    xdata = stats.row_names()
    ydatas = []
    for field in fields:
      ydatas.append(stats.get_column(field))

    # create x and y axis labels
    xlabel = 'Time'
    ylabel = 'Latency'
    if args.latency_units:
      ylabel += ' ({0})'.format(args.latency_units)

    # plot
    mlp = ssplot.MultilinePlot(plt, xdata, ydatas)
    mlp.set_xlabel(xlabel)
    mlp.set_ylabel(ylabel)
    mlp.set_data_labels(fields)
    mlp.apply_args(args, *TimeLatency._SKIP)
    mlp.plot(args.plotfile)

    return 0


ssplot.CommandLine.register(TimeLatency)
