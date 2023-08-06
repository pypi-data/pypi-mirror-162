# SPDX-FileCopyrightText: 2021-2 Galagic Limited, et. al. <https://galagic.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# figular generates visualisations from flexible, reusable parts
#
# For full copyright information see the AUTHORS file at the top-level
# directory of this distribution or at
# [AUTHORS](https://gitlab.com/thegalagic/figular/AUTHORS.md)
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import sys


def usage():
    usage = '''
fig is short for figular which generates visualisations from reusable
parts.

Usage:
  fig [flags] [figure/file] [arguments...]

Specify a Figure by name or provide your own Asymptote source code file with
the Figular figures available as imports.

Available figures:
  concept/circle     A circle of text blobs with (optionally) one in the
                     centre. It can be rotated and the font changed. It takes
                     arguments: blob, middle, degreeStart and font.
  org/orgchart       An organisational chart depicting the structure of an
                     organisation and the relationships of its positions or
                     roles. It takes arguments of the form:
                     "Name|Description|Parent"

Flags:
  --help             Help for Figular

Examples:
  fig concept/circle blob=Hello blob=There blob=You
  fig org/orgchart "Boss|CEO|" "Employee|Team Lead|Boss"
  fig myfile.asy'''
    print(usage)
    exit(0)


def main(args=None):
    """ Marshall the args and run the figure """
    if args is None:
        args = sys.argv[1:]
    if len(args) == 0:
        exit(0)

    cmd = ['asy',
           '-safe', '-noView', '-noglobalread',
           '-f', 'svg', '-tex', 'xelatex',
           '-o', 'out.svg']
    sourcefile = args[0]
    figurefile = os.path.join(os.path.dirname(__file__), f"{args[0]}.asy")
    remainingArgs = args[1:]

    if os.path.exists(sourcefile):
        cmd.append(sourcefile)
        input = None
    elif os.path.exists(figurefile):
        cmd.extend(['-autoimport',
                    os.path.join(os.path.dirname(__file__), figurefile),
                    '-c', 'run(currentpicture, input(comment=""));'])
        input = "\n".join(remainingArgs)
    elif args[0] == "--help":
        usage()
    else:
        print(f"fig: argument {args[0]} was neither a figure nor a file!")
        exit(1)

    # Add the right dir to environ for Asymptote to find our figures
    os.environ["ASYMPTOTE_DIR"] = os.path.join(os.path.dirname(__file__))
    subprocess.run(cmd, input=input, text=True)
