# Changelog

All notable changes to harbor and the meta-repo template. harbor and the
template are released together, so one version covers both.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions are dates (`YYYY.M.D`, with `.1`, `.2` … for further releases the same
day) from 2026.10.11 on; earlier template-only releases used semantic versions.

## [Unreleased]

### Added

- **Developer toolkit for meta repos and this repo alike.** Generated meta repos get
  `mise-tasks/` (their tasks plus the toolkit), a `Tiltfile` and `tilt/`, kept current
  by template updates; a repo's own tasks go in `.mise/tasks/`, where the same name
  overrides the toolkit's. harbor's own repo uses the same files.
- Tasks are script files, one per task, named by their path (`docs/serve` is
  `docs:serve`), so no config file grows with the task list.
- `mise run tilt:up`: a Tilt dashboard with a button for every task, generated from
  mise's task list. `#TILT serve`, `#TILT deps=…`, `#TILT link=…` and `#TILT hide` in a
  task's file set how Tilt runs it. Each repo gets its own ports (from fnox, else
  derived from the repo path), so dashboards of different projects run side by side.
- A second dashboard for the same repo, from any terminal or port, shows up red under
  "other tilts", with a button to pick one and stop it (`tilt:others`, `tilt:stop`).
- Values and secrets in fnox, split into `fnox/config.toml` and `fnox/secrets.toml`;
  per-machine overrides in `fnox.local.toml`; flavours as fnox profiles picked with
  `FNOX_PROFILE` in `mise.local.toml`. Tasks read them fresh on every run and Tilt
  starts with a nearly empty environment, so changes apply without restarting it.
  Secrets are `env = "exec"`, so shells never see them; `mise run examples:secret`
  shows a per-task, redacted grant through mise's fnox integration.
- `mise run env`: every value tasks see, with the file it comes from (global fnox
  config included).
- `mise run dev` installs a checkout as an editable uv tool: the same package and
  commands users get, running the checkout's code. An editable harbor renders the
  checkout's committed template, so `harbor sync` brings your own meta repos onto it.
- `mise run test`: end-to-end tests in an offline sandbox with a fake `gh` and local
  bare repos standing in for GitHub; each run is isolated, and a failing check shows
  the output it checked.
- CI workflow: tests, package build and docs build on every push and pull request.
- `mise run ci:local` and `mise run release:dry-run` run the GitHub workflows locally in
  Docker with act; they stop with a hint when Docker/Colima isn't running.
- Release workflow `dry_run` input. Runs under act are always dry runs.
- A [Developing](https://kbhatiya999.github.io/meta-template/developing/) guide, and a
  [Primer](https://kbhatiya999.github.io/meta-template/primer/): one short page per
  tool and idea you need before working on this repo, in reading order.

### Changed

- **Meta repos:** tasks moved from `mise.toml` to `mise-tasks/`; `check-secrets` is now
  `secrets:check`. `harbor adopt` keeps a meta repo's existing `Tiltfile`,
  `mise-tasks/` or `tilt/` as its own.
- The package version comes from git tags (hatch-vcs): a release is `2026.10.11.2`,
  and a build after it is `2026.10.11.2.postN.devM+g<hash>`.

### Fixed

- A template update that copier can't apply is rolled back and reported, instead of
  stopping `harbor sync` with an error.
- Paths under a home folder reached through a symlink are shown as `~/…`.

## [2026.10.11.2] - 2026-10-11

### Added

- Documentation site at <https://kbhatiya999.github.io/meta-template/>, with screenshots
  of real harbor output, and this changelog.
- MIT license.
- PyPI project page: description, documentation and changelog links, keywords.
- `harbor-meta` command alias, so `uvx harbor-meta` works without `--from`.
- Release notes contain the changelog entry plus install and upgrade instructions.

### Changed

- Releases publish to PyPI before tagging, so a failed publish no longer uses up a
  version, and a release is refused unless this changelog has an Unreleased entry.

## [2026.10.11.1] - 2026-10-11

First release published to PyPI as `harbor-meta`.

### Fixed

- `harbor adopt` refuses a meta repo with uncommitted changes instead of committing them
  along with the adoption.
- Development builds no longer report that a newer release is available.

## [2026.10.11] - 2026-10-11

harbor rebuilt around one tree of meta repos per GitHub account, with every repo
cloned exactly once. Not published to PyPI.

### Added

- `harbor` (status): every meta repo and clone, with uncommitted, unpushed and behind
  counts; repos not cloned yet; meta repos not adopted or on an older template; clones
  outside every root; duplicate clones.
- `harbor init`: sets up the account root `~/repo/<account>-meta` by adopting, cloning
  or creating it, and binds commit identity for the tree with a git `includeIf`.
- `harbor sync`: clones missing repos, fetches everything, rebases branches with no
  uncommitted work, pushes meta repos' own commits and applies template updates.
- `harbor add` and `harbor new`: refuse anything that already exists locally or on
  GitHub; `harbor add <path>` moves an existing clone into the tree.
- `harbor adopt`: brings an existing meta repo under the template, keeping its files.
- Every git and gh call inside a root runs as that root's account.
- Template: `AGENTS.md` and `CLAUDE.md` for coding agents.
- Template: `keep` question; template-managed files a repo already had stay its own.

### Changed

- **Breaking:** harbor is a Python CLI only; the Go and Node versions are removed, and
  the setup scripts run `uvx harbor-meta`.
- Template: `mani.yaml`, `README.md`, `.gitignore`, `.ignore` and `fnox.toml` belong to
  the meta repo once created; template updates only touch `mise.toml`, `AGENTS.md` and
  `CLAUDE.md`.
- Date-based versions, released with `gh workflow run release.yml`; each harbor release
  renders the template tag with its own version.

## [2.0.0] - 2026-08-08

### Changed

- **Breaking:** a single `github_slug` question (`owner/repo`) replaces `github_user`
  and `repo_name`.

## [1.1.0] - 2026-07-31

### Changed

- Cross-repo tasks live in `mani.yaml` again; `mise.toml` holds meta-level tasks and
  thin wrappers.

### Fixed

- The `branch` task uses `git branch --show-current`, so it works on a repo with no
  commits yet.

## [1.0.1] - 2026-07-31

### Added

- Copier answers file, so `copier update` works.

## [1.0.0] - 2026-07-31

### Added

- Copier template for meta repos with mani, mise and fnox.

[Unreleased]: https://github.com/kbhatiya999/meta-template/compare/v2026.10.11.2...HEAD
[2026.10.11.2]: https://github.com/kbhatiya999/meta-template/compare/v2026.10.11.1...v2026.10.11.2
[2026.10.11.1]: https://github.com/kbhatiya999/meta-template/compare/v2026.10.11...v2026.10.11.1
[2026.10.11]: https://github.com/kbhatiya999/meta-template/compare/v2.0.0...v2026.10.11
[2.0.0]: https://github.com/kbhatiya999/meta-template/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/kbhatiya999/meta-template/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/kbhatiya999/meta-template/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/kbhatiya999/meta-template/releases/tag/v1.0.0
