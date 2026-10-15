# A button for every mise task of this repo, generated from `mise tasks --json`,
# so adding a task never needs a Tiltfile edit.
#
# A task's group is its folder (tilt:watch and tilt -> "tilt"; none -> "tasks"). How
# Tilt treats it comes from `#TILT` lines in the task's own file:
#
#   #TILT serve                  a long-running server, restarted when config changes
#   #TILT deps=src,tests         also run automatically when these paths change
#   #TILT link=http://127.0.0.1:${DOCS_PORT}/   a link; ${NAME} as tasks see it
#   #TILT hide                   no button
#
# Without any, a task is a button that runs when clicked. Hidden mise tasks
# (`#MISE hide=true`) never get one. Tilt's own dependency on files is not mise's
# `sources`: mise skips a task whose sources are unchanged, so a click would do
# nothing.

ROOT = config.main_dir
TASK_DIRS = ['mise-tasks', '.mise/tasks']
# Values tasks read: a change restarts servers (and reloads this file for links).
CONFIG_FILES = ['fnox.toml', 'fnox', 'fnox.local.toml', 'mise.toml', 'mise.local.toml']
OTHERS_FILE = '.tilt-others.' + os.getenv('TILT_PORT', '10350')

def _abs(p):
    return os.path.join(ROOT, p)

# A new or removed task, or a config change, rebuilds the buttons.
for p in TASK_DIRS + CONFIG_FILES:
    watch_file(_abs(p))

def _value(name):
    """NAME as every task sees it (fnox, else the toolkit's derived default)."""
    return str(local('mise exec -- mise-tasks/.lib/value ' + name, quiet=True, echo_off=True, dir=ROOT)).strip()

def _expand(text):
    """Replace each ${NAME} with its value."""
    out = ''
    rest = text
    for _ in range(20):
        i = rest.find('${')
        if i < 0:
            break
        j = rest.find('}', i)
        if j < 0:
            break
        out += rest[:i] + _value(rest[i + 2:j])
        rest = rest[j + 1:]
    return out + rest

def _annotations(path):
    ann = {}
    for line in str(read_file(path)).split('\n'):
        if not line.startswith('#TILT '):
            continue
        for tok in line[len('#TILT '):].split(' '):
            if not tok:
                continue
            if '=' in tok:
                k, v = tok.split('=', 1)
                ann[k] = v
            else:
                ann[tok] = True
    return ann

TASKS = decode_json(str(local('mise tasks --json', quiet=True, echo_off=True, dir=ROOT)))
for t in TASKS:
    name = t['name']
    src = t.get('source') or ''
    # This repo's tasks only: mise also lists global ones.
    if not os.path.exists(src) or not (src.startswith(ROOT) or os.path.realpath(src).startswith(os.path.realpath(ROOT))):
        continue
    ann = _annotations(src)
    if ann.get('hide'):
        continue
    # build/_default is `build`: it belongs with build:* in the "build" group.
    group = name.split(':')[0] if (':' in name or src.endswith('/_default')) else 'tasks'
    links = [link(_expand(ann['link']), 'open')] if 'link' in ann else []
    deps = [_abs(d) for d in ann['deps'].split(',')] if 'deps' in ann else []
    if ann.get('serve'):
        local_resource(name, serve_cmd='mise run ' + name, serve_dir=ROOT, labels=[group], links=links,
                       deps=deps + [_abs(p) for p in CONFIG_FILES] + [_abs(OTHERS_FILE)])
    else:
        local_resource(name, cmd='mise run ' + name, dir=ROOT, labels=[group], links=links, deps=deps,
                       auto_init=False, trigger_mode=TRIGGER_MODE_AUTO if deps else TRIGGER_MODE_MANUAL)
