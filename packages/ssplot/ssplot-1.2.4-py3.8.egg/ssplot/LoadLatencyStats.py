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

class LoadLatencyStats(object):
  """
  This class holds load versus latency statistics. It is a simple class that
  contains the data from one load sweep.
  """

  FIELDS = ['Minimum', 'Mean', 'Median', '90th%', '99th%', '99.9th%',
            '99.99th%', '99.999th%', 'Maximum']

  def __init__(self, start, stop, step, grids, row='Packet'):
    # save incase someone needs to check these
    self.start = start
    self.stop = stop
    self.step = step

    # create arrays
    assert start <= stop, 'start must be <= stop'
    assert step > 0, 'step must be > 0.0'
    load = numpy.arange(start, stop, step)
    self.data = {'Load': load}
    for field in LoadLatencyStats.FIELDS:
      self.data[field] = numpy.empty(len(load), dtype=float)

    # verify stat row and number of grids
    assert row in ['Packet', 'Message', 'Transaction']
    assert len(grids) == len(self.data['Load']), 'wrong number of grids'

    # load data arrays
    for idx, grid in enumerate(grids):
      assert isinstance(grid, handycsv.GridStats), 'grids must be GridStats'
      for key in self.data.keys():
        if key != 'Load':
          self.data[key][idx] = grid.get(row, key)
