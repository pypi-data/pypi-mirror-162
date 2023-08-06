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
import math
import numpy

class LoadRateStats(object):
  """
  This class holds load versus rate statistics. It is a simple class that
  contains the data from one load sweep.
  """

  FIELDS = ['Minimum', 'Mean', 'Maximum']

  def __init__(self, start, stop, step, grids, ignore_zeros=False):
    # check that all the grids are the same size
    for idx, grid in enumerate(grids[1:]):
      assert len(grid.column_names()) == len(grids[0].column_names()), (
          ("grid {0} and {1} don't have the same number of columns\n"
           "grid {0} is {2} with {3} columns\n"
           "grid {1} is {4} with {5} columns")
           .format(0, idx+1, grids[0].source, len(grids[0].column_names()),
                   grid.source, len(grid.column_names())))
      assert len(grid.row_names()) == len(grids[0].row_names()), (
        "grid {0} and {1} don't have the same #rows".format(0, idx+1))

    # save these incase someone needs to check them
    self.start = start
    self.stop = stop
    self.step = step

    # create arrays
    assert start <= stop, 'start must be <= stop'
    assert step > 0, 'step must be > 0.0'
    injected = numpy.arange(start, stop, step)
    self.data = {'Injected': injected}
    for field in LoadRateStats.FIELDS:
      self.data[field] = numpy.empty(len(injected), dtype=float)

    # check number of grids
    assert len(grids) == len(self.data['Injected']), 'wrong number of grids'

    # load data arrays
    for idx, grid in enumerate(grids):
      assert isinstance(grid, handycsv.GridStats), 'grids must be GridStats'
      # extract delivered
      delivered = []
      count = 0
      for term in range(0, len(grid.row_names()) - 1):
        value = grid.get(term, 'delivered') * 100
        if value > 0.0 or math.isnan(value) or not ignore_zeros:
          delivered.append(value)
          count += 1


      # compute stats
      minEj = min(delivered)
      meanEj = sum(delivered) / count
      maxEj = max(delivered)

      # prepare data
      self.data['Minimum'][idx] = minEj
      self.data['Mean'][idx] = meanEj
      self.data['Maximum'][idx] = maxEj
