# harbor

Keep every repo you work on in **one tree per GitHub account, cloned exactly once**,
so you always know what exists, where it lives, and whether it's safe to work on.
Part of [The Helping Hand](https://github.com/kbhatiya999).

```
~/repo/
  kbhatiya999-meta/          root meta repo for the kbhatiya999 account
    mani.yaml                what this meta repo holds
    some-repo/               the only clone of some-repo
    courses-meta/            a nested meta repo
      mani.yaml
      another-repo/
```

A meta repo is any repo with a `mani.yaml`. harbor scaffolds and adopts them with
this [Copier](https://copier.readthedocs.io) template, and the generated repos use
[mani](https://manicli.com), [mise](https://mise.jdx.dev) and
[fnox](https://github.com/jdx/fnox).

## Use

```sh
uvx harbor-meta            # status: everything you have, run with no install
uv tool install harbor-meta   # or install it, then just: harbor
```

| Command | Does |
|---------|------|
| `harbor` | Fetches, then shows every meta repo and clone: changed / ↑unpushed / ↓behind, not cloned yet, not adopted, clones outside every root, duplicates |
| `harbor init [account]` | Sets up the account's root `~/repo/<account>-meta`: adopts it if it's there, clones it if it's only on GitHub, creates it otherwise. Binds commit identity for the whole tree |
| `harbor sync` | Clones what's missing, fetches everything, rebases branches that have nothing uncommitted, pushes meta repos' own manifest commits. Never touches dirty or conflicting repos |
| `harbor add <owner/repo \| url \| path>` | Adds a repo to the current meta repo. A path to an existing clone is **moved** in, so there's still one copy |
| `harbor new <name>` | Creates a nested meta repo (GitHub + local) |
| `harbor adopt [path]` | Runs the template over an existing meta repo, keeping your files |

`add`, `new` and `sync` act on the meta repo you're in (`--in <path>` to pick
another); outside every root they use the active gh account's root.

**What harbor refuses to do:**
- clone a repo that's already cloned anywhere under `~/repo` (it tells you where, and how to move it in)
- create a repo or meta repo that already exists, locally or on GitHub
- rebase over uncommitted work or through a conflict

**One account per root.** Inside `~/repo/<account>-meta`, every git and gh call
runs with that account's gh token, whichever gh account is active, and refuses if
gh isn't logged in as it. `harbor init` also adds a git `includeIf` to
`~/.gitconfig` so commits anywhere in the tree use that account's name and email.

Maintainers can change the base folder (`~/repo`) and the template at the top of
`src/harbor/main.py`.

**Manual setup:**

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

## Updating

harbor and the template are released together with date versions (`vYYYY.M.D`,
`.1`, `.2` … for more releases that day), and each harbor release renders the
template at its own version. So there is one thing to update:

```sh
uv tool upgrade harbor-meta   # or always run the latest: uvx harbor-meta@latest
harbor sync                   # moves every clean meta repo to the new template
```

`harbor` tells you when a newer harbor is out and which meta repos are on an
older template.

Updates only touch files the template owns: `mise.toml`, `AGENTS.md` and
`CLAUDE.md`. `mani.yaml`, `README.md`, `.gitignore`, `.ignore` and `fnox.toml`
are yours once created, and so is any template-owned file a repo already had
when `harbor adopt` took it over (recorded as `keep` in `.copier-answers.yml`). A template update that conflicts with your edits is rolled back
and reported, never left half-applied.

## Releasing

```sh
gh workflow run release.yml
```

Tags today's date version, creates the GitHub release and publishes
`harbor-meta` to PyPI. One-time setup: add this repo and workflow (environment
`pypi`) as a trusted publisher on PyPI.
