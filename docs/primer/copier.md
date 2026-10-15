# Copier

## What it is

[Copier](https://copier.readthedocs.io) makes new projects from a **template**:
a folder of files with blanks to fill in. It asks a few questions, fills the
blanks, and writes the result. Later, it can bring template improvements into
projects it already made. harbor uses Copier to create and update meta repos.

## What you need to know

**The template is the `template/` folder.** Files ending in `.jinja` have blanks
like `{{ repo_name }}`; Copier fills them in and drops the `.jinja`. Other files
are copied as they are.

**Questions live in `copier.yml`**, for example `github_slug` (`owner/repo`) and
`use_fnox`.

**Answers are remembered** in `.copier-answers.yml` in the new project, along
with the template version it was made from (`_commit`). That file is how harbor
knows a meta repo is "adopted", and which version it's on.

| Command | Does |
|---------|------|
| `copier copy <template> <dir>` | create a project |
| `copier update` | bring in a newer template version |

**Updates merge with your edits.** Copier compares old template, new template
and your file. If you changed the same lines the template changed, that's a
conflict. harbor then rolls the update back and tells you.

**Template versions are git tags.** Copier uses the newest tag unless told
otherwise (`--vcs-ref`). A released harbor renders the tag with its own version.

**Some files are yours once created.** `copier.yml`'s `_skip_if_exists` lists
them (`mani.yaml`, `README.md`, `fnox.toml`, ...): Copier writes them once and
never again. The rest (`mise-tasks/`, `Tiltfile`, `tilt/`, `AGENTS.md`, ...) stay
template-managed and get updates. A repo can keep one of those as its own with
the `keep` answer.

## Try it

```sh
copier copy --vcs-ref HEAD ~/repo/meta-template /tmp/try-meta   # a throwaway meta repo
cat /tmp/try-meta/.copier-answers.yml
```

## In this repo

- `harbor new` and `harbor adopt` run `copier copy`; `harbor sync` runs
  `copier update` for meta repos on an older template.
- An editable harbor (`mise run dev`) renders your checkout's **committed**
  template, so commit a template change before trying it with `harbor sync`.
