# harbor

[![PyPI](https://img.shields.io/pypi/v/harbor-meta)](https://pypi.org/project/harbor-meta/)
[![Docs](https://img.shields.io/badge/docs-kbhatiya999.github.io-indigo)](https://kbhatiya999.github.io/meta-template/)
[![Release](https://github.com/kbhatiya999/meta-template/actions/workflows/release.yml/badge.svg)](https://github.com/kbhatiya999/meta-template/actions/workflows/release.yml)

**One tree of meta repos per GitHub account, with every repo cloned exactly once.**
Part of [The Helping Hand](https://github.com/kbhatiya999).

When you work across many repos, things drift. The same repo ends up cloned in two
folders, local copies fall behind GitHub, repos you created get forgotten and
created again, and commits go out under the wrong account. harbor keeps
all of it in one tree you can see:

```text
~/repo/
  kbhatiya999-meta/          root meta repo for the kbhatiya999 account
    mani.yaml                what this meta repo holds
    api/                     the only clone of api
    courses-meta/            a nested meta repo
      mani.yaml
      course-1/
```

![harbor status: every repo with changed, unpushed and behind counts, clones outside the tree, and duplicates](https://raw.githubusercontent.com/kbhatiya999/meta-template/main/docs/assets/harbor-status.svg)

## Install

```sh
uv tool install harbor-meta     # or run without installing: uvx harbor-meta
```

## Use

```sh
harbor init      # set up or adopt ~/repo/<account>-meta
harbor sync      # clone what's missing, rebase what's safe to rebase
harbor           # everything you have: changed / unpushed / behind, strays, duplicates
harbor add ~/code/api          # move an existing clone into the tree
harbor add owner/repo          # or clone one from GitHub
harbor new courses-meta        # create a nested meta repo
```

harbor refuses to clone a repo that's already cloned anywhere under `~/repo`, or
to create one that already exists locally or on GitHub. It never rebases over
uncommitted work. Inside a root, every git and gh call runs as that root's
account, and every change it makes is printed.

## Documentation

**<https://kbhatiya999.github.io/meta-template/>**:
[getting started](https://kbhatiya999.github.io/meta-template/getting-started/),
[concepts](https://kbhatiya999.github.io/meta-template/concepts/),
[commands](https://kbhatiya999.github.io/meta-template/commands/),
[updating](https://kbhatiya999.github.io/meta-template/updating/),
[the template](https://kbhatiya999.github.io/meta-template/template/),
[troubleshooting](https://kbhatiya999.github.io/meta-template/troubleshooting/).

Release history: [CHANGELOG.md](https://github.com/kbhatiya999/meta-template/blob/main/CHANGELOG.md).

## The template on its own

harbor scaffolds meta repos from the [Copier](https://copier.readthedocs.io)
template in this repository, which uses [mani](https://manicli.com),
[mise](https://mise.jdx.dev) and [fnox](https://github.com/jdx/fnox). It works
without harbor too:

```sh
copier copy gh:kbhatiya999/meta-template my-meta
```

## Contributing

```sh
mise run tilt:up  # every task as a button (Tilt dashboard)
mise run dev      # install your checkout as an editable uv tool
mise run test     # end-to-end tests, offline
mise run release  # publish the next version from CHANGELOG.md
```

See [Developing](https://kbhatiya999.github.io/meta-template/developing/) and
[Releasing](https://kbhatiya999.github.io/meta-template/releasing/).

## License

[MIT](https://github.com/kbhatiya999/meta-template/blob/main/LICENSE)
