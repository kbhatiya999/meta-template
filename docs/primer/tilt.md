# Tilt

## What it is

[Tilt](https://tilt.dev) is a dashboard in your browser. Each thing it manages is
a **resource**, shown with its status and logs. In this project every task is a
resource, so every flow is one click away and you don't have to remember commands.

## What you need to know

**Start and stop it with mise:**

```sh
mise run tilt:up       # prints the dashboard URL
mise run tilt:down
```

**Two kinds of resources.**

| Kind | Example | Behaves |
|------|---------|---------|
| one-shot | `test`, `build` | runs, finishes, shows pass or fail |
| server | `docs:serve` | keeps running; restarted when its config changes |

**When a resource runs.** By default, when you click it. A task can also run by
itself when files change: `test` reruns when you edit code.

**The `Tiltfile` describes the resources.** It's written in Starlark, a small
Python-like language. Ours builds the buttons from mise's task list, so a new
task appears by itself. A task's file can add `#TILT` lines:

| Line | Means |
|------|-------|
| `#TILT serve` | a long-running server |
| `#TILT deps=src,tests` | also run when these change |
| `#TILT link=http://127.0.0.1:${DOCS_PORT}/` | a link on the resource |
| `#TILT hide` | no button |

**Tilt keeps the environment it starts with.** If you `export` something after
starting Tilt, Tilt never sees it. That's why this project keeps values in
[fnox](fnox.md), and starts Tilt with an almost empty environment: every button
reads values fresh from fnox when it runs.

**Each dashboard has a port** (`TILT_PORT`). Each repo has its own, so dashboards
of different projects can run side by side. Changing it needs `tilt:down`, then
`tilt:up`.

**Two dashboards for the same repo** start every server twice, and they fight
over ports. The **other tilts** resource turns red when that happens; its
**Stop another Tilt** button lets you pick one and stop it.

## Try it

```sh
mise run tilt:up                 # then open the URL it prints
mise run tilt get uiresource     # list resources from the terminal
mise run tilt:others             # other dashboards for this repo
mise run tilt:down
```

## In this repo

```text
Tiltfile                 includes the parts below
tilt/tasks.Tiltfile      a button for every mise task
tilt/others.Tiltfile     other dashboards, and the Stop button
tilt/uibutton.Tiltfile   Tilt's button helper, stored here so no download is needed
```

Everything Tilt does is also a plain `mise run <task>`, so nothing depends on it.
