# fnox

## What it is

[fnox](https://fnox.jdx.dev) keeps a project's **values** (like ports) and
**secrets** (like tokens) in files, and hands them to commands when they run.
Secrets stay encrypted or in a password store; the file only says where they are.

## What you need to know

**Values live in `fnox.toml`.** A plain value has a `default`:

```toml
[secrets]
DOCS_PORT = { default = "8361" }
```

(fnox calls every entry a "secret", even plain ones.)

**A real secret is stored through a provider**, never as plain text. On a Mac,
the Keychain is the simplest provider:

```sh
fnox provider add keychain keychain      # once
fnox set API_TOKEN --provider keychain   # asks for the value
```

`fnox.toml` then holds only a reference, so it's safe to commit.

**Commands get values when they run.**

| Command | Does |
|---------|------|
| `fnox get DOCS_PORT` | print one value |
| `fnox exec -- <cmd>` | run a command with all values as environment variables |
| `fnox list --sources` | every key, and the file it comes from |

Because values are read at the moment a command runs, a change applies on the
next run. Nothing needs restarting.

**`env = "exec"` keeps secrets out of shells.** Mark every secret with it:
commands run through `fnox exec` get it, but your shell and `fnox export` never
do.

**Files merge, in this order** (later ones win):

1. your global config, `~/.config/fnox/config.toml`
2. `fnox.toml` files in parent folders
3. this folder's `fnox.toml`, plus the files it `import`s
4. `fnox.local.toml`: your machine's overrides, gitignored

So a secret in your root meta repo reaches every repo under it.

**Profiles are flavours**: a set of values that replaces the defaults.

```toml
[profiles.scratch.secrets]
HARBOR_BASE = { default = "~/harbor-scratch" }
```

You pick a profile with `FNOX_PROFILE`, which this project sets in
`mise.local.toml`.

## Try it

```sh
mise run env                 # every value tasks see, and where it comes from
fnox list --sources
fnox get TILT_PORT
```

## In this repo

| File | Holds |
|------|-------|
| `fnox.toml` | imports the files below, and profiles |
| `fnox/config.toml` | plain values: `TILT_PORT`, `DOCS_PORT` |
| `fnox/secrets.toml` | secrets, all `env = "exec"` |
| `fnox.local.toml` | your overrides (not committed) |
