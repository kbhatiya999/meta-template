# Meta repos and mani

## The problem

When you work on many repos, things drift:

- the same repo gets cloned twice, and you're not sure which copy is current;
- a local copy falls behind GitHub without you noticing;
- you create a repo, forget it, and create it again;
- commits go out under the wrong GitHub account.

harbor exists to stop all of that.

## What a meta repo is

A **meta repo** is a normal git repo whose job is to *list other repos*. The
list is a file called `mani.yaml`. The listed repos are cloned *inside* the meta
repo, but git ignores them, so the meta repo stores the list, not their code.

```yaml
projects:
  api:
    path: api
    url: https://github.com/kbhatiya999/api.git
```

A meta repo can list other meta repos, so you get a **tree**:

```text
~/repo/
  kbhatiya999-meta/        the root: one per GitHub account
    api/                   a repo, cloned once
    courses-meta/          a nested meta repo
      course-1/
```

## mani

[mani](https://manicli.com) reads `mani.yaml` and works with all the listed
repos at once.

| Command | Does |
|---------|------|
| `mani sync` | clone every listed repo that's missing |
| `mani run status --all` | run a task in every repo |
| `mani list projects` | show the list |

`mani sync` also keeps a block in `.gitignore`, between two `# mani #` lines,
listing the cloned repos so the meta repo doesn't commit them.

## What harbor adds on top

- **One root per account:** `~/repo/<account>-meta`.
- **One clone per repo:** harbor refuses to clone a repo that's already cloned
  anywhere under `~/repo`, and tells you where it is.
- **Visibility:** `harbor` shows every repo with changed, unpushed (`↑`) and
  behind (`↓`) counts.
- **Safety:** `harbor sync` never touches uncommitted work or resolves a conflict.

## Try it

```sh
harbor status --offline        # your tree, without fetching
cat ~/repo/*-meta/mani.yaml    # the lists
```

## In this repo

harbor is the CLI in `src/harbor/main.py`, and the meta repo template is in
`template/`. See [Concepts](../concepts.md) for the full picture.
