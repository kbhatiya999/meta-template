# Releasing

For maintainers. harbor (the `harbor-meta` package) and the template are released
together under one version.

## Versions

Versions are dates: `YYYY.M.D` (UTC), with `.1`, `.2` … for further releases the
same day. They always increase, and they sort above the earlier semantic-version
template tags (`v1.0.0` … `v2.0.0`). Git tags carry a `v` prefix.

## Cutting a release

1. Describe the changes under `## [Unreleased]` in `CHANGELOG.md`, using
   [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) sections (`Added`,
   `Changed`, `Fixed`, `Removed`). Push to `main`.
2. Run:

    ```sh
    mise run release
    ```

    This checks that everything is committed and pushed, starts the release workflow
    (`gh workflow run release.yml`), waits for it, then pulls the release commit and
    refreshes your editable install, so you end up on the version you just released.

The workflow:

1. picks the next date version
2. moves the Unreleased entry under that version in `CHANGELOG.md` (it refuses to release if the entry is empty)
3. builds `harbor-meta` with that version and **publishes it to PyPI**
4. only then commits the changelog, tags `vX`, and creates the GitHub release, with the
   changelog entry, install instructions and the built files

If publishing fails, nothing is tagged or committed, so the version isn't used up.
The docs site rebuilds after every release and on every push to `main`.

## One-time setup

- **PyPI:** a trusted publisher for `harbor-meta`: owner `kbhatiya999`, repository
  `meta-template`, workflow `release.yml`, environment `pypi`.
- **GitHub Pages:** Settings → Pages → Source: *GitHub Actions*.

## Previewing the docs

```sh
mise run docs
```

## Maintainer defaults

The base folder (`~/repo`) and the template source are constants at the top of
`src/harbor/main.py`. `HARBOR_BASE`, `HARBOR_TEMPLATE` and `HARBOR_TEMPLATE_REF`
override them for testing.
