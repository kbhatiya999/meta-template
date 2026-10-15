# Other Tilt dashboards serving this repo, from any terminal, found by their
# working directory rather than their port. Two Tilts run every server twice,
# so they fight over ports: "other tilts" turns red while any exist, and its
# "Stop another Tilt" button stops the one you pick. tilt-watch keeps the list in
# .tilt-others.<port> (gitignored) so the button and status stay current, and
# servers restart when it changes, taking any port that was freed.

load('ext://uibutton', 'cmd_button', 'choice_input')

ROOT = config.main_dir
OTHERS_FILE = os.path.join(ROOT, '.tilt-others.' + os.getenv('TILT_PORT', '10350'))
watch_file(OTHERS_FILE)

local_resource('tilt-watch', serve_cmd='mise run tilt:watch', serve_dir=ROOT, labels=['tilt'])
local_resource('other tilts', cmd='mise run tilt:others', dir=ROOT, deps=[OTHERS_FILE], labels=['tilt'])

OTHERS = [o for o in str(read_file(OTHERS_FILE, '')).strip().split('\n') if o]
if OTHERS:
    cmd_button('stop-other-tilt', resource='other tilts', text='Stop another Tilt', icon_name='stop_circle',
               argv=['sh', '-c', 'cd "%s" && mise run tilt:stop "$TILT_TO_STOP"' % ROOT],
               inputs=[choice_input('TILT_TO_STOP', 'Which Tilt (pid:port)', OTHERS)])
