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

__version__ = '1.2.4'

from .utils import *
from .consts import *

# data classes
from .SampleStats import SampleStats
from .LoadLatencyStats import LoadLatencyStats
from .LoadRateStats import LoadRateStats
from .LoadHopsStats import LoadHopsStats

# utility classes
from .PlotLineStyle import PlotLineStyle
from .PlotBarStyle import PlotBarStyle
from .GridStyle import GridStyle
from .FigureSize import FigureSize
from .LatencyPlot import LatencyPlot
from .MultilinePlot import MultilinePlot
from .MultibarPlot import MultibarPlot

# these are the commandline interfaces
from .CommandLine import CommandLine
from .TimeLatencyScatter import TimeLatencyScatter
from .LatencyPdf import LatencyPdf
from .LatencyCdf import LatencyCdf
from .LatencyPercentile import LatencyPercentile
from .LoadLatency import LoadLatency
from .LoadLatencyCompare import LoadLatencyCompare
from .LoadRate import LoadRate
#from .LoadRateVariance import LoadRateVariance    # loadratevar lrv (MAYBE or StdDev)
from .LoadRatePercent import LoadRatePercent
from .LoadPercentMinimal import LoadPercentMinimal
from .LoadAverageHops import LoadAverageHops
from .TimePercentMinimal import TimePercentMinimal
from .TimeAverageHops import TimeAverageHops
from .TimeLatency import TimeLatency
from .SimTimeCompare import SimTimeCompare
