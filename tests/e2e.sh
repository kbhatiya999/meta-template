#!/usr/bin/env bash
# End-to-end tests for harbor, fully offline and sandboxed.
#
# "GitHub" is a folder of bare repos (git's url.insteadOf rewrites
# https://github.com/ to it), gh is a fake script, and HOME, ~/.gitconfig and the
# base folder all live in a temp dir. Your real config, repos and GitHub are
# never touched.
#
# Usage: tests/e2e.sh          (KEEP=1 keeps the sandbox for inspection)
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK=$(cd "$(mktemp -d)" && pwd -P)  # resolved: harbor reports resolved paths
[ "${KEEP:-}" = 1 ] && echo "sandbox: $WORK" || trap 'rm -rf "$WORK"' EXIT

uv sync --project "$ROOT" --quiet
HARBOR_BIN="$ROOT/.venv/bin/harbor"

# ── sandbox ──────────────────────────────────────────────────────────────────
mkdir -p "$WORK/bin" "$WORK/home/repo" "$WORK/remotes"
cat > "$WORK/bin/gh" <<'EOF'
#!/bin/sh
# fake gh: logged-in accounts are $FAKE_LOGINS, repos are bare repos in $FAKE_REMOTES
case "$1 $2" in
  "auth token") for l in $FAKE_LOGINS; do [ "$l" = "$4" ] && echo "tok-$l" && exit 0; done; exit 1;;
  "api user") l=${GH_TOKEN#tok-}; [ -z "${GH_TOKEN:-}" ] && l=${FAKE_LOGINS%% *}
     if [ "$3" = "--jq" ]; then echo "$l"; else echo "{\"login\":\"$l\",\"id\":42,\"name\":\"Test $l\",\"email\":null}"; fi;;
  "repo view") [ -d "$FAKE_REMOTES/$3.git" ];;
  "repo create") git init -q --bare "$FAKE_REMOTES/$3.git";;
  *) echo "fake gh: unsupported: $*" >&2; exit 2;;
esac
EOF
chmod +x "$WORK/bin/gh"
cat > "$WORK/home/.gitconfig" <<EOF
[user]
	name = Sandbox
	email = sandbox@example.com
[init]
	defaultBranch = main
[url "file://$WORK/remotes/"]
	insteadOf = https://github.com/
[protocol "file"]
	allow = always
EOF

export HOME="$WORK/home" GIT_CONFIG_GLOBAL="$WORK/home/.gitconfig" PATH="$WORK/bin:$PATH"
export FAKE_LOGINS=kb FAKE_REMOTES="$WORK/remotes" HARBOR_BASE="$WORK/home/repo"
export HARBOR_TEMPLATE="$ROOT" HARBOR_TEMPLATE_REF=HEAD
harbor() { "$HARBOR_BIN" "$@"; }

remote() {  # remote <owner/name> [mani.yaml content]
  git init -q --bare "$WORK/remotes/$1.git"
  local t; t=$(mktemp -d)
  git clone -q "https://github.com/$1.git" "$t" 2>/dev/null
  (cd "$t" && echo "# $1" > README.md && { [ -z "${2:-}" ] || printf "$2" > mani.yaml; } \
    && git add -A && git commit -qm init && git push -q origin main)
  rm -rf "$t"
}
push_remote() {  # push_remote <owner/name> <line>: someone else pushes a commit
  local t; t=$(mktemp -d)
  git clone -q "https://github.com/$1.git" "$t"
  (cd "$t" && echo "$2" >> README.md && git commit -qam remote && git push -q)
  rm -rf "$t"
}

pass=0; fail=0
check() {
  if eval "$2" >/dev/null 2>&1; then pass=$((pass + 1)); echo "  ✓ $1"
  else fail=$((fail + 1)); echo "  ✗ $1"; fi
}

# The state that made harbor necessary: an unadopted root, a repo in its
# manifest cloned outside it, and other clones scattered under the base.
remote kb/kb-meta "projects:\n  kb-meta:\n    path: .\n    url: https://github.com/kb/kb-meta.git\n\n  krish:\n    url: https://github.com/kb/krish.git\n"
remote kb/krish; remote kb/adam; remote other/bootcamp
R="$WORK/home/repo"; M="$R/kb-meta"
cd "$R"
git clone -q https://github.com/kb/kb-meta.git kb-meta
git clone -q https://github.com/kb/adam.git adam
git clone -q https://github.com/kb/krish.git krish

# ── tests ────────────────────────────────────────────────────────────────────
echo "discovery"
out=$(harbor 2>&1)
check "flags the root as not adopted" 'grep -q "not adopted" <<<"$out"'
check "flags a manifest repo that isn't cloned" 'grep -q "krish .*not cloned" <<<"$out"'
check "lists clones outside every root" 'grep -q "~/repo/adam" <<<"$out"'

echo "init and adopt"
harbor init >/dev/null 2>&1
check "adopts the root" 'test -f "$M/.copier-answers.yml"'
check "keeps the root's own README.md and mani.yaml" 'grep -q "# kb/kb-meta" "$M/README.md" && grep -q krish "$M/mani.yaml"'
check "binds commit identity with includeIf" 'git config --global --get-all "includeIf.gitdir:$M/.path"'
check "leaves the root clean" 'test -z "$(git -C "$M" status --porcelain)"'

echo "one clone per repo"
out=$(harbor sync 2>&1)
check "sync won't clone a repo that's cloned elsewhere" 'grep -q "already cloned at ~/repo/krish" <<<"$out"'
check "sync pushes the root's own commits" 'grep -q pushed <<<"$out"'
harbor add ~/repo/krish >/dev/null 2>&1
check "add <path> moves the clone into its slot" 'test -d "$M/krish/.git" && test ! -e "$R/krish"'
harbor add ~/repo/adam >/dev/null 2>&1
check "add <path> registers a new project" 'grep -q adam "$M/mani.yaml" && test -d "$M/adam/.git"'
check "add refuses a repo that's already tracked" '! harbor add kb/adam'
(cd "$M" && harbor new courses-meta >/dev/null 2>&1)
check "new creates a nested meta repo, locally and on GitHub" 'test -f "$M/courses-meta/.copier-answers.yml" && test -d "$WORK/remotes/kb/courses-meta.git"'
check "new refuses a duplicate" '! (cd "$M" && harbor new courses-meta)'
check "new refuses a repo that exists on GitHub" '! (cd "$M" && harbor new krish)'
harbor add other/bootcamp --in "$M/courses-meta" >/dev/null 2>&1
check "add --in targets a nested meta repo" 'test -d "$M/courses-meta/bootcamp/.git"'
harbor sync >/dev/null 2>&1
check "meta repos are clean after sync" 'test -z "$(git -C "$M" status --porcelain)" && test -z "$(git -C "$M/courses-meta" status --porcelain)"'

echo "safe sync"
push_remote kb/krish one; push_remote kb/adam two; push_remote other/bootcamp three
(cd "$M/krish" && echo l > l.txt && git add -A && git commit -qm local)
echo dirty >> "$M/adam/README.md"
(cd "$M/courses-meta/bootcamp" && echo conflict >> README.md && git commit -qam conflict)
check "status shows a repo behind" 'harbor | grep -q "krish .*↓1 behind"'
out=$(harbor sync 2>&1)
check "rebases local commits onto upstream" 'grep -q "krish .*rebased" <<<"$out"'
check "skips a repo with uncommitted work" 'grep -q "adam .*skipped" <<<"$out" && grep -q dirty "$M/adam/README.md"'
check "leaves a conflicting repo untouched" 'grep -q "bootcamp .*left untouched" <<<"$out" && test -z "$(git -C "$M/courses-meta/bootcamp" status --porcelain)"'

echo "accounts"
check "refuses when gh isn't logged in as the root's account" '! (cd "$M" && FAKE_LOGINS=other harbor sync)'
check "runs as the root's account when another is active" '(cd "$M" && FAKE_LOGINS="other kb" harbor sync)'

echo "fresh machine"
HARBOR_BASE="$WORK/home/repo2" harbor init kb >/dev/null 2>&1
HARBOR_BASE="$WORK/home/repo2" harbor sync >/dev/null 2>&1
check "init clones the root, sync clones the whole tree" 'test -d "$WORK/home/repo2/kb-meta/courses-meta/bootcamp/.git"'

echo "adopt safety"
mkdir "$M/x-meta" && (cd "$M/x-meta" && git init -q && git remote add origin https://github.com/kb/x-meta.git \
  && echo "projects: {}" > mani.yaml && echo dirty > d.txt)
check "adopt refuses a repo with uncommitted changes" '! harbor adopt "$M/x-meta"'

echo "template updates"
TPL="$WORK/template"
git clone -q "$ROOT" "$TPL" && rsync -a --exclude .git "$ROOT/" "$TPL/" \
  && (cd "$TPL" && git add -A && git commit -qm wip && git tag v2026.1.1 \
      && echo "Note A." >> template/AGENTS.md.jinja && git commit -qam A && git tag v2026.1.2)
export HARBOR_TEMPLATE="$TPL"
rm -rf "$R"/* && mkdir -p "$R"
HARBOR_TEMPLATE_REF=v2026.1.1 harbor init kb >/dev/null 2>&1
(cd "$R/kb-meta" && HARBOR_TEMPLATE_REF=v2026.1.1 harbor new z-meta >/dev/null 2>&1)
out=$(HARBOR_TEMPLATE_REF=v2026.1.2 harbor 2>&1)
check "status flags meta repos on an older template" 'grep -q "z-meta/.*template v2026.1.1 → harbor sync" <<<"$out"'
out=$(HARBOR_TEMPLATE_REF=v2026.1.2 harbor sync 2>&1)
check "sync moves meta repos to the new release" 'grep -q "z-meta/ .*✓ template v2026.1.1 → v2026.1.2" <<<"$out"'
check "...and the template-owned file changed" 'grep -q "Note A." "$R/kb-meta/z-meta/AGENTS.md"'
echo "Uncommitted." >> "$TPL/template/AGENTS.md.jinja"
HARBOR_TEMPLATE_REF=HEAD harbor sync >/dev/null 2>&1
check "uncommitted template edits are not rendered" '! grep -q Uncommitted "$R/kb-meta/z-meta/AGENTS.md"'
(cd "$TPL" && git commit -qam "dev change")
HARBOR_TEMPLATE_REF=HEAD harbor sync >/dev/null 2>&1
check "committed template edits reach meta repos on sync" 'grep -q Uncommitted "$R/kb-meta/z-meta/AGENTS.md"'
(cd "$TPL" && echo "Note B." >> template/AGENTS.md.jinja && git commit -qam B)
HARBOR_TEMPLATE_REF=HEAD harbor sync >/dev/null 2>&1
check "consecutive template commits keep updating" 'grep -q "Note B." "$R/kb-meta/z-meta/AGENTS.md"'
check "no meta repo is left behind" '! HARBOR_TEMPLATE_REF=HEAD harbor | grep -q "template v"'
(cd "$R/kb-meta/z-meta" && sed -i.bak "s/Note B./Mine./" AGENTS.md && rm AGENTS.md.bak && git commit -qam mine)
(cd "$TPL" && sed -i.bak "s/Note B./Note C./" template/AGENTS.md.jinja && rm template/AGENTS.md.jinja.bak && git commit -qam C)
out=$(HARBOR_TEMPLATE_REF=HEAD harbor sync 2>&1)
check "a conflicting template update is rolled back and reported" 'grep -q "z-meta/ .*conflicts with local edits" <<<"$out" && grep -q Mine. "$R/kb-meta/z-meta/AGENTS.md" && test -z "$(git -C "$R/kb-meta/z-meta" status --porcelain)"'
check "the root's own README.md is never updated" 'grep -q "^# kb/kb-meta" "$R/kb-meta/README.md" || ! grep -q "Note" "$R/kb-meta/README.md"'

echo
echo "passed $pass, failed $fail"
[ "$fail" = 0 ]
