# uv and Python packaging

## What it is

harbor is a Python program. [uv](https://docs.astral.sh/uv/) installs Python
programs and their dependencies, fast. **PyPI** is the public store where
Python packages live; harbor is published there as `harbor-meta`.

## What you need to know

**A package can install commands.** The package `harbor-meta` installs the
commands `harbor` and `harbor-meta`. (The name `harbor` was taken on PyPI.)

| Command | Does |
|---------|------|
| `uvx harbor-meta` | run the latest harbor once, without installing it |
| `uv tool install harbor-meta` | install it, so `harbor` works everywhere |
| `uv tool upgrade harbor-meta` | get the newest release |
| `uv tool list` | what's installed |

**A virtual environment (`.venv`)** is a private folder of packages for one
project, so projects don't break each other.

**An editable install** points at your source folder instead of a copy, so your
code changes apply immediately. That's what `mise run dev` does: it installs
your checkout as a tool, so you use your own changes every day.

**`pyproject.toml` describes the package**: its name, dependencies, and how to
build it.

**The version comes from git tags.** We use `hatch-vcs`:

| Your checkout | Version |
|---------------|---------|
| exactly on tag `v2026.10.11.2` | `2026.10.11.2` |
| two commits later | `2026.10.11.2.post1.dev2+g<hash>` |

So the version always tells you which release you're building on.

**Trusted publishing:** GitHub proves to PyPI that a release really comes from
our release workflow, so no PyPI password or token is stored anywhere.

## Try it

```sh
harbor --version          # your version, and which template it renders
uv tool list              # installed tools
```

## In this repo

- `mise run dev` installs your checkout (editable).
- `mise run build` builds the package and checks it the way PyPI would.
- Releases are built and published by `.github/workflows/release.yml`.
