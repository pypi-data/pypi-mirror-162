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

# Contributing

Feedback and contribution are very welcome!

## Table of Contents

* [General Information](#general-information)
* [Contributions](#contributions)
  * [Working with the Code](#working-with-the-code)
  * [Developer Certificate of Origin (DCO)](#developer-certificate-of-origin-dco)
  * [License](#license)
  * [Code Changes](#code-changes)
  * [Updating Dependencies](#updating-dependencies)
  * [Releasing](#releasing)
* [Vulnerability Reporting or Security Issues](#vulnerability-reporting-or-security-issues)
* [Attribution](#attribution)

## General Information

This project is just getting started! To discuss a new idea or contribution the
best way to contact us is through the details on our
website at [figular.com](https://figular.com/). If you have found a problem or
bug you can also raise a new issue in our GitLab repository:
[https://gitlab.com/thegalagic/figular](https://gitlab.com/thegalagic/figular).

Our documentation consists of the following files in the repository:

* AUTHORS.md
* CHANGELOG.md
* CODE_OF_CONDUCT.md
* CONTRIBUTING.md (this file)
* GOVERNANCE.md
* README.md
* LICENSES directory
* docs directory

## Contributions

Please note that this project is released with a Contributor Code of Conduct. By
participating in this project you agree to abide by its terms. We use the
[Contributor Convenant version
2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct.html) a
copy of which is available in the repository: CODE_OF_CONDUCT.md. This code is
the same as used by the Linux kernel and many other projects.

### Working with the Code

You'll need to install the prerequisites as stated in the README section
'Install'. On top of that there are some prerequisites for building the code:

* We use [ninja](ninja-build.org/) as our build tool, it's available as
  package `ninja-build` on most distros.
* Python [build](https://pypi.org/project/build/) is needed to build our Python
  package: `pip install build`.
* We use the [REUSE tool](https://github.com/fsfe/reuse-tool) to check licensing
  is compliant. This is available either through pip or some distros have it
  available as package `reuse`.

Once you've checked out the code run the following from the new source dir:

* Run `./configure` to create your own build settings file `build_config.ninja`.
  You can change the build dir by adding a line `builddir=DIR`, where DIR is
  where you want build artifacts to end up. The default dir is `build`.
* Run `ninja` to build the project. Just a warning our tests are extremely
  fragile to the exact version of asymptote and texlive installed. This will be
  addressed in future but for now expect breakage. The test will show the files
  that do not meet expectations and there you will see the versions reported.

To install figular from your source directory run: `pip install .` You should
then be able to run your new version with `fig`.

#### Adding a new Figure

Every figure has to provide this interface:

```asy
void run(picture pic, string[] input)

```

It is passed an array of lines of string input and a picture to draw on. Input
that will end up as text in a figure should be correctly escaped for LaTeX.

New figures should be created in the right subdir following our naming
convention of grouping similar figures together, e.g. `org/orgchart.asy`.

#### Advanced

The normal way a figure is run means input actually comes via a stdin pipe but
thanks to Asymptote's implicit casting of file to string[] we can not be aware
of this. We do not use Asymptote's built-in `stdin` as it enforces a '#'
[comment
character](https://asymptote.sourceforge.io/doc/Files.html#index-comment-character)
and this interferes with our interpretation (e.g. markdown).

### Developer Certificate of Origin (DCO)

All contributions must agree to the Developer Certificate of Origin (DCO) to
certify that you wrote or otherwise have the right to submit code or
documentation to the project. We use the same DCO as many other projects: the
[Developer Certificate of Origin version
1.1](https://developercertificate.org/):

> Developer Certificate of Origin
> Version 1.1
>
> Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
> 1 Letterman Drive
> Suite D4700
> San Francisco, CA, 94129
>
> Everyone is permitted to copy and distribute verbatim copies of this
> license document, but changing it is not allowed.
>
>
> Developer's Certificate of Origin 1.1
>
> By making a contribution to this project, I certify that:
>
> (a) The contribution was created in whole or in part by me and I
>     have the right to submit it under the open source license
>     indicated in the file; or
>
> (b) The contribution is based upon previous work that, to the best
>     of my knowledge, is covered under an appropriate open source
>     license and I have the right under that license to submit that
>     work with modifications, whether created in whole or in part
>     by me, under the same open source license (unless I am
>     permitted to submit under a different license), as indicated
>     in the file; or
>
> (c) The contribution was provided directly to me by some other
>     person who certified (a), (b) or (c) and I have not modified
>     it.
>
> (d) I understand and agree that this project and the contribution
>     are public and that a record of the contribution (including all
>     personal information I submit with it, including my sign-off) is
>     maintained indefinitely and may be redistributed consistent with
>     this project or the open source license(s) involved.

Simply submitting a contribution implies this agreement however for larger
contributions please include a "Signed-off-by" tag in every patch (this tag is a
conventional way to confirm that you agree to the DCO). You can do this with git
commit --signoff (the -s flag is a synonym for --signoff).

Another way to do this is to write the following at the end of the commit
message, on a line by itself separated by a blank line from the body of the
commit:

```text
Signed-off-by: YOUR NAME <YOUR.EMAIL@EXAMPLE.COM>
```

You can signoff by default in this project by creating a file (say
"git-template") that contains some blank lines and the signed-off-by text above;
then configure git to use that as a commit template. For example:

```text
git config commit.template ~/cii-best-practices-badge/git-template
```

It's not practical to fix old contributions in git, so if one is forgotten, do
not try to fix them. We presume that if someone sometimes used a DCO, a commit
without a DCO is an accident and the DCO still applies.

### License

All (new) contributed material must be released under the AGPLv3 or later. A
copy of the license is included in the repository, see the LICENSES directory.
All new contributed material that is not executable, including all text when not
executed, is also released under the [Creative Commons Attribution ShareAlike
4.0 International (CC BY-SA
4.0)](https://creativecommons.org/licenses/by-sa/4.0/) license.

### Code Changes

* When reusing components they MUST have a license compatible with the license of
  this software.
* Test coverage is required except in case of trivial changes

Below are guidelines for specific languages.

#### Python

Please ensure code conforms with [flake8](https://flake8.pycqa.org/en/latest/) linting.

#### Markdown

Please ensure Markdown confirms with
[mdl](https://github.com/markdownlint/markdownlint) linting.

### Updating Dependencies

There are some parts of figular that need to be kept up to date:

* Dependencies in `api/requirements.txt`
* Dependencies in `tests/python/requirements.txt`
  * Test dependencies e.g. pytest
  * Here we have to also replicate the versions and dependencies of our runtime
    environment so we can test the api: fastapi. These are NOT present in
    `api/requirements.txt` as they are already supplied in the runtime
    container.
* `pyproject.toml` lists some requirements of its own for building.
  We do not specify version numbers here, so there is no update needed. But it's
  noted in case this changes.
* `galagos` via copybara. Run `ninja update`

### Releasing

In the following `<VERSION>` should be replaced with the new version number
prepended with a `v`, e.g. `v1.0.0`.

* Update [CHANGELOG.md](CHANGELOG.md)

  The 'Unreleased' entry at the top of `CHANGELOG.md` should already
  enumerate the significant updates to the new version. If not update it, retitle
  it with the version number and date, then create a new empty 'Unreleased' entry.

* Update copyright years if applicable

  Edit galagos/local/settings.bara.sky and update the copyright year. You can
  use a range here so long as you have a statement explaining this use in your
  README. For an example see our README. You may want to re-apply your copyright
  headers to files now and check REUSE compliance to ensure all updated.

* Bump the version number

  Update version in `setup.cfg`.

  Commit this and above changes (including the `CHANGELOG.md` changes) in a
  commit with the message `figular <VERSION>`

  Create a new signed, annotated tag with:

  ```bash
  git tag -a -s <VERSION>
  ```

  Include the `CHANGELOG.md` notes corresponding to the new version as the
  tag annotation, except the first line should be:

  ```text
  figular <VERSION> - YYYY-MM-DD
  ```

* Create a GitLab release

  Push the new version commit and tag to GitLab via the following:

  ```bash
  git push --follow-tags
  ```

  Then use the GitLab API to [create
  a release](https://docs.gitlab.com/ee/api/releases/index.html#create-a-release):

  You'll need an access code with scopes: `read_api, api`

  ```bash
   pac=<PRIVATE ACCESS CODE>
  version=<VERSION>
  description=$(jq -Rs << EOF
  <COPY CHANGELOG FOR VERSION MINUS TITLE HERE
   ESCAPE ANY \, $ or ` AS PER BASH HERE-DOC FORMAT WITH a \
   https://www.gnu.org/software/bash/manual/bash.html#Here-Documents >
  EOF
  )
  curl https://gitlab.com/api/v4/projects/23633712/releases \
       --header 'Content-Type: application/json' \
       --header "PRIVATE-TOKEN: $pac" \
       --data @- << EOF
  { "name": "Figular $version",
    "tag_name": "$version",
    "description": $description }
  EOF
  ```

  If successful you'll see a response from the API with the new release's data
  returned on stdout.

* Upload a new package to PyPi: `ninja pypi_upload`

* Announce - make a brief announcement.

## Vulnerability Reporting or Security Issues

If you find a significant vulnerability, or evidence of one, please send an
email to the security contact that you have such information, and we'll tell
you the next steps. For now, the security contact is: infoNOSPAM@galagic.com
(remove the NOSPAM marker).

Please use an email system that supports hop-to-hop encryption using STARTTLS
when reporting vulnerabilities. Examples of such systems include Gmail,
Outlook.com, and runbox.com. See STARTTLS Everywhere if you wish to learn more
about efforts to encourage the use of STARTTLS. Your email client should use
encryption to communicate with your email system (i.e., if you use a web-based
email client then use HTTPS, and if you use email client software then configure
it to use encryption). Hop-to-hop encryption isn't as strong as end-to-end
encryption, but we've decided that it's strong enough for this purpose and it's
much easier to get everyone to use it.

We will gladly give credit to anyone who reports a vulnerability so that we can
fix it. If you want to remain anonymous or pseudonymous instead, please let us
know that; we will gladly respect your wishes.

## Attribution

Parts of this text are based on the contribution guide of the Core
Infrastructure Initiative's
[Best Practices Badge
Project](https://github.com/coreinfrastructure/best-practices-badge/blob/master/CONTRIBUTING.md),
licensed under the [Creative Commons Attribution 3.0 International (CC BY 3.0)
license or later.](https://creativecommons.org/licenses/by/3.0/):

Specifically the following sections were copied and adapted: the introduction,
'General information', 'Developer Certificate of Origin (DCO)', 'License',
'Vulnerability Reporting' and 'Code Changes'.
