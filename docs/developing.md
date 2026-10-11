# Developing

You use harbor the same way your users do: the same package and commands, and
the version of the release you're building on. The only difference is that your
copy runs the code in your checkout.

## Setup

Requires [mise](https://mise.jdx.dev) (it installs uv for you) and git.

```sh
git clone https://github.com/kbhatiya999/meta-template.git ~/repo/meta-template
cd ~/repo/meta-template
mise trust
mise run dev
```

`mise run dev` installs the checkout as an **editable uv tool**, the same
`uv tool install` your users run, but pointed at your code:

```text
Installed harbor-meta from ~/repo/meta-template (editable)
harbor-meta v2026.10.11.2.post1.dev0+g990b5db
- harbor
- harbor-meta
```

`harbor` is now on your `PATH` everywhere. Code changes apply on the next run.
Run `mise run dev` again after a release, a pull, or a dependency change, so the
version and dependencies are refreshed.

## Which version you're on

The version comes from git tags ([hatch-vcs](https://github.com/ofek/hatch-vcs)):

| Checkout | `harbor --version` |
|----------|--------------------|
| exactly on a release tag, clean | `2026.10.11.2`, the same as users |
| commits or edits after a release | `2026.10.11.2.post1.dev0+g<hash>`, i.e. built on 2026.10.11.2 |

Published releases get their version from the release workflow, so users only
ever see clean date versions.

## Which template you're on

A released harbor renders the template tag matching its own version. Your
editable harbor renders **your checkout's committed HEAD**:

```console
$ harbor --version
harbor 2026.10.11.2.post1.dev0+g990b5db (editable: ~/repo/meta-template, template v2026.10.11.2-0 = its committed HEAD)
```

So the rule is: **commit a template change, then `harbor sync`.** Your own meta
repos pick it up exactly the way users' repos will after the release.
Uncommitted template edits are ignored on purpose. Copier would record them as a
throwaway commit that later updates can't find again.

To try a template edit without committing it, render it somewhere disposable:

```sh
copier copy --vcs-ref HEAD ~/repo/meta-template /tmp/try-meta
```

## Tasks

| Task | Does |
|------|------|
| `mise run dev` | install the checkout as an editable uv tool |
| `mise run undev` | uninstall it |
| `mise run build` | build the sdist and wheel and check them as PyPI would |
| `mise run docs` | serve this site locally with live reload |
| `mise run docs-build` | build the site the way CI does (fails on warnings) |
| `mise run release` | publish the next version, then refresh your install ([Releasing](releasing.md)) |

## Reusing this setup for another product

None of it names harbor, so it carries over to any uv-packaged Python CLI.
Copy these files:

```text
mise.toml                         the tasks above
.github/workflows/release.yml     date-versioned release to PyPI + GitHub
.github/scripts/changelog.py      cuts CHANGELOG.md into release notes
.github/workflows/docs.yml        docs site to GitHub Pages   (optional)
mkdocs.yml, docs/                 the site                    (optional)
CHANGELOG.md                      start with just "## [Unreleased]"
```

Then, in the new project's `pyproject.toml`, take the version from git:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"

[tool.hatch.version.raw-options]
version_scheme = "no-guess-dev"
git_describe_command = ["git", "describe", "--dirty", "--tags", "--long", "--match", "v[0-9]*"]
```

The links in `changelog.py`'s release notes and in `mkdocs.yml` point at this
project, so change those. Then add a PyPI trusted publisher (see
[Releasing](releasing.md#one-time-setup)) and run `mise run dev`.
