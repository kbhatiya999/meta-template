# Every mise task of this repo as a Tilt button: `mise run tilt:up`.
#
# The shared parts live in tilt/ and come from the meta-repo template, so
# template updates keep them current. Put this repo's own Tilt extras in
# .tilt/Tiltfile; usually none are needed, since new mise tasks appear by
# themselves (see tilt/tasks.Tiltfile for the #TILT annotations).
#
# Tilt keeps the environment it starts with, so `mise run tilt:up` starts it
# nearly empty and every button runs `mise run`, which resolves values fresh
# (fnox, the flavour from mise.local.toml). Changes apply without a restart,
# except TILT_PORT itself.

include('./tilt/others.Tiltfile')
include('./tilt/tasks.Tiltfile')
if os.path.exists(os.path.join(config.main_dir, '.tilt', 'Tiltfile')):
    include('./.tilt/Tiltfile')
