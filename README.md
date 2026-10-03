# harbor

[Copier](https://copier.readthedocs.io) template for **meta repos** — repos whose
job is to manage a set of other repos. Part of [The Helping Hand](https://github.com/kbhatiya999).

Any repo with a `mani.yaml` is a meta repo. This template scaffolds one with
[mani](https://manicli.com) for repo management, [mise](https://mise.jdx.dev) as
task runner, and [fnox](https://github.com/jdx/fnox) for secrets.

## Use

**Guided setup (recommended):**

Four prompts (slug, description, fnox, directory), then it installs what's
missing and scaffolds the repo. Pick whichever runtime you already have; all
three behave identically:

```sh
uvx harbor-meta                                  # Python (uv)
npx @kbhatiya999/harbor                          # Node
go run github.com/kbhatiya999/harbor@latest      # Go

# No runtime? One-liner downloads a pre-built binary:
bash <(curl -fsSL https://raw.githubusercontent.com/kbhatiya999/harbor/main/setup.sh)

# Windows PowerShell:
irm https://raw.githubusercontent.com/kbhatiya999/harbor/main/setup.ps1 | iex
```

The setup scripts auto-detect the runtime (`uvx` → `npx` → `go run` → binary download).

**Install permanently** (so `harbor` works anywhere):

```sh
uv tool install harbor-meta                      # Python
npm install -g @kbhatiya999/harbor               # Node
go install github.com/kbhatiya999/harbor@latest  # Go
```

**Manual setup:**

```sh
copier copy gh:kbhatiya999/harbor my-new-meta
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

## Releasing

Push a tag such as `v0.2.0`; `.github/workflows/release.yml` publishes the Go
binaries (GitHub release + Go module proxy), the PyPI package `harbor-meta`
and the npm package `@kbhatiya999/harbor`, all versioned from the tag. One-time
setup: add a PyPI trusted publisher for this repo/workflow (environment
`pypi`) and an `NPM_TOKEN` repo secret.
