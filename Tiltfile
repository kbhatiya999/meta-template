# Every flow of this repo as a button: `mise run up`, then the URL it prints
# (TILT_PORT in fnox.toml, so it never collides with another project's Tilt).
#
# Env vars: Tilt keeps the environment it started with, and reloading this file
# doesn't refresh it. So `mise run up` starts Tilt with a nearly empty
# environment, and every resource goes through mise and fnox, which resolve
# values fresh on each run from fnox.toml / fnox.local.toml, in the flavour
# mise.local.toml picks (FNOX_PROFILE). A change applies the next time a resource
# runs, and the long-running docs server restarts when any of those files change.
#
# Everything here is also a plain `mise run <task>`, so nothing depends on Tilt.

load('ext://uibutton', 'cmd_button', 'choice_input')

ENV_FILES = ['fnox.toml', 'fnox.local.toml', 'mise.toml', 'mise.local.toml']

# Read the docs port the way tasks do (mise picks the flavour, fnox resolves it),
# and reload this file when config changes, so the docs link follows a change.
for f in ENV_FILES:
    watch_file(f)
DOCS_PORT = str(local('mise exec -- fnox get DOCS_PORT', quiet=True, echo_off=True)).strip()
watch_settings(ignore=['.venv', 'site', 'dist', '**/__pycache__'])


def task(name, run, labels, deps=[], auto=False, serve=False, links=[]):
    """A resource that runs `mise run <run>` (or any mise-run command line).

    auto=False: only when you click it. auto=True: also whenever deps change.
    serve=True: a long-running process, restarted when deps, env files or the other
    Tilts change."""
    cmd = 'mise run ' + run
    if serve:
        # Restart on config changes, and when another Tilt comes or goes: a port it
        # held may just have been freed.
        local_resource(name, serve_cmd=cmd, deps=deps + ENV_FILES + [OTHERS_FILE], labels=labels, links=links)
    else:
        local_resource(
            name, cmd=cmd, deps=deps, labels=labels, links=links, auto_init=False,
            trigger_mode=TRIGGER_MODE_AUTO if auto else TRIGGER_MODE_MANUAL)


# ── tilt ─────────────────────────────────────────────────────────────────────
# Other dashboards serving this repo, from any terminal, found by their working
# directory rather than their port. Two Tilts run every server twice, so they
# fight over ports: "other tilts" turns red while any exist, and its "Stop
# another Tilt" button stops the one you pick. A small watcher keeps the list in
# .tilt-others.<port> (gitignored), so the button and status stay current.
OWN_PORT = os.getenv('TILT_PORT', '10350')
OTHERS_FILE = '.tilt-others.' + OWN_PORT
watch_file(OTHERS_FILE)
local_resource('tilt-watch', serve_cmd='scripts/tilts --watch --except %s --state %s' % (OWN_PORT, OTHERS_FILE),
               labels=['tilt'])
local_resource('other tilts', cmd='scripts/tilts --except ' + OWN_PORT, deps=[OTHERS_FILE], labels=['tilt'])
OTHERS = [o for o in str(read_file(OTHERS_FILE, '')).strip().split('\n') if o]
if OTHERS:
    cmd_button('stop-other-tilt', resource='other tilts', text='Stop another Tilt', icon_name='stop_circle',
               argv=['sh', '-c', 'scripts/tilts --stop "$TILT_TO_STOP"'],
               inputs=[choice_input('TILT_TO_STOP', 'Which Tilt (pid:port)', OTHERS)])

# ── develop ──────────────────────────────────────────────────────────────────
# Re-installs when dependencies or the version source change; code edits need nothing.
task('install', 'dev', ['develop'], deps=['pyproject.toml', 'uv.lock'], auto=True)
task('uninstall', 'undev', ['develop'])

# ── check ────────────────────────────────────────────────────────────────────
# The e2e suite reruns by itself when code, template or tests change (~35s).
task('test', 'test', ['check'], deps=['src', 'tests', 'template', 'copier.yml'], auto=True)
task('build', 'build', ['check'])
task('docs-build', 'docs-build', ['check'])
# The GitHub workflows themselves, run locally in Docker by act. They stop with a
# message if Docker/Colima isn't running.
task('ci-local', 'ci-local', ['check'])

# ── docs ─────────────────────────────────────────────────────────────────────
task('docs', 'docs', ['docs'], serve=True, deps=['mkdocs.yml'],
     links=[link('http://127.0.0.1:%s/meta-template/' % DOCS_PORT, 'docs site')])

# ── use (this project only) ──────────────────────────────────────────────────
# Your installed harbor, through fnox so values like HARBOR_BASE apply.
local_resource('harbor status', cmd='mise exec -- fnox exec -- harbor status', labels=['use'],
               auto_init=False, trigger_mode=TRIGGER_MODE_MANUAL)
local_resource('harbor sync', cmd='mise exec -- fnox exec -- harbor sync', labels=['use'],
               auto_init=False, trigger_mode=TRIGGER_MODE_MANUAL)

# ── env ──────────────────────────────────────────────────────────────────────
# What every button sees: the fnox flavour, plain values, and secret names.
task('env', 'env', ['env'])
# A task that receives a secret through a mise grant; its log shows [redacted].
task('secret-example', 'secret-example', ['env'])

# ── release ──────────────────────────────────────────────────────────────────
# Local rehearsal in Docker: version, changelog and build only. Can't publish,
# push or release.
task('release-dry-run', 'release-dry-run', ['release'])
# The real thing. Refuses unless everything is committed and pushed and
# CHANGELOG.md has an Unreleased entry; then publishes, waits, pulls and reinstalls.
task('release', 'release', ['release'])
