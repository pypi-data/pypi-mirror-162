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

import copy

class CommandLine(object):
  """
  This class is the abstract interface definition for a command line interface.
  """

  @staticmethod
  def create_parser(subparser):
    """
    This function adds a parser to the subparser object according to the
    specific command line interface implementation.
    """
    raise NotImplementedError('subclasses must override this')

  @staticmethod
  def run_command(args, plt):
    """
    This function is used to run the command if it is chosen at the command
    line. This function should be registered to the parser in create_parser().
    """
    raise NotImplementedError('subclasses must override this')

  # this is a mapping of all names (class->names)
  _names = {}

  @staticmethod
  def register(cls):
    # gather names
    primary_name = cls.NAME
    aliases = cls.ALIASES

    # create a set to hold all
    all_names = [primary_name] + aliases

    # check current names against all new names
    for new_name in all_names:
      for pname in CommandLine._names:
        assert new_name is not pname, '{} already exists'.format(new_name)
        for alias in CommandLine._names[pname]:
          assert new_name is not alias, '{} already exists'.format(new_name)

    # add to map
    CommandLine._names[cls] = all_names

  @staticmethod
  def command_lines():
    return set(CommandLine._names.keys())

  @staticmethod
  def all_names():
    return copy.copy(CommandLine._names)
