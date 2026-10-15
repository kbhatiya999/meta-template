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

## Dashboard

You don't need to remember any of these flows:

```sh
mise run up      # then open the URL it prints
```

[Tilt](https://tilt.dev) shows every flow as a button, grouped as *develop*,
*check*, *docs*, *use* and *release*, with its last result and logs:

| Resource | Runs | When |
|----------|------|------|
| install | `mise run dev` | click, or automatically when `pyproject.toml` or `uv.lock` change |
| test | `mise run test` | click, or automatically when `src/`, `tests/`, `template/` or `copier.yml` change |
| docs | `mise run docs` | always running at <http://127.0.0.1:8361/meta-template/> |
| build, docs-build | the CI checks | click |
| ci-local | the CI workflow, in Docker | click |
| release-dry-run | the release workflow, in Docker, publishing nothing | click |
| harbor status, harbor sync | your installed harbor | click |
| release | `mise run release` | click |

`mise run down` stops it all. Every button is also a plain `mise run <task>`,
so nothing depends on Tilt.

### More than one dashboard

Two Tilts running this repo's Tiltfile run every server twice, so they fight
over ports (`Address already in use`). That happens easily: a `mise run up` in a
second terminal, or after changing `TILT_PORT`, when the old dashboard keeps
running on the old port.

Each dashboard watches for the others, found by their working directory, so a
different port or terminal can't hide one:

- **other tilts** (group *tilt*) turns red and lists each one: process id, port,
  when and in which terminal it started.
- Its **Stop another Tilt** button asks which one, then stops it and the servers
  it started. Servers in your dashboard restart by themselves and take the
  freed ports.
- `mise run up` also warns before starting when one is already running.

From a terminal: `scripts/tilts` lists them, `scripts/tilts --stop <pid>` stops one.

### Values, secrets and flavours

Tilt keeps the environment it starts with, and reloading the Tiltfile doesn't
refresh it. So values never come from your shell or from Tilt. They live in
[fnox](https://fnox.jdx.dev), plain config and secrets alike:

| File | Committed | Holds |
|------|-----------|-------|
| `fnox.toml` | yes | every value: ports, secrets (stored through a provider), and flavours as profiles |
| `fnox.local.toml` | no | your machine's overrides; start from `fnox.local.toml.example` |
| `mise.local.toml` | no | which flavour you use: `FNOX_PROFILE = "<profile>"`; start from `mise.local.toml.example` |

Every consumer reaches fnox the same way, so they all see the same values:

| Who | How |
|-----|-----|
| a task that needs values | `run = "fnox exec -- …"` |
| a Tilt button | `mise run <task>`, so the same |
| the Tiltfile (the docs link) | `mise exec -- fnox get DOCS_PORT` |
| Tilt itself | `mise run up` reads `TILT_PORT` with `fnox get`, then starts Tilt with an otherwise empty environment |

`fnox exec` resolves values on every run, and mise sets `FNOX_PROFILE` from
`mise.local.toml` on every run. So editing a value, adding or removing an
override, or switching flavour applies the next time you click, with no
restart, and the docs server restarts by itself. Only `TILT_PORT` needs
`mise run down` and `mise run up`: Tilt can't move a running dashboard.

```console
$ mise run env
fnox profile: default

Plain values:
  TILT_PORT=10369
  DOCS_PORT=8361
```

`mise run env` (also a Tilt button) shows what every task sees: the flavour,
the plain values, and the names of the secrets.

#### Secrets

Secrets are marked `env = "exec"` in `fnox.toml`. Tasks run through `fnox exec`
receive them; your shell (`fnox activate`), agents' shells and `fnox export`
never do. Store real values through a provider, never as a plain `default`:

```sh
fnox provider add keychain keychain        # once
fnox set DEPLOY_TOKEN --provider keychain  # prompts for the value
```

To give a secret to one task only, with its value redacted in that task's
output, grant it through mise's [fnox integration](https://mise.jdx.dev/environments/secrets/fnox.html)
instead of `fnox exec`:

```toml
[tasks.deploy]
secrets = ["DEPLOY_TOKEN"]
run = './deploy.sh'   # reads $DEPLOY_TOKEN; mise prints [redacted] if it shows up
```

`mise run secret-example` shows this with `EXAMPLE_TOKEN`, a placeholder.

#### Flavours

A flavour is an fnox profile: a set of values that overrides the defaults.

```toml
# fnox.toml
[profiles.scratch.secrets]
HARBOR_BASE = { default = "~/harbor-scratch" }
```

```toml
# mise.local.toml
[env]
FNOX_PROFILE = "scratch"
```

Every task and Tilt button now uses the `scratch` values. Remove the line to go
back to the default.

#### Ports

Each project gets its own ports in `fnox.toml` (`TILT_PORT`, `DOCS_PORT`), so
dashboards of different projects run side by side. For other Tilt commands use
`mise run tilt …` (for example `mise run tilt get uiresource`), which reads the
port from fnox.

## Tasks

| Task | Does |
|------|------|
| `mise run up` / `down` | start / stop the Tilt dashboard |
| `mise run env` | what tasks see: the fnox flavour, plain values and secret names |
| `mise run tilt …` | any tilt command against this project's dashboard |
| `mise run dev` | install the checkout as an editable uv tool |
| `mise run undev` | uninstall it |
| `mise run test` | end-to-end tests in a throwaway sandbox (offline; your config is never touched) |
| `mise run build` | build the sdist and wheel and check them as PyPI would |
| `mise run docs` | serve this site locally with live reload |
| `mise run docs-build` | build the site the way CI does (fails on warnings) |
| `mise run release` | publish the next version, then refresh your install ([Releasing](releasing.md)) |
| `mise run ci-local` | run the CI workflow (`.github/workflows/ci.yml`) locally in Docker |
| `mise run release-dry-run` | run the release workflow locally: version, changelog, build; publishes nothing |

## Agents

`AGENTS.md` (and `CLAUDE.md`, which includes it) describes the project as it is
now, so agents start with context. It's a snapshot, not a set of limits: agents
are free to go beyond it, and update it when they change how things work.

`.scratch/` is shared working memory for agents and you: notes, plans and
handoffs between sessions. It's gitignored, so nothing in it is committed, and
re-included in `.ignore`, so agents' search tools still find it.

## Running the GitHub workflows locally

[act](https://github.com/nektos/act) runs the workflows in Docker containers that
mimic GitHub's runners, using your working copy, uncommitted changes included.
Docker has to be running first: with [Colima](https://github.com/abiosoft/colima),
`colima start`. The tasks check this and stop with that hint if it isn't.

```sh
mise run ci-local          # tests, package build, docs build, as CI runs them
mise run release-dry-run   # version, changelog cut, build: what a release would do
```

A local release run is always a dry run: the workflow skips publishing, pushing
and the GitHub release whenever it runs under act (`ACT=true`), so a local run
can't publish anything even by mistake. Its changelog edit happens inside the
container and never reaches your files. On GitHub, the same rehearsal is
`gh workflow run release.yml -f dry_run=true`.

`.actrc` pins act's runner image, so act never stops to ask for one. The first
run downloads it (about 1 GB).

## Reusing this setup for another product

None of it names harbor, so it carries over to any uv-packaged Python CLI.
Copy these files:

```text
mise.toml                         the tasks above
Tiltfile                          the dashboard (keep the generic part, replace "use")
scripts/tilts                     finds and stops other Tilts serving the repo
fnox.toml                         every value: config, secrets, flavours
fnox.local.toml.example           document per-machine value overrides
mise.local.toml.example           document picking a flavour (FNOX_PROFILE)
.actrc, .github/workflows/ci.yml  local workflow runs with act, and CI
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
