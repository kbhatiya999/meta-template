# Docker, Colima and act

## What it is

- **Docker** runs programs in **containers**: small, isolated Linux systems.
- **Colima** runs Docker on a Mac.
- **act** runs GitHub Actions workflows inside Docker containers, so you can
  test a workflow on your machine before pushing.

You only need these to run the GitHub workflows locally. Everything else in this
project works without them.

## What you need to know

**Docker must be running first.**

```sh
colima start      # start Docker
colima status
colima stop       # when you're done, to free memory
```

**act uses your working copy**, uncommitted changes included, so you see what CI
would do with exactly what you have.

**act needs to know where Docker is.** Colima's Docker lives at a different
address than act expects; our tasks find it for you.

**The first run downloads a big image** (about 1 GB). `.actrc` picks the image so
act never stops to ask.

**A local release can never publish.** The release workflow skips publishing,
pushing and creating the GitHub release whenever it runs under act.

## Try it

```sh
colima start
mise run ci:local            # tests, build and docs, as CI runs them
mise run release:dry-run     # what a release would do, publishing nothing
```

If Docker isn't running, both stop at once and tell you to run `colima start`.

## In this repo

| Task | Runs |
|------|------|
| `mise run ci:local` | `.github/workflows/ci.yml` |
| `mise run release:dry-run` | `.github/workflows/release.yml`, as a dry run |
