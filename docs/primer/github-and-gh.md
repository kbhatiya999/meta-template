# GitHub and gh

## What it is

**GitHub** hosts git repos online. **`gh`** is GitHub's command-line tool: it
lets you do on the terminal what you'd otherwise do on the website.

## What you need to know

**Repos have an owner.** `kbhatiya999/meta-template` means the repo
`meta-template` owned by the account `kbhatiya999`. This `owner/repo` form is
called a *slug*.

**`gh` can be logged in to several accounts.** One of them is *active*, but
programs can ask for any logged-in account's token.

```sh
gh auth status            # which accounts are logged in, which is active
gh auth login             # log in to another account
```

harbor uses this: inside `~/repo/<account>-meta`, it always uses *that*
account's token, whichever account is active.

**A token is a password for programs.** Never paste one into a file, a chat or a
URL. Let `gh` keep it.

**A pull request (PR)** asks to merge one branch into another. People review it,
CI checks it, then someone merges it.

**GitHub Actions** run *workflows*: scripts that run on GitHub's machines when
something happens, like a push or a PR. They live in `.github/workflows/`.

**GitHub Pages** hosts a website from a repo. Our docs site lives there.

**Archived repos are read-only.** Pushing to one fails with error 403.

## Try it

```sh
gh repo view kbhatiya999/meta-template
gh pr list
gh run list --limit 3      # recent workflow runs
```

## In this repo

| Workflow | Runs when | Does |
|----------|-----------|------|
| `ci.yml` | every push and PR | tests, package build, docs build |
| `release.yml` | you start it (`mise run release`) | publishes a new version |
| `docs.yml` | push to `main`, after a release | rebuilds the docs site |
