# Primer

These pages explain the tools and ideas this project is built on. Read them
before you change anything. You don't need to be an expert: each page explains
one thing in simple words, shows a few safe commands to try, and says how this
repo uses it.

## Reading order

Start at the top. Each page builds on the ones before it.

| # | Page | You learn |
|---|------|-----------|
| 1 | [Terminal and shell](terminal-and-shell.md) | commands, `PATH`, environment variables, scripts |
| 2 | [Git](git.md) | repos, commits, branches, remotes, tags |
| 3 | [GitHub and gh](github-and-gh.md) | accounts, the `gh` command, pull requests, Actions |
| 4 | [Processes and ports](processes-and-ports.md) | what runs, who listens where, how to stop it |
| 5 | [Meta repos and mani](meta-repos-and-mani.md) | the problem harbor solves |
| 6 | [uv and Python packaging](uv-and-packaging.md) | how harbor is installed and versioned |
| 7 | [mise](mise.md) | tools and tasks |
| 8 | [fnox](fnox.md) | values and secrets |
| 9 | [Tilt](tilt.md) | the dashboard with a button per task |
| 10 | [Copier](copier.md) | the template that makes meta repos |
| 11 | [Docker, Colima and act](docker-and-act.md) | running GitHub workflows on your machine |
| 12 | [Releases and the changelog](releases-and-changelog.md) | how a new version goes out |

## Three ideas that run through everything

**1. One copy of everything.** Every repo is cloned once, every value is defined
once, every task is written once. When something exists twice, the two copies
drift apart and you stop trusting both. harbor exists because of this.

**2. Nothing happens silently.** Every tool here prints what it changed. If you
write a task or change harbor, keep it that way: say what you did.

**3. Values never come from your shell.** Settings and secrets live in files
(fnox), not in `export` lines you typed once and forgot. Then every task, every
button and every teammate sees the same thing.

## When you're done

Go to [Developing](../developing.md) to set up your machine, and read
`AGENTS.md` in the repo root: it describes how the project works today.
