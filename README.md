# meta-template

[Copier](https://copier.readthedocs.io) template for **meta repos** — repos whose
job is to manage a set of other repos.

Any repo with a `mani.yaml` is a meta repo. This template scaffolds one with
[mani](https://manicli.com) for repo management, [mise](https://mise.jdx.dev) as
task runner, and [fnox](https://github.com/jdx/fnox) for secrets.

## Use

```sh
copier copy gh:kbhatiya999/meta-template my-new-meta
cd my-new-meta
mise install
mise run sync
```

Pull later template changes into an existing meta repo:

```sh
copier update
```

## Questions

| Question | Default | Notes |
|----------|---------|-------|
| `github_slug` | — | `owner/repo` where this meta repo lives, e.g. `kbhatiya999/kn-courses-meta`. Validated against `owner/repo`. |
| `description` | `<repo> meta repo` | Free text. |
| `use_fnox` | `true` | Include fnox + its tasks. |

`owner` and `repo_name` are derived from `github_slug` (not asked). A meta repo
only needs to know where *it* lives — the repos it holds carry their own owners
in their per-project `url:` lines.

## What it generates

```
mani.yaml     sub-repo declarations
mise.toml     pinned tools + tasks (hello, sync, status, pull, secrets)
fnox.toml     encrypted secrets           (if use_fnox)
.gitignore    what isn't committed        + # mani # block
.ignore       what isn't editor-searchable + # mani # block
README.md
```

### The two ignore files

`.gitignore` and `.ignore` share the same body and the same `# mani #` block, on
the rule *what needn't be committed needn't be searchable*. `.ignore` prefixes
`!*` / `!*/` so the editor re-includes everything git hid before the shared body
narrows it back down.

`mani sync` only writes the block into `.gitignore`, so the generated `sync` task
wraps it and mirrors the block into `.ignore`.
