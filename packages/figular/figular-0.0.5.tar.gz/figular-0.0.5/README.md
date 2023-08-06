<!--
SPDX-FileCopyrightText: 2021-2 Galagic Limited, et. al. <https://galagic.com>

SPDX-License-Identifier: CC-BY-SA-4.0

figular generates visualisations from flexible, reusable parts

For full copyright information see the AUTHORS file at the top-level
directory of this distribution or at
[AUTHORS](https://gitlab.com/thegalagic/figular/AUTHORS.md)

This work is licensed under the Creative Commons Attribution 4.0 International
License. You should have received a copy of the license along with this work.
If not, visit http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# Figular

Figular generates visualisations from flexible, reusable parts. It is in early
development so use with caution.

The official repository is [https://gitlab.com/thegalagic/figular](https://gitlab.com/thegalagic/figular).

## Table of Contents

<!--
* [Security](#security)
-->

* [Install](#install)
* [Background](#background)
* [Usage](#usage)
* [Thanks](#thanks)
* [Contributing](#contributing)
* [Licensing](#licensing)

## Install

Prerequisites:

* Linux
* Python 3
* [Asymptote](https://asymptote.sourceforge.io/). This may be in your
  distribution's repositories already as `asymptote`. If not see Asymptote's
  [Installation](https://asymptote.sourceforge.io/doc/Installation.html) docs.
* [dvisvgm](https://dvisvgm.de/). A dependency of asymptote required for
  producing SVG graphics. This may be in your distribution's repositories under
  `dvisvgm`, `texlive-dvisvgm` or `texlive-extra-utils`. If not see dvisvgm's
  [Downloads](https://dvisvgm.de/Downloads/) page.

Install the latest version via pip:

```bash
pip install figular
```

This will install the cmdline tool `fig`. For usage see below.

## Background

Producing visualisations and documents can result in a lot of effort that is
hard to reuse. Work such as drawing a diagram by hand, arranging items, placing
text, aligning graphs and choosing colours may have to be repeated if a document
needs to be updated or expanded to depict new data.

If we can automate that work and have our visualisations react to new data
intelligently we can get a much higher level of reuse. If we can build a
community we can share our efforts with others and build on their
work in turn.

Figular is designed to help in particular situations where:

* You need to produce a good looking visualisation, image, document
* You need to produce it more than once, for example a report or dashboard, a
  set of labels, marketing campaign graphics.
* The visualisation may need to adapt in future to changes in the data driving
  it, design changes, layout tweaks etc.
* You want to share/collaborate on the visualisation or leverage the work of
  others.

Figular provides preprepared visualisations that you can populate with your own
data and tweak the style or layout. You can also develop your own and share with
the community. Visualisations can be combined, remixed and adapted.

It's available in the browser and at the cmdline.

## Usage

Figular produces SVG files. Run it from the cmdline:

```bash
fig [FIGURE] ARGUMENTS
```

You can specify FIGUREs by name, for example `concept/circle`. Follow this with
arguments in the form `param=ARGUMENT`. If an argument contains spaces surround
with it with quotes to prevent your shell from splitting the argument.

For example to use the `concept/circle` figure and pass it some `blob` arguments:

```bash
fig concept/circle blob=One blob=Two
```

This will produce a file `out.svg`.

Full documentation and a list of all figures is available in the docs directory
of the source repository or your installation i.e. [/docs/Figular.md](/docs/Figular.md).

## Thanks

Like all free/open source software Figular is made possible by building on the
shoulders of giants. Our thanks to every contributor and maintainer who have
brought the ecosystem to where it is today.

In particular we thank the [Asymptote](https://asymptote.sourceforge.io/)
project whose graphics language makes it easy to design pictures with code.

## Contributing

It's great that you're interested in contributing. Please visit the
[wiki](https://gitlab.com/thegalagic/figular/-/wikis/home) for how to get
involved.

## License

We declare our licensing by following the REUSE specification - copies of
applicable licenses are stored in the LICENSES directory. Here is a summary:

* All source code is licensed under AGPL-3.0-or-later.
* Anything else that is not executable, including the text when extracted from
  code, is licensed under CC-BY-SA-4.0.

For more accurate information, check individual files.

Figular is free software: you can redistribute it and/or modify it under the
terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
