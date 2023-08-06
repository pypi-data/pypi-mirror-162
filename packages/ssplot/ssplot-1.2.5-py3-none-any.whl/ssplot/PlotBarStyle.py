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

class PlotBarStyle(object):
  """
  This is a plot bar style generator
  """

  __style_map = {}
  __default_style = None

  def __init__(self, style, plt, bar_count):
    assert style in PlotBarStyle.__style_map, \
      '{} is not a registered plot bar style'.format(style)
    self._all_styles = list(zip(*PlotBarStyle.__style_map[style](
      plt, bar_count)))
    assert len(self._all_styles) == bar_count, 'error in style implementation'

  @staticmethod
  def styles():
    return list(PlotBarStyle.__style_map.keys())

  @staticmethod
  def default():
    return PlotBarStyle.__default_style

  @staticmethod
  def registerStyle(style, func, default=False):
    assert style not in PlotBarStyle.__style_map, \
      '{} is already a registered plot style'.format(style)
    PlotBarStyle.__style_map[style] = func
    if default:
      PlotBarStyle.__default_style = style

  def __getitem__(self, index):
    names = ['color', 'edgecolor', 'ecolor', 'hatch']
    style = self._all_styles[index]
    assert len(names) == len(style)
    return dict(zip(names, style))

def colorful(plt, bar_count):
  if bar_count <= 3:
    cmap = plt.get_cmap('brg')
  else:
    cmap = plt.get_cmap('gist_rainbow')
  colors = [cmap(idx) for idx in numpy.linspace(0, 1, bar_count)]
  edgecolors = colors
  ecolors = colors
  hatches = [''] * bar_count
  return colors, edgecolors, ecolors, hatches
PlotBarStyle.registerStyle('colorful', colorful, True)

def black(plt, bar_count):
  colors = ['w'] * bar_count
  edgecolors = ['k'] * bar_count
  ecolors = ['k'] * bar_count
  hatches = ['//', '---', '++', '||', '.', '\\\\', 'o', 'xx', 'O', '*']
  assert len(hatches) >= bar_count, 'Too many bars for plot style'
  return colors, edgecolors, ecolors, hatches[:bar_count]
PlotBarStyle.registerStyle('black', black, False)

def inferno(plt, bar_count):
  cmap = plt.get_cmap('inferno')
  colors = [cmap(idx) for idx in numpy.linspace(0, 0.9, bar_count)]
  edgecolors = colors
  ecolors = colors
  hatches = [''] * bar_count
  return colors, edgecolors, ecolors, hatches
PlotBarStyle.registerStyle('inferno', inferno, False)

def inferno2(plt, bar_count):
  assert bar_count <= 2, '"inferno2" only supports 2 bars'
  cmap = plt.get_cmap('inferno')
  colors = [cmap(idx) for idx in numpy.linspace(0, 1.0, 6)]
  colors = [colors[1], colors[-2]]
  colors = colors[0:bar_count]
  edgecolors = colors
  ecolors = colors
  hatches = [''] * bar_count
  return colors, edgecolors, ecolors, hatches
PlotBarStyle.registerStyle('inferno2', inferno2, False)

def plasma(plt, bar_count):
  cmap = plt.get_cmap('plasma')
  colors = [cmap(idx) for idx in numpy.linspace(0, 0.9, bar_count)]
  edgecolors = colors
  ecolors = colors
  hatches = [''] * bar_count
  return colors, edgecolors, ecolors, hatches
PlotBarStyle.registerStyle('plasma', plasma, False)
