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

import gzip
import math
import numpy
import percentile
import random

class SampleStats(object):
  """
  Sample statistics for a single simulation run.
  """

  def __init__(self, filename, allow_negative=False):
    # read in raw data
    self.times = []
    self.samples = []
    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename, 'rb') as fd:
      while True:
        line = fd.readline().decode('utf-8')
        delim = line.find(',')
        if (delim >= 0):
          cols = line.split(',')
          startTime = float(cols[0])
          endTime = float(cols[1])
          self.times.append(startTime)
          self.samples.append(endTime - startTime)
        else:
          break
      self.times = numpy.array(self.times)
      self.samples = numpy.array(self.samples)
      assert len(self.times) == len(self.samples)

    # size
    self.size = len(self.times)
    if self.size > 0:
      # min and max
      self.tmin = min(self.times)
      self.tmax = max(self.times)
      self.smin = min(self.samples)
      self.smax = max(self.samples)
      if allow_negative:
        assert self.smin >= 0, 'samples can not be negative'

      # compute the probability density function
      try:
        hist, self.pdfx = numpy.histogram(self.samples, density=True, bins='auto')
      except:
        hist, self.pdfx = numpy.histogram(self.samples, density=True)
      self.pdfy = hist.astype(float) / hist.sum()

      # compute the cumulative distribution function
      self.cdfx = numpy.sort(self.samples)
      self.cdfy = numpy.linspace(1.0 / self.size, 1.0, self.size)

      # find percentiles
      self.p50 = self.percentile(0.50)
      self.p90 = self.percentile(0.90)
      self.p99 = self.percentile(0.99)
      self.p999 = self.percentile(0.999)
      self.p9999 = self.percentile(0.9999)

  def percentile(self, percent):
    """
    This function retrieves a sample percentile.
    """
    if percent < 0 or percent > 1:
      raise Exception('percent must be between 0 and 1')
    index = int(round(percent * len(self.cdfx)))
    index = min(len(self.cdfy) - 1, index)
    return self.cdfx[index]

  def nines(self):
    """
    This computes the number of nines needed to represent the percentile
    distribution.
    """
    if self.size > 0:
      nines = int(math.ceil(math.log10(len(self.cdfx))))
    else:
      nines = 5
    return nines
