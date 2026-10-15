# The template

harbor scaffolds meta repos from the [Copier](https://copier.readthedocs.io)
template in this repository. You can also use it on its own, without harbor.

## Questions

| Question | Default | Notes |
|----------|---------|-------|
| `github_slug` | none | `owner/repo` where the meta repo lives. `owner` and `repo_name` are derived from it |
| `description` | `<repo> meta repo` | free text |
| `use_fnox` | `true` | include [fnox](https://github.com/jdx/fnox) and its tasks |
| `keep` | `[]` | template-owned files that stay yours (see [Updating](updating.md#what-a-template-update-touches)) |

harbor answers these for you. It takes the slug from the account and name, and
`keep` from the files a repo already has.

## Generated files

```text
mani.yaml          the repos this meta repo holds, and cross-repo tasks
mise.toml          pinned tools (mani, tilt, fnox)
mise-tasks/        meta-level tasks and the shared toolkit (tilt:*, env), one script each
Tiltfile, tilt/    a Tilt dashboard with a button per task
fnox.toml          values and encrypted secrets (if use_fnox)
.gitignore         what isn't committed, plus the # mani # block
.ignore            what your editor doesn't search, plus the same block
AGENTS.md          instructions for coding agents working in the meta repo
CLAUDE.md          points Claude Code at AGENTS.md
README.md
.copier-answers.yml
```

## Tasks

Tasks that run **inside each repo** are mani tasks in `mani.yaml`. **Meta-level**
tasks are script files in `mise-tasks/`, and `mise run` wraps the mani ones so
you have one entry point.

| Task | Does |
|------|------|
| `mise run sync` | `mani sync` plus mirroring the `# mani #` block into `.ignore` |
| `mise run hello` | the mani `hello` task in every repo |
| `mise run status` | `git status --short` in every repo |
| `mise run pull` | `git pull --ff-only` in every repo |
| `mise run tasks` | lists the cross-repo tasks |
| `mise run secrets` / `secrets:check` | `fnox list` / `fnox check` (if use_fnox) |
| `mise run tilt:up` | every task as a button in a Tilt dashboard, on the repo's own port |
| `mise run env` | every value tasks see, and the file it comes from |

`mise-tasks/`, `Tiltfile` and `tilt/` are the shared developer toolkit, the
same one harbor's own repo uses ([Developing](developing.md)). Template updates
keep them current, so don't edit them in place: put the meta repo's own tasks in
`.mise/tasks/`, where a task with the same name overrides the toolkit's.

You can also run mani directly: `mani run status --all --parallel`,
`mani run pull --tags active`, `mani tui`.

## The two ignore files

`.gitignore` decides what isn't committed, and `.ignore` decides what your editor
doesn't search. They share the same body and the same `# mani #` block,
following the rule *what needn't be committed needn't be searchable*. `.ignore`
opens with `!*` / `!*/`, so the editor first re-includes everything git hid
before the shared body narrows it back down.

## Using it without harbor

```sh
copier copy gh:kbhatiya999/meta-template my-meta
cd my-meta
mise install
mise run sync
```

Pull later template releases with `copier update`. Copier picks the newest tag;
pin one with `--vcs-ref vYYYY.M.D`.
