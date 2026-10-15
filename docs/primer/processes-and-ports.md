# Processes and ports

## What it is

A **process** is a running program. A **port** is a numbered door on your
machine that a process can listen on, so a browser or another program can talk
to it. `http://localhost:8361` means "port 8361 on this machine".

## What you need to know

**Every process has a PID**, a number that identifies it, and a *parent*: the
process that started it. When you stop a parent, its children usually stop too.

**Every process has a working directory**: the folder it was started in. This
repo uses it to tell which Tilt dashboards belong to which project.

**Only one process can listen on a port at a time.** A second one fails with:

```text
OSError: [Errno 48] Address already in use
```

That's what happens when two Tilt dashboards for the same repo both start a docs
server on the same port.

| Command | Does |
|---------|------|
| `lsof -i :8361` | which process listens on port 8361 |
| `pgrep -fl tilt` | running processes whose command mentions "tilt" |
| `ps -o pid,command -p <pid>` | what a PID is running |
| `kill <pid>` | ask a process to stop (it can clean up first) |

`kill` sends a polite stop signal. Prefer it to `kill -9`, which stops a process
without letting it clean up.

## Try it

```sh
lsof -nP -iTCP -sTCP:LISTEN | head     # everything listening on a port
pgrep -fl "tilt up"                    # running Tilt dashboards
```

## In this repo

- Each repo has its own `TILT_PORT` and `DOCS_PORT`, so projects don't collide.
- `mise run tilt:others` finds Tilt dashboards for this repo by their working
  directory, not their port, so a changed port can't hide one.
- `mise run tilt:stop <pid>` stops one, and checks first that the PID really is a
  Tilt for this repo.
