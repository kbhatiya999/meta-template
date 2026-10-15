# Developing

You use harbor the same way your users do: the same package and commands, and
the version of the release you're building on. The only difference is that your
copy runs the code in your checkout.

New to the tools here (mise, fnox, Tilt, Copier, ...)? Read the
[Primer](primer/index.md) first: one short page per tool, in reading order.

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

Every task is a script file, one per task. mise loads two folders together:

| Folder | Holds | Owned by |
|--------|-------|----------|
| `mise-tasks/` | the shared toolkit: `tilt:*`, `env` | the template (`template/mise-tasks/`; here, links to it) |
| `.mise/tasks/` | this repo's own tasks | this repo; a task with the same name overrides the toolkit's |

A file's path is its name: `.mise/tasks/docs/serve` is `mise run docs:serve`,
and `build/_default` is plain `build`. Its description and settings are `#MISE`
comments at the top, and how Tilt treats it is `#TILT` comments
([below](#dashboard)). `mise.toml` holds only tools and settings, so it never
grows with the task list.

| Task | Does |
|------|------|
| `mise run tilt:up` / `tilt:down` | start / stop this repo's Tilt dashboard |
| `mise run tilt …` | any tilt command against it, e.g. `mise run tilt get uiresource` |
| `mise run tilt:others` / `tilt:stop <pid>` | list / stop other Tilts serving this repo |
| `mise run env` | every value tasks see, and the file it comes from |
| `mise run dev` / `undev` | install / uninstall the checkout as an editable uv tool |
| `mise run test` | end-to-end tests in a throwaway sandbox (offline; your config is never touched) |
| `mise run build` | build the sdist and wheel and check them as PyPI would |
| `mise run docs:serve` | this site with live reload, on `DOCS_PORT` |
| `mise run docs:build` | build the site the way CI does (fails on warnings) |
| `mise run release` | publish the next version, then refresh your install ([Releasing](releasing.md)) |
| `mise run release:dry-run` | the release workflow locally in Docker: version, changelog, build; publishes nothing |
| `mise run ci:local` | the CI workflow locally in Docker |
| `mise run harbor:status` / `harbor:sync` | your installed harbor, with this repo's fnox values |
| `mise run examples:secret` | a task receiving a secret, redacted in its output |

To add a task, add an executable file:

```bash
#!/usr/bin/env bash
#MISE description="Lint the shell scripts"
#TILT deps=mise-tasks,.mise/tasks
exec shellcheck mise-tasks/.lib/* .mise/tasks/*
```

Saved as `.mise/tasks/lint` (and `chmod +x`), it's `mise run lint`, and the
dashboard grows a *lint* button that reruns whenever a task changes.

## Dashboard

You don't need to remember any of these flows:

```sh
mise run tilt:up      # then open the URL it prints
```

[Tilt](https://tilt.dev) shows a button for every task, generated from mise's
task list, so a new task needs no Tiltfile edit. Buttons are grouped by folder
(`docs:serve` and `docs:build` under *docs*). By default a task runs when you
click it; a few comment lines in the task's file change that:

| In the task file | Tilt |
|------------------|------|
| `#TILT serve` | a long-running server, restarted when config changes |
| `#TILT deps=src,tests` | also runs whenever those paths change |
| `#TILT link=http://127.0.0.1:${DOCS_PORT}/` | a link on the resource; `${NAME}` as tasks see it |
| `#TILT hide` | no button (as do mise's hidden tasks) |

Tilt's file triggers are not mise's `sources`: mise skips a task whose sources
haven't changed, so a click would silently do nothing.

The Tiltfile is split by job, and its shared parts come from the template:

```text
Tiltfile                  includes the parts below
tilt/tasks.Tiltfile       buttons from mise's task list
tilt/others.Tiltfile      other dashboards for this repo, and the Stop button
tilt/uibutton.Tiltfile    Tilt's button extension, loaded locally (no download)
.tilt/Tiltfile            optional: this repo's own extras
```

`mise run tilt:down` stops it all. Every button is also a plain `mise run <task>`,
so nothing depends on Tilt.

### More than one dashboard

Two Tilts running this repo's Tiltfile run every server twice, so they fight
over ports (`Address already in use`). That happens easily: a `mise run tilt:up`
in a second terminal, or after changing `TILT_PORT`, when the old dashboard
keeps running on the old port.

Each dashboard watches for the others, found by their working directory, so a
different port or terminal can't hide one:

- **other tilts** (group *tilt*) turns red and lists each one: process id, port,
  when and in which terminal it started.
- Its **Stop another Tilt** button asks which one, then stops it and the servers
  it started. Servers in your dashboard restart by themselves and take the
  freed ports.
- `mise run tilt:up` also warns before starting when one is already running.

From a terminal: `mise run tilt:others` lists them, `mise run tilt:stop <pid>`
stops one.

## Values, secrets and flavours

Tilt keeps the environment it starts with, and reloading the Tiltfile doesn't
refresh it. So values never come from your shell or from Tilt. They live in
[fnox](https://fnox.jdx.dev), plain config and secrets alike, split by topic:

| File | Committed | Holds |
|------|-----------|-------|
| `fnox.toml` | yes | imports the files below, and flavours (profiles) |
| `fnox/config.toml` | yes | plain values: `TILT_PORT`, `DOCS_PORT`, ... |
| `fnox/secrets.toml` | yes | secrets (through a provider), always `env = "exec"` |
| `fnox.local.toml` | no | your machine's overrides; start from `fnox.local.toml.example` |
| `mise.local.toml` | no | which flavour you use: `FNOX_PROFILE = "<profile>"`; start from `mise.local.toml.example` |

fnox also merges `fnox.toml` files from parent folders and your global config
(`~/.config/fnox/config.toml`). `mise run env` (also a button) shows which file
each value actually comes from:

```console
$ mise run env
fnox profile: default  (pick one with FNOX_PROFILE in mise.local.toml)

  KEY              VALUE                      FROM
  EXAMPLE_TOKEN    (secret: tasks only)       fnox/secrets.toml
  TILT_PORT        10369                      fnox/config.toml
  DOCS_PORT        8361                       fnox/config.toml
```

Every task reads values the same way, fresh on every run, and `mise run tilt:up`
starts Tilt with an otherwise empty environment. So editing a value, adding or
removing an override, or switching flavour applies the next time you click,
with no restart, and servers restart by themselves. Only `TILT_PORT` needs
`mise run tilt:down` and `tilt:up`: Tilt can't move a running dashboard.

### Ports

Each repo gets its own `TILT_PORT` and `DOCS_PORT`, so dashboards of different
projects run side by side. Set them in fnox; without them the toolkit derives
both from the repo's path, so every repo still differs without any setup.

### Secrets

Secrets are marked `env = "exec"`: tasks run through `fnox exec` receive them;
your shell (`fnox activate`), agents' shells and `fnox export` never do. Store
real values through a provider, never as a plain `default`:

```sh
fnox provider add keychain keychain        # once
fnox set DEPLOY_TOKEN --provider keychain  # prompts for the value
```

To give a secret to one task only, with its value redacted in that task's
output, grant it with mise's [fnox integration](https://mise.jdx.dev/environments/secrets/fnox.html):

```bash
#!/usr/bin/env bash
#MISE secrets=["DEPLOY_TOKEN"]
./deploy.sh   # reads $DEPLOY_TOKEN; mise prints [redacted] if it shows up
```

`mise run examples:secret` shows this with `EXAMPLE_TOKEN`, a placeholder.

### Flavours

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
mise run ci:local          # tests, package build, docs build, as CI runs them
mise run release:dry-run   # version, changelog cut, build: what a release would do
```

A local release run is always a dry run: the workflow skips publishing, pushing
and the GitHub release whenever it runs under act (`ACT=true`), so a local run
can't publish anything even by mistake. Its changelog edit happens inside the
container and never reaches your files. On GitHub, the same rehearsal is
`gh workflow run release.yml -f dry_run=true`.

`.actrc` pins act's runner image, so act never stops to ask for one. The first
run downloads it (about 1 GB).

## Reusing this setup

**In meta repos:** the template ships the same toolkit (`mise-tasks/` with
`tilt:*` and `env`, plus the meta-repo tasks `sync`, `status`, `pull`, ...), the
same Tiltfile, and the same fnox conventions. Template updates (`harbor sync`)
keep `mise-tasks/`, `Tiltfile` and `tilt/` current; a repo's own tasks go in
`.mise/tasks/`, which the template never touches.

**In another product:** nothing in the toolkit names harbor. Copy:

```text
mise-tasks/                       the toolkit: tilt:*, env (from template/mise-tasks/)
Tiltfile, tilt/                   the dashboard (from template/)
.mise/tasks/                      your own tasks (dev, test, release, ... as examples)
mise.toml                         tools and settings
fnox.toml, fnox/                  values and secrets
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
