# Troubleshooting

## `gh isn't logged in as <account>`

The root belongs to an account that `gh` has no token for. Log in to that account:

```sh
gh auth login
```

harbor uses that account's token inside its root even if another account is
active, so you don't need to `gh auth switch`.

## `push failed` / HTTP 403 on push

The GitHub repo is usually archived (read-only). Check:

```sh
gh repo view <owner>/<repo> --json isArchived
```

Unarchive it with `gh repo unarchive <owner>/<repo>` if you mean to keep using
it, then run `harbor sync` to push.

## `already cloned at …`

That repo is already cloned somewhere under `~/repo`, so harbor won't make a second
copy. Move the existing clone into the tree:

```sh
harbor add <path printed in the message>
```

## `already tracked at …` / `already exists on GitHub`

The repo or meta repo exists already. Use the existing one: `harbor add owner/repo`
for a GitHub repo that isn't in your tree yet.

## `conflicts with upstream, left untouched`

Your local commits and the upstream changed the same lines. harbor aborted the
rebase, so the repo is exactly as it was. Resolve it yourself:

```sh
cd <repo>
git pull --rebase
```

## `template … conflicts with local edits; left as is`

See [When an update conflicts](updating.md#when-an-update-conflicts).

## `skipped: N uncommitted change(s)`

harbor never rebases over uncommitted work. Commit or stash, then
`harbor sync` again.

## `has uncommitted changes; commit or stash them, then adopt`

`harbor adopt` makes a commit, so it won't adopt a repo that has uncommitted
changes, which could otherwise be swept into that commit.

## A repo shows under *Outside every root*

It's a clone under `~/repo` that isn't in any tree. `harbor add <path>` moves it
into the current meta repo. If it shows up under *Duplicates* too, keep the one in
the tree and delete the other once it's *clean* with nothing unpushed.
