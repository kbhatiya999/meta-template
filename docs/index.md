# harbor

**One tree of meta repos per GitHub account, with every repo cloned exactly once.**

When you work across many repos, things drift. The same repo ends up cloned in
two folders and you're not sure which one is current. A local copy falls behind
GitHub without you noticing. You create a repo and forget it exists, then create
it again. Commits go out under the wrong GitHub account.

harbor keeps all of it in one place you can see:

```text
~/repo/
  kbhatiya999-meta/            root meta repo for the kbhatiya999 account
    mani.yaml                  what this meta repo holds
    api/                       the only clone of api
    web/
    courses-meta/              a nested meta repo
      mani.yaml
      course-1/
```

![harbor status: every repo in the tree with changed, unpushed and behind counts, a repo not cloned yet, clones outside the tree, and a duplicate clone](assets/harbor-status.svg)

## What harbor guarantees

- **One clone per repo.** harbor won't clone a repo that's already cloned anywhere
  under `~/repo`. It shows you where the existing copy is and how to move it into the tree.
- **No accidental duplicates.** `harbor new` and `harbor add` refuse anything that
  already exists, locally or on GitHub.
- **You can see what's stale.** `harbor` fetches first, then shows what's changed, unpushed or
  behind for every repo.
- **Your work is never overwritten.** `harbor sync` only rebases branches with no uncommitted
  work, and leaves anything that conflicts exactly as it was.
- **One account per root.** Everything inside `~/repo/<account>-meta` runs as that
  GitHub account, and commits use its identity.
- **Every change is reported.** Every clone, move, commit, push and config change prints
  a line, so nothing happens without you knowing.

## Quick start

```sh
uv tool install harbor-meta
harbor init      # set up or adopt ~/repo/<your-account>-meta
harbor sync      # clone what's missing, bring everything up to date
harbor           # see everything
```

Continue with [Getting started](getting-started.md).

Working on harbor itself? Start with the [Primer](primer/index.md): one short
page per tool this project is built on, in reading order.

## How it fits together

A **meta repo** is a git repo with a `mani.yaml` listing other repos. harbor uses
[mani](https://manicli.com) manifests, scaffolds and updates meta repos with
[Copier](https://copier.readthedocs.io), and the generated repos come with
[mise](https://mise.jdx.dev) tasks and optional [fnox](https://github.com/jdx/fnox)
secrets.
