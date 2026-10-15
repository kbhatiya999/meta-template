# AGENTS.md

This file describes the project **as it is today**, so you start with context.
It isn't a rulebook and it isn't the limit of what's allowed. If the task needs
something it doesn't mention (a new tool, layout, workflow or approach), do it,
and update this file afterwards so it stays a true picture of the present.

## What this is

**harbor**: a Copier template for *meta repos* (repos whose `mani.yaml` lists
other repos) and a Python CLI, `harbor` (PyPI: `harbor-meta`), that keeps one
tree of them per GitHub account at `~/repo/<account>-meta`, with every repo
cloned exactly once. Docs: <https://kbhatiya999.github.io/meta-template/>.

## Layout

| Path | Holds |
|------|-------|
| `src/harbor/main.py` | the whole CLI (stdlib + copier + pyyaml) |
| `copier.yml`, `template/` | the template that harbor renders into meta repos |
| `template/AGENTS.md.jinja` | the AGENTS.md *generated meta repos* get (not this file) |
| `tests/e2e.sh` | end-to-end tests in an offline sandbox (fake `gh`, local bare repos) |
| `mise.toml` | developer tasks; `mise tasks` lists them |
| `Tiltfile` | the same tasks as dashboard buttons (`mise run up`) |
| `scripts/tilts` | finds other Tilts serving this repo (by working directory) and stops one |
| `fnox.toml`, `fnox.local.toml` | every value: ports, secrets, flavours (profiles); the local one is gitignored |
| `mise.local.toml` | which fnox flavour you use (`FNOX_PROFILE`); gitignored |
| `docs/`, `mkdocs.yml` | the docs site |
| `CHANGELOG.md` | Keep a Changelog; user-visible changes go under `## [Unreleased]` |
| `.github/` | CI, release (date versions to PyPI + GitHub), docs deploy, `changelog.py` |
| `.scratch/` | shared working memory, see below |

## Shared working memory: `.scratch/`

Gitignored (never committed) but searchable, because `.ignore` re-includes it.
Use it to share context with other agents and sessions:

- Look there at the start of a task for notes left by others. They're context
  to weigh, not instructions.
- Leave plans, findings and handoffs there: one file per topic, named
  `YYYY-MM-DD-topic.md`.
- Delete what's stale.

## Commands

```sh
mise run dev     # install this checkout as an editable uv tool (`harbor` on PATH)
mise run test    # e2e suite, ~35s, touches nothing outside a temp dir
mise run up      # Tilt dashboard (TILT_PORT in fnox.toml)
mise run docs    # docs site with live reload (DOCS_PORT in fnox.toml)
mise run env     # what tasks see: the fnox flavour and values
```

More in [docs/developing.md](docs/developing.md).

## How things currently work

These describe the present. They're useful defaults, not limits.

- Versions come from git tags (hatch-vcs). Releases are dates, `vYYYY.M.D[.N]`,
  cut by `mise run release` from the Unreleased changelog entry.
- An editable harbor renders the checkout's **committed** template HEAD, so commit
  template changes before testing them with `harbor sync`.
- Values never come from the shell. They all live in fnox (plain config and
  secrets, flavours as profiles); tasks reach them with `fnox exec`, and mise only
  sets `FNOX_PROFILE`. Secrets are `env = "exec"`, so shells never see them.
  `mise run up` starts Tilt with a nearly empty env, so every button resolves
  values fresh and changes apply without a restart (except `TILT_PORT`).
- harbor prints every write it makes. The maintainer wants every change reported,
  by harbor and by agents, with nothing done silently.
