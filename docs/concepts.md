# Concepts

## Meta repo

A git repo whose `mani.yaml` lists other repos under `projects:`. The repos it
lists are cloned inside it and ignored by its git, so a meta repo records
*which* repos belong together without containing their code.

```yaml
projects:
  kbhatiya999-meta:
    path: .
    url: https://github.com/kbhatiya999/kbhatiya999-meta.git

  api:
    path: api
    url: https://github.com/kbhatiya999/api.git
```

A project whose folder has its own `mani.yaml` is a **nested meta repo**. You
can build on the root or on any meta repo in the tree.

## Root

Each GitHub account has exactly one root: `~/repo/<account>-meta`, the meta repo
at the top of that account's tree. Every repo you work on lives somewhere in a
root's tree. A repo that doesn't is listed under *Outside every root* until you
`harbor add` it.

The base folder (`~/repo`) is a package default that maintainers can change in
`src/harbor/main.py`. Users don't configure it, so every machine has the same
layout.

## One clone per repo

harbor compares remotes across every clone under `~/repo`, ignoring case,
`.git`, and the difference between https and ssh. Before anything is cloned or
created, it checks:

- every `mani.yaml` in every tree
- every git repo on disk under `~/repo`, inside or outside the trees
- GitHub itself, for `new` and `init`

If the repo already exists anywhere, harbor stops and tells you where it is.

## Accounts

Inside a root, every git and gh call uses that root's account token
(`gh auth token --user <account>`), whichever account is active in `gh`. If gh
isn't logged in as that account, harbor refuses to run. Git's credential helper
for github.com is forced to gh's for these calls, so a keychain entry for another
account can't be used by mistake.

`harbor init` also binds commit identity: a git `includeIf` for the root folder
loads `~/.config/harbor/<account>.gitconfig`, which holds the account's name and
email. If the email is private, it uses the GitHub noreply address.

## Adoption

A meta repo is **adopted** once the template has been applied to it. Its
`.copier-answers.yml` records which template version it's on and the answers it
was given. That file is how harbor remembers what it created, and it's what
makes [template updates](updating.md) possible.

`harbor adopt` applies the template to an existing meta repo without
overwriting your files. Any file the repo already has is kept.

## Safe sync

For every repo in the tree, `harbor sync`:

1. fetches
2. skips the repo if it has uncommitted changes
3. skips it if the branch has no upstream
4. rebases local commits onto the upstream if the repo is behind
5. aborts the rebase and leaves the repo exactly as it was if there's a conflict

Meta repos also get their own commits pushed (harbor's manifest changes and
template updates). Regular repos are never pushed.
