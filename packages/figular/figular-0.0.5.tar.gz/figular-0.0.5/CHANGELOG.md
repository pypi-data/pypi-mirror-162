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

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.5 - 2022-08-11](https://gitlab.com/thegalagic/figular/-/releases/v0.0.5)

### Changed

* Big changes underneath, not yet exposed to end users:
  * Use [asyunit v2](https://gitlab.com/thegalagic/asymptote-glg-contrib/-/releases/v2.0.0)
    for tests which gives better isolation and detects more issues.
  * Evolved our libraries that power the figures. Drawing is expressed in more
    natural language and many more parts are stylable.
* All dependencies update to latest

### Removed

* Figure 'board election' has been removed to focus on our core figures. This
  decision was taken to avoid extra work in migrating it to the new changes
  above.

## [0.0.4 - 2022-05-13](https://gitlab.com/thegalagic/figular/-/releases/v0.0.4)

### Added

* New figure 'board election' introduced. See
  [docs](docs/figures/case/boardelection.md) and blog post [A new Figure for the
  OSI Board Election](https://figular.com/post/20220511172059/a-new-figure-for-the-osi-board-election/)
  for more info.
* New form at the cmdline `fig [file]` where you can run any custom Asymptote
  file and easily import our figures, e.g. `import "org/orgchart" as orgchart;`
  This allows anyone to combine existing figures into new pictures.
* Use an explicit 'style reset' in all figures so they all start from the same
  assumptions. This is particularly important now we are combining figures in
  board election.

### Changed

* The cmdline interface has changed so we can accept markdown. Now the first
  argument is either a file or figure and the remaining arguments are fed to the
  figure. You also no longer need to prefix a figure name with a hyphen.
* The input for a Figure is now of type `string[]` instead of `file`.
  Asymptote (I have discovered) will implicitly cast a file to string[] for us.
  This makes life much easier for testing and for reusing existing Figures in
  new pictures as we do not need to create files to pass data around.

### Removed

* We no longer rely on Asymptote's default `stdin` global variable which defines
  `#` as the comment char as we now need to interpret markdown. So comments are
  no longer possible in input (for now).

## [0.0.3 - 2022-02-15](https://gitlab.com/thegalagic/figular/-/releases/v0.0.3)

### Added

* New figure `org/orgchart` for organisational charts. See
  [orgchart](docs/figures/org/orgchart.md) in the docs for details.
* All Figure documentation has been expanded to cover website usage.
* README: direct contributors to our new wiki.

### Fixed

* Figures can accept and cope with all ASCII printable characters as input. We
  apply fuzz testing to this.
* Don't set CORS in the app, better set on network applicances.
* Build: clear out old built packages otherwise twine will try and upload them
  and fail.

### Changed

* Dependencies updated to latest.

## [0.0.2 - 2021-11-10](https://gitlab.com/thegalagic/figular/-/releases/v0.0.2)

### Added

* More detail on the deployment instructions.

### Fixed

* Quick patch to increase asy timeout to 3s which was hitting 1s limit on prod

## [0.0.1 - 2021-11-08](https://gitlab.com/thegalagic/figular/-/releases/v0.0.1)

### Added

* New cmdline flag `--help` to show usage.
* An API using FastAPI so Figular can be hosted and accessible over HTTP.
* GOVERNANCE.md was missing, added benevolent dictator.

### Fixed

* Bugs in figure `concept/circle`:
  * Crash when not given any blobs. Now we will skip drawing.
  * Crash when one blob and middle=true
  * Blobs were drawn on top of each other when only two blobs and middle=true

## [0.0.0 - 2020-04-01](https://gitlab.com/thegalagic/figular/-/releases/v0.0.0)

First version, basic cmdline usage and docs.

### Added

* New figure `concept/circle`, see docs for details.
