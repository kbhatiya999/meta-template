# Updating

harbor and the template are released together under one version, and each harbor
release renders the template tag with its own version. Updating is two commands:

```sh
uv tool upgrade harbor-meta
harbor sync
```

`harbor` tells you when a newer release is out, and marks every meta repo that's on
an older template.

!!! tip "Always run the latest"
    `uvx harbor-meta@latest` runs the newest release without installing it.

## What a template update touches

The template owns three files and updates them: `mise.toml`, `AGENTS.md`,
`CLAUDE.md`.

Everything else is **yours once created**. The template writes it once and never
changes it again:

- `mani.yaml`, which lists your repos
- `README.md`
- `.gitignore` and `.ignore` (harbor still maintains their `# mani #` block)
- `fnox.toml`, which holds your secrets

If a repo already had one of the template-owned files when it was adopted, that
file is recorded under `keep` in `.copier-answers.yml` and stays yours too. You
can add to `keep` yourself:

```yaml
# .copier-answers.yml
keep:
  - AGENTS.md
```

## When an update conflicts

If you edited a template-owned file in the same place the template changed it,
harbor rolls the update back and leaves the repo clean:

```text
z-meta/   ! template v2026.10.11 → v2026.10.12 conflicts with local edits; left as is (run copier update there)
```

The meta repo stays on its current template until you resolve it. Either move your
edit somewhere else in the file, add the file to `keep`, or run
`copier update` in that repo to merge by hand.

Meta repos with uncommitted changes are skipped until they're clean.
