# Terminal and shell

## What it is

The **terminal** is the window where you type commands. The **shell** is the
program inside it that reads your commands and runs them. On a Mac the shell is
usually `zsh`. Our scripts use `bash` or `sh`, which work almost the same.

## What you need to know

**A command is a program plus arguments.**

```sh
git status --short
```

`git` is the program. `status` and `--short` are arguments that tell it what to do.

**`PATH` decides which program runs.** When you type `git`, the shell looks
through a list of folders, in order, and runs the first `git` it finds. That
list is the `PATH` environment variable.

```sh
echo "$PATH"          # the folders, separated by ':'
which git             # the git that will run
```

Tools like mise add their own folders to `PATH`. That's how `mise` can give
every project its own tool versions.

**Environment variables are settings a program inherits.** Every program starts
with a copy of its parent's variables, and can't change the parent's copy.

```sh
export GREETING=hello     # set it for this shell and everything it starts
sh -c 'echo $GREETING'    # a child program sees it: hello
```

The catch: a long-running program keeps the copy it started with. If you change
a variable later, it never sees the change. This is why this project keeps
values in files, not in `export` lines (see [fnox](fnox.md) and [Tilt](tilt.md)).

**A script is a file of commands.** Its first line, the *shebang*, says which
program runs it:

```bash
#!/usr/bin/env bash
echo "hello from a script"
```

To run it by its name, it must be *executable*: `chmod +x myscript`.

**Every command ends with an exit code.** `0` means success; anything else means
failure. Scripts and tools use it to decide what to do next.

```sh
true;  echo $?   # 0
false; echo $?   # 1
```

## Lines you'll see at the top of our scripts

| Line | Means |
|------|-------|
| `#!/usr/bin/env bash` | run this file with bash |
| `set -e` | stop at the first command that fails |
| `set -u` | treat a missing variable as an error, not as empty |
| `set -o pipefail` | in `a \| b`, fail if `a` fails, not only if `b` fails |
| `exec some-command` | replace this script with `some-command` (it keeps the same process) |
| `"$@"` | all the arguments the script was given, unchanged |

## Try it

```sh
which mise uv git
echo "$SHELL"
env | sort | head        # some of your environment variables
```

## In this repo

- Every task is a small executable script in `mise-tasks/` or `.mise/tasks/`.
- Scripts start with `set -euo pipefail` so a failure stops them early.
- Tasks read settings from files at the moment they run, never from what you
  exported earlier.
