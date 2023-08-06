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

Figular lets you build visualisations. You can choose from a range of
existing figures that can be customised or build your own (in future).

## Figures

A figure is a self-contained visualisation that can adjust itself based on your
content. Content can be parameters that control display (rotation, layout) and
data that populates the figure (text, images). Figular comes with a range of our
own figures, documentation on each of them is linked below:

* [Concept/circle](figures/concept/circle.md)
* [Org/orgchart](figures/org/orgchart.md)

Please help us grow this list by contributing to the project!

Figures can come from different repositories. If no repository is specified the
default is 'Figular' which is what comes bundled as standard with any
installation. At present we do not support repositories so this is purely
theoretical. Our inspiration comes from [flatpak](https://flatpak.org/).

Each figure has a unique, case-insensitive name within its repository. Related
figures are grouped together in a tree-like structure. Levels in the tree are
separated by a forward slash `/`, e.g.  'concept/circle'. Our inspiration comes
from URLs.

Figures can be versioned, if a version is not supplied the latest is assumed.
The version is not part of the name however. Versioning is inspired by [Semantic
Versioning](https://semver.org/). New versions should not break older usage
without a major version bump for example.

In future we may also support metadata such as categories/tags and other
information. Inspiration comes from [PyPi](pypi.org/).

## Threat Model

Figular tries to guarantee the following:

* There is no input that can cause Figular to do anything other than render an
  image.
* Figular will always return a timely result - whether an image can be produced
  or rendering was aborted.
* Figular will not reveal information about the system it is run on in its
  output.

Assumptions:

* The host system is trusted. For Figular cmdline we do not control the host
  system. For SaaS we do and should ensure the system is trusted.

* The user has an authentic copy of Figular. We should ensure all distribution
  channels provide a means by which the user can verify they have received an
  authentic copy. Further we should ensure our channels cannot be hijacked i.e.
  secure supply chain.

  Current distribution channels for Figular include:

  * [GitLab](gitlab.com/)
  * [PyPi](https://pypi.org/)

The adversary's attacks will vary depending on usage as detailed below.

### Figular at the Cmdline

The adversary's only means of attacking others is by communicating suggested
malicious input/usage to a target user i.e. social engineering. Attacks include:

* Exploitation of user system: adversary gains access to run arbitrary code as
  user on target system.
* Denial of service: excessive use of system resources
* If the adversary can gain access to a user's results then further attack
  vectors are possible. The user would have to play along with attacker by
  posting results back to adversary so further social engineering is required:
  * Adversary wishes to hijack compute power for own purposes by suggesting
    malicious input that causes some desirable computation to be performed and
    result to be contained in Figular output.
  * Adversary to reveal sensitive information about user/target system through
    Figular output, e.g. credentials, file contents, IP address, digital
    currency wallet.

### Figular SaaS

Attacks include:

* Exploitation of Figular infrastructure: adversary uses our compute power for
  their own purpose.
* Denial of service to others: excessive use of system resources.
* Information theft: mining of information from Figular infrastructure such as
  credentials, certificates in order to perpetrate further attacks e.g.
  supply chain attack, impersonation.
* Theft of users' data, renderings, etc by exploiting side-channels,
  escalation of privilege, code exploits etc.
  * One vector is to attack the current use of the `/tmp` filesystem for
    intermediate results of the render. If there was some naming collision or other
    method of tricking the request into reading from the wrong dir then
    results could be delivered to the wrong user.

    To mitigate we create a unique temp dir per request that is cleaned up after
    use. Inside this we also use a temp filename for the final output.
    Intermediate files that Asymptote creates are based on the final output
    filename so should also be using the same temp filename stem.
* Impersonation of other users to gain access to their data.
