# Git

## What it is

Git keeps the history of a folder of files. That folder is a **repository**
(repo). Every saved state of it is a **commit**.

## What you need to know

**The three places a change can be.**

1. **Working tree:** files as they are on disk now.
2. **Staged:** changes you picked for the next commit (`git add`).
3. **Committed:** saved in history (`git commit`).

Changes that aren't committed yet are **uncommitted**. Many tools here refuse
to touch a repo with uncommitted changes, so they can never lose your work.

**Branches are names for lines of history.** `main` is the usual default. You
work on a branch, then merge it into `main`.

**A remote is another copy of the repo**, usually on GitHub, named `origin`.

| Command | Does |
|---------|------|
| `git clone <url>` | copy a remote repo to your machine |
| `git fetch` | download new commits from the remote, without changing your files |
| `git pull` | fetch, then update your branch |
| `git push` | send your commits to the remote |
| `git rebase` | replay your local commits on top of newer ones |

**Ahead and behind.** If you have commits the remote doesn't, you're *ahead*
(unpushed). If the remote has commits you don't, you're *behind* (stale). harbor
shows these as `↑` and `↓`.

**A conflict** happens when your change and someone else's touch the same lines.
Git can't choose, so you must. harbor never resolves conflicts for you: it
leaves the repo exactly as it was and tells you.

**Tags are fixed names for one commit**, like `v2026.10.11.2`. Releases are tags.

**`.gitignore` lists files git should never track**, like build output or your
personal settings files.

**Your identity** (name and email on commits) comes from git config. Git can use
a different identity per folder with `includeIf`. harbor uses that so commits
under one GitHub account's tree always use that account's identity.

## Try it

```sh
git status                     # what changed
git log --oneline -5           # the last five commits
git branch --show-current      # which branch you're on
git remote -v                  # where origin points
git tag --sort=-creatordate | head -3
```

## In this repo

- Versions come from git tags (see [Releases](releases-and-changelog.md)).
- harbor's main promise is about git: every repo cloned once, never a second copy.
- `harbor sync` fetches, and rebases only branches with no uncommitted work.
