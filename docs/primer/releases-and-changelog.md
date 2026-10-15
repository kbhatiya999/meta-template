# Releases and the changelog

## What it is

A **release** publishes a new version of harbor (to PyPI) and of the template
(a git tag), together, under one version number. The **changelog**,
`CHANGELOG.md`, says what changed in each version, for people.

## What you need to know

**Versions are dates.** `2026.10.11` is a release made on 11 October 2026. A
second release that day is `2026.10.11.1`, then `.2`. Dates always go up, so
newer is always bigger. Git tags add a `v`: `v2026.10.11.2`.

**The changelog has an "Unreleased" section** at the top. While you work, add
one line per user-visible change there, under a heading:

```markdown
## [Unreleased]

### Added
- `harbor foo`: does the thing.

### Fixed
- `harbor sync` no longer ...
```

Headings: `Added`, `Changed`, `Fixed`, `Removed`. The format is
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

**A release turns "Unreleased" into a version.** The release refuses to run if
"Unreleased" is empty. Its notes on GitHub are that section, plus install steps.

**Publish first, tag after.** The release workflow publishes to PyPI first, and
only then commits the changelog, creates the tag and the GitHub release. If
publishing fails, nothing is tagged, so no version number is wasted.

**Meta repos update after a release.** Once a new version is out, users run
`uv tool upgrade harbor-meta`, then `harbor sync` brings their meta repos onto
the new template.

## Try it

```sh
sed -n '/## \[Unreleased\]/,/^## \[2/p' CHANGELOG.md    # what's waiting to be released
gh release list --limit 3
```

## In this repo

1. Describe your changes under `## [Unreleased]`, commit, push to `main`.
2. Rehearse if you like: `mise run release:dry-run` (needs Docker).
3. Release: `mise run release`. It waits for the workflow, then updates your
   install to the new version.

See [Releasing](../releasing.md) for the details.
