# mise

## What it is

[mise](https://mise.jdx.dev) does two jobs:

1. **Tools:** it installs the exact tool versions a project needs (uv, tilt,
   fnox, ...) and puts them on `PATH` when you're in that project.
2. **Tasks:** it runs the project's tasks, like `mise run test`.

## What you need to know

**`mise.toml` lists the tools.**

```toml
[tools]
uv = "latest"
tilt = "latest"
```

`mise install` installs them. Inside the project, `uv` and `tilt` then mean
these versions.

**mise asks before trusting a config.** A config file can run commands, so the
first time you use a project, run `mise trust`.

**Tasks are script files, one per task.** mise finds them in task folders. The
file's path is the task's name:

| File | Task |
|------|------|
| `.mise/tasks/dev` | `mise run dev` |
| `.mise/tasks/docs/serve` | `mise run docs:serve` |
| `.mise/tasks/build/_default` | `mise run build` |

The comments at the top of a task set its options:

```bash
#!/usr/bin/env bash
#MISE description="Build the docs"
exec uv run --only-group docs mkdocs build --strict
```

To add a task: create the file and make it executable (`chmod +x`).

**Two task folders, one list.** mise loads both:

| Folder | Holds |
|--------|-------|
| `mise-tasks/` | the shared toolkit (`tilt:*`, `env`), from the template |
| `.mise/tasks/` | this repo's own tasks; the same name here wins |

**Local files are just for you.** `mise.local.toml` is gitignored. Use it for
settings on your machine only, like which fnox flavour to use:

```toml
[env]
FNOX_PROFILE = "scratch"
```

**Secrets for one task.** mise can hand a secret from [fnox](fnox.md) to a
single task and hide it in that task's output:

```bash
#MISE secrets=["DEPLOY_TOKEN"]
```

A trap to know: mise's `sources` option makes mise *skip* a task when its
files haven't changed. Don't use it to mean "run when these change". Our Tilt
setup uses its own `#TILT deps=` line for that.

## Try it

```sh
mise tasks                 # every task, with descriptions
mise run env               # what tasks see from fnox
mise tasks info test       # where a task is defined
```

## In this repo

`mise.toml` holds tools and settings only. All tasks are scripts, so nothing
grows into one big file, and Tilt builds a button for each one.
