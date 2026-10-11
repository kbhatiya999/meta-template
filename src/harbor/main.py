"""harbor: one tree of meta repos per GitHub account, every repo cloned exactly once.

Layout:  <BASE>/<account>-meta/            root meta repo for <account>
           mani.yaml                       its projects (repos and nested meta repos)
           <repo>/                         the one clone of <repo>
           <nested-meta>/mani.yaml         a meta repo inside the tree

Every git/gh call inside a root runs as that root's account, whichever gh account
is active. A meta repo is "adopted" once copier has written .copier-answers.yml.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Maintainers: change these defaults for your users. The env vars exist for tests.
BASE = Path(os.environ.get("HARBOR_BASE", "~/repo")).expanduser().resolve()
TEMPLATE = os.environ.get("HARBOR_TEMPLATE", "gh:kbhatiya999/meta-template")

ANSWERS = ".copier-answers.yml"
TEMPLATE_GIT = re.sub(r"^gh:", "https://github.com/", TEMPLATE)
TEMPLATE_FILES = ["README.md", "mani.yaml", "mise.toml", ".gitignore", ".ignore",
                  "AGENTS.md", "CLAUDE.md", "fnox.toml"]
TEMPLATE_MANAGED = ["mise.toml", "AGENTS.md", "CLAUDE.md"]  # the rest are yours once created
SKIP_DIRS = {"node_modules", ".venv", "venv", "__pycache__", "dist", "build", "target"}
SLUG_RE = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")
MARK = "# mani #"


# ── small helpers ─────────────────────────────────────────────────────────────

def die(msg: str):
    sys.exit(f"harbor: {msg}")


def run(args, cwd=None, env=None, check=True) -> subprocess.CompletedProcess:
    r = subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                       capture_output=True, text=True)
    if check and r.returncode:
        die(f"`{' '.join(map(str, args))}` failed:\n{(r.stderr or r.stdout).strip()}")
    return r


def show(p: Path) -> str:
    home = str(Path.home())
    return "~" + str(p)[len(home):] if str(p).startswith(home) else str(p)


def bare(url: str) -> str:
    """host/owner/repo with scheme, credentials and .git stripped; case kept."""
    url = re.sub(r"^(ssh://)?git@github\.com[:/]", "github.com/", url.strip(), flags=re.I)
    url = re.sub(r"^https?://([^@/]*@)?", "", url)
    return url.rstrip("/").removesuffix(".git")


def norm(url: str) -> str:
    """Comparable form of a remote URL (GitHub names are case-insensitive)."""
    return bare(url).lower()


def slug_of(url: str) -> str | None:
    b = bare(url)
    return b.split("/", 1)[1] if b.lower().startswith("github.com/") else None


def gh_url(slug: str) -> str:
    return f"https://github.com/{slug}.git"


def origin(path: Path) -> str | None:
    # The configured URL, not `remote get-url`, which applies insteadOf rewrites.
    r = run(["git", "-C", path, "config", "--get", "remote.origin.url"], check=False)
    return r.stdout.strip() or None


def is_clone(path: Path) -> bool:
    return (path / ".git").exists()


# ── versions ──────────────────────────────────────────────────────────────────
# harbor and the template are released together as vYYYY.M.D[.N], so a harbor
# release always renders the template tag with its own version.

def version() -> str:
    try:
        return importlib.metadata.version("harbor-meta")
    except importlib.metadata.PackageNotFoundError:
        return "0"


def template_ref() -> str | None:
    """The template tag this harbor renders; None means copier's latest tag (dev builds)."""
    if ref := os.environ.get("HARBOR_TEMPLATE_REF"):
        return ref
    v = version()
    return None if v.startswith("0") else f"v{v}"


def vkey(tag: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", tag))


def template_commit(meta: Path) -> str | None:
    f = meta / ANSWERS
    return (yaml.safe_load(f.read_text()) or {}).get("_commit") if f.exists() else None


def latest_release() -> str | None:
    r = run(["git", "ls-remote", "--tags", "--refs", TEMPLATE_GIT], check=False)
    tags = re.findall(r"refs/tags/(v[\d.]+)$", r.stdout, re.M)
    return max(tags, key=vkey) if tags else None


# ── accounts ──────────────────────────────────────────────────────────────────

@dataclass
class Account:
    login: str
    root: Path
    env: dict

    def git(self, *args, cwd=None, check=True):
        # Force gh's credential helper so the root's token is used, never a
        # keychain entry for some other account.
        return run(["git", "-c", "credential.https://github.com.helper=",
                    "-c", "credential.https://github.com.helper=!gh auth git-credential",
                    *args], cwd=cwd, env=self.env, check=check)

    def gh(self, *args, check=True):
        return run(["gh", *args], env=self.env, check=check)


def account(root: Path) -> Account:
    login = root.name.removesuffix("-meta")
    r = run(["gh", "auth", "token", "--user", login], check=False)
    if r.returncode or not r.stdout.strip():
        die(f"{show(root)} belongs to {login}, but gh isn't logged in as {login}.\n"
            f"Run: gh auth login   (harbor uses {login}'s token here even if another account is active)")
    token = r.stdout.strip()
    return Account(login, root, {**os.environ, "GH_TOKEN": token, "GITHUB_TOKEN": token,
                                 "GIT_TERMINAL_PROMPT": "0"})


def active_login() -> str:
    r = run(["gh", "api", "user", "--jq", ".login"], check=False)
    if r.returncode:
        die("gh isn't logged in. Run: gh auth login")
    return r.stdout.strip()


def root_of(path: Path) -> Path | None:
    try:
        rel = path.resolve().relative_to(BASE)
    except ValueError:
        return None
    if rel.parts and rel.parts[0].endswith("-meta"):
        return BASE / rel.parts[0]
    return None


def roots() -> list[Path]:
    if not BASE.is_dir():
        return []
    return sorted(d for d in BASE.iterdir() if d.name.endswith("-meta") and (d / "mani.yaml").exists())


def bind_identity(acct: Account):
    """Commits anywhere under the root use the account's name/email (git includeIf)."""
    cfg = Path("~/.config/harbor").expanduser() / f"{acct.login}.gitconfig"
    if not cfg.exists():
        u = json.loads(acct.gh("api", "user").stdout)
        email = u.get("email") or f"{u['id']}+{u['login']}@users.noreply.github.com"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(f"[user]\n\tname = {u.get('name') or u['login']}\n\temail = {email}\n")
    key = f"includeIf.gitdir:{acct.root}/.path"
    if str(cfg) not in run(["git", "config", "--global", "--get-all", key], check=False).stdout.split("\n"):
        run(["git", "config", "--global", "--add", key, cfg])
        print(f"✓ commits under {show(acct.root)} now use the identity in {show(cfg)}")


# ── the tree ──────────────────────────────────────────────────────────────────

@dataclass
class Node:
    name: str
    path: Path
    url: str | None
    meta: bool = False
    children: list[Node] = field(default_factory=list)


def projects(meta: Path) -> dict:
    data = yaml.safe_load((meta / "mani.yaml").read_text()) or {}
    return data.get("projects") or {}


def load(meta: Path, name: str | None = None, url: str | None = None) -> Node:
    node = Node(name or meta.name, meta, url or origin(meta), meta=True)
    for pname, spec in projects(meta).items():
        spec = spec or {}
        rel = str(spec.get("path", pname))
        if rel in (".", ""):
            continue
        p = (meta / rel).resolve()
        if (p / "mani.yaml").exists():
            node.children.append(load(p, pname, spec.get("url")))
        else:
            node.children.append(Node(pname, p, spec.get("url")))
    return node


def walk(node: Node):
    yield node
    for c in node.children:
        yield from walk(c)


def find_clones(top: Path, prune: set[Path], depth: int = 4):
    """Git repos under top, not descending into pruned paths or into other repos."""
    top = top.resolve()
    for dirpath, dirs, _ in os.walk(top):
        d = Path(dirpath)
        if d != top and is_clone(d):
            dirs[:] = []
            yield d
            continue
        if len(d.relative_to(top).parts) >= depth:
            dirs[:] = []
            continue
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")
                   and (d / x).resolve() not in prune]


@dataclass
class Survey:
    trees: list[Node]
    untracked: list[tuple[Node, Path]]      # clones inside a meta repo dir, not in its mani.yaml
    outside: list[Path]                     # clones under BASE but outside every root
    clones: dict[str, list[Path]]           # normalized url -> every local clone of it


def survey() -> Survey:
    trees = [load(r) for r in roots()]
    known = {n.path for t in trees for n in walk(t)}
    untracked = [(m, p) for t in trees for m in walk(t) if m.meta and m.path.exists()
                 for p in find_clones(m.path, known - {m.path})]
    outside = list(find_clones(BASE, {t.path for t in trees}, depth=3)) if BASE.is_dir() else []
    clones = defaultdict(list)
    paths = [n.path for t in trees for n in walk(t) if is_clone(n.path)]
    for p in paths + [p for _, p in untracked] + outside:
        if u := origin(p):
            clones[norm(u)].append(p)
    return Survey(trees, untracked, outside, clones)


def here(arg: str | None) -> tuple[Account, Path]:
    """The meta repo a command acts on: --in, else the cwd, else the active account's root."""
    start = Path(arg).expanduser().resolve() if arg else Path.cwd().resolve()
    root = root_of(start)
    if root is None:
        if arg:
            die(f"{show(start)} isn't inside a root under {show(BASE)}")
        root = start = BASE / f"{active_login()}-meta"
    if not (root / "mani.yaml").exists():
        die(f"no root at {show(root)} yet. Run: harbor init")
    d = start
    while d != root and not (d / "mani.yaml").exists():
        d = d.parent
    return account(root), d


# ── git state ─────────────────────────────────────────────────────────────────

@dataclass
class State:
    branch: str = "?"
    upstream: str | None = None
    ahead: int = 0
    behind: int = 0
    changed: int = 0
    note: str = ""

    def __str__(self):
        parts = [self.branch, f"{self.changed} changed" if self.changed else "clean"]
        if self.upstream is None:
            parts.append("no upstream")
        if self.ahead:
            parts.append(f"↑{self.ahead} unpushed")
        if self.behind:
            parts.append(f"↓{self.behind} behind")
        if self.note:
            parts.append(self.note)
        return " · ".join(parts)


def state(path: Path, acct: Account | None = None, fetch: bool = False) -> State:
    s = State()
    if fetch and acct and acct.git("fetch", "--quiet", "--prune", cwd=path, check=False).returncode:
        s.note = "fetch failed"
    lines = run(["git", "-C", path, "status", "--porcelain=v1", "-b"], check=False).stdout.splitlines()
    head = lines[0] if lines else ""
    s.changed = len(lines) - 1
    if m := re.match(r"## No commits yet on (\S+)", head):
        s.branch, s.note = m.group(1), "no commits"
    elif m := re.match(r"## (\S+?)(?:\.\.\.(\S+))?(?: \[(.*)\])?$", head):
        s.branch, s.upstream, info = m.group(1), m.group(2), m.group(3) or ""
        s.ahead = int(a.group(1)) if (a := re.search(r"ahead (\d+)", info)) else 0
        s.behind = int(b.group(1)) if (b := re.search(r"behind (\d+)", info)) else 0
        if "gone" in info:
            s.note = "upstream deleted"
    return s


# ── editing a meta repo ───────────────────────────────────────────────────────

def add_project(meta: Path, name: str, url: str):
    """Append a project to mani.yaml as text, so comments survive."""
    f = meta / "mani.yaml"
    text = f.read_text()
    entry = f"  {name}:\n    path: {name}\n    url: {url}\n"
    m = re.search(r"^projects:[ \t]*\n", text, re.M)
    if not m:
        text = f"projects:\n{entry}\n{text}"
    else:
        nxt = re.search(r"^\S", text[m.end():], re.M)
        at = m.end() + nxt.start() if nxt else len(text)
        head = text[:at].rstrip("\n") + "\n\n"
        text = head + entry + ("\n" + text[at:] if nxt else "")
    yaml.safe_load(text)  # never leave a broken manifest behind
    f.write_text(text)


def write_ignores(meta: Node):
    """Keep the # mani # block of .gitignore and .ignore listing the children."""
    rels = sorted(str(c.path.relative_to(meta.path)) for c in meta.children
                  if c.path.is_relative_to(meta.path))
    block = MARK + "\n" + "".join(r + "\n" for r in rels) + MARK + "\n"
    for name in (".gitignore", ".ignore"):
        f = meta.path / name
        if not f.exists() and name == ".ignore":
            continue
        text = f.read_text() if f.exists() else ""
        if MARK in text:
            new = re.sub(rf"{MARK}\n.*?{MARK}\n?", lambda _: block, text, count=1, flags=re.S)
        else:
            new = (text.rstrip("\n") + "\n\n" if text.strip() else "") + block
        if new != text:
            f.write_text(new)


def commit(meta: Path, msg: str, names=("mani.yaml", ".gitignore", ".ignore")) -> bool:
    files = [f for f in names if (meta / f).exists()]
    run(["git", "-C", meta, "add", "--", *files])
    if run(["git", "-C", meta, "diff", "--cached", "--quiet"], check=False).returncode:
        run(["git", "-C", meta, "commit", "--quiet", "-m", msg])
        return True
    return False


def copier(dest: Path, slug: str, desc: str | None = None, skip=()):
    # Template-managed files a repo already had stay its own on every update.
    keep = [f for f in skip if f in TEMPLATE_MANAGED]
    args = [sys.executable, "-m", "copier", "copy", TEMPLATE, dest, "--defaults",
            "--data", f"github_slug={slug}", "--data", f"keep={json.dumps(keep)}"]
    if desc:
        args += ["--data", f"description={desc}"]
    for f in skip:
        args += ["--skip", f]
    if ref := template_ref():
        args += ["--vcs-ref", ref]
    run(args)


def update_template(meta: Path) -> str | None:
    """Bring an adopted, clean meta repo to this harbor's template. Returns a message."""
    have, want = template_commit(meta), template_ref()
    if not have or not want or have == want or vkey(have) > vkey(want):
        return None
    if state(meta).changed:
        return f"· template {have} → {want} waits: uncommitted changes"
    run([sys.executable, "-m", "copier", "update", "--defaults", "--skip-answered",
         "--conflict", "rej", "--vcs-ref", want], cwd=meta, check=False)
    rejects = run(["git", "-C", meta, "ls-files", "--others", "--exclude-standard", "*.rej"]).stdout.split()
    if rejects:
        run(["git", "-C", meta, "reset", "--hard", "--quiet"])
        run(["git", "-C", meta, "clean", "-fdq"])
        return f"! template {have} → {want} conflicts with local edits; left as is (run copier update there)"
    run(["git", "-C", meta, "add", "-A"])
    run(["git", "-C", meta, "commit", "--quiet", "-m", f"harbor: update template to {want}"])
    return f"✓ template {have} → {want}"


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_status(args):
    s = survey()
    if not s.trees:
        print(f"No roots under {show(BASE)} yet. Run: harbor init")
    accounts: dict[Path, Account | None] = {}
    for t in s.trees:
        try:
            accounts[t.path] = None if args.offline else account(t.path)
        except SystemExit as e:
            accounts[t.path] = None
            print(e.code)

    def line(n: Node, depth: int, acct):
        pad = "  " * depth
        label = n.name + ("/" if n.meta else "")
        if not n.path.exists():
            info = "not cloned → harbor sync"
        elif not is_clone(n.path):
            info = "folder exists but isn't a git repo"
        else:
            info = str(state(n.path, acct, fetch=acct is not None))
            if n.meta and not (n.path / ANSWERS).exists():
                info += " · not adopted → harbor adopt " + show(n.path)
            elif n.meta and (want := template_ref()) and (have := template_commit(n.path)) \
                    and vkey(have) < vkey(want):
                info += f" · template {have} → harbor sync updates it to {want}"
            if n.url and (o := origin(n.path)) and norm(o) != norm(n.url):
                info += f" · origin is {o}, mani.yaml says {n.url}"
        print(f"{pad}{label:<{max(1, 34 - len(pad))}} {info}")
        for c in n.children:
            line(c, depth + 1, acct)

    for t in s.trees:
        acct = accounts[t.path]
        print(f"\n{show(t.path)}  (root of {t.path.name.removesuffix('-meta')})")
        line(t, 1, acct)
        for m, p in s.untracked:
            if p.is_relative_to(t.path):
                print(f"  ! {show(p)} is a clone not listed in {show(m.path / 'mani.yaml')} → harbor add {show(p)}")

    if s.outside:
        print(f"\nOutside every root (move in with harbor add <path>):")
        for p in s.outside:
            o = origin(p)
            print(f"  {show(p):<40} {(slug_of(o) or o) if o else 'no remote'} · {state(p)}")

    dups = {u: ps for u, ps in s.clones.items() if len(ps) > 1}
    if dups:
        print("\nDuplicates (same repo cloned more than once; keep the one in the tree):")
        for u, ps in dups.items():
            print(f"  {slug_of(u) or u}")
            for p in ps:
                where = "in tree" if root_of(p) else "outside"
                print(f"    {show(p):<38} {where} · {state(p)}")
    if args.offline:
        print("\n(offline: ahead/behind are as of the last fetch)")
    elif (latest := latest_release()) and vkey(latest) > vkey(version()):
        print(f"\nharbor {latest[1:]} is out (you have {version()}). "
              f"Upgrade: uv tool upgrade harbor-meta, then harbor sync updates every meta repo.")


def cmd_add(args):
    acct, meta = here(args.into)
    s = survey()
    src = Path(args.repo).expanduser()
    local = src.exists()
    if local:
        src = src.resolve()
        if not is_clone(src):
            die(f"{show(src)} isn't a git repo")
        url = origin(src) or die(f"{show(src)} has no origin remote; push it to GitHub first")
    elif SLUG_RE.match(args.repo):
        url = gh_url(args.repo)
    elif slug_of(args.repo):
        url = gh_url(slug_of(args.repo))
    else:
        die(f"{args.repo} is neither a path, owner/repo nor a GitHub URL")
    name = args.name or (slug_of(url) or url).rsplit("/", 1)[-1]

    for t in s.trees:
        for n in walk(t):
            if n.url and norm(n.url) == norm(url):
                if local and not n.path.exists():
                    move_in(src, n.path)
                    return
                die(f"already tracked at {show(n.path)}")
    others = [p for p in s.clones.get(norm(url), []) if p != src]
    if others:
        die(f"already cloned at {show(others[0])}. Move that one in instead: harbor add {show(others[0])}")

    target = meta / name
    if local and src == target.resolve():
        pass  # already in place, just register it
    elif target.exists():
        die(f"{show(target)} already exists")
    elif local:
        move_in(src, target)
    else:
        acct.git("clone", "--quiet", url, target)
        print(f"✓ cloned {slug_of(url)} → {show(target)}")

    add_project(meta, name, url)
    write_ignores(load(meta))
    commit(meta, f"harbor: add {name}")
    print(f"✓ added {name} to {show(meta / 'mani.yaml')} (committed locally)")


def move_in(src: Path, target: Path):
    if len(run(["git", "-C", src, "worktree", "list"]).stdout.splitlines()) > 1:
        die(f"{show(src)} has extra worktrees; remove them before moving it")
    shutil.move(src, target)
    print(f"✓ moved {show(src)} → {show(target)}")


def cmd_new(args):
    acct, parent = here(args.into)
    create_meta(acct, parent / args.name, f"{acct.login}/{args.name}", args.description)
    add_project(parent, args.name, gh_url(f"{acct.login}/{args.name}"))
    write_ignores(load(parent))
    commit(parent, f"harbor: add meta repo {args.name}")
    print(f"✓ {args.name} added to {show(parent / 'mani.yaml')} (committed locally)")


def create_meta(acct: Account, target: Path, slug: str, desc: str | None):
    """Create a meta repo on GitHub and locally; refuse if it exists anywhere."""
    url = gh_url(slug)
    s = survey()
    for t in s.trees:
        for n in walk(t):
            if n.url and norm(n.url) == norm(url):
                die(f"{slug} is already tracked at {show(n.path)}")
    if s.clones.get(norm(url)):
        die(f"{slug} is already cloned at {show(s.clones[norm(url)][0])}")
    if target.exists():
        die(f"{show(target)} already exists")
    if acct.gh("repo", "view", slug, "--json", "name", check=False).returncode == 0:
        die(f"{slug} already exists on GitHub. Bring it in with: harbor add {slug}")

    acct.gh("repo", "create", slug, "--private", *(["--description", desc] if desc else []))
    print(f"✓ created github.com/{slug} (private)")
    target.mkdir(parents=True)
    run(["git", "init", "--quiet", "-b", "main", target])
    copier(target, slug, desc)
    run(["git", "-C", target, "add", "-A"])
    run(["git", "-C", target, "commit", "--quiet", "-m", "harbor: scaffold meta repo"])
    run(["git", "-C", target, "remote", "add", "origin", url])
    acct.git("push", "--quiet", "-u", "origin", "main", cwd=target)
    print(f"✓ scaffolded and pushed {show(target)}")


def adopt(path: Path):
    url = origin(path) or die(f"{show(path)} has no origin remote")
    slug = slug_of(url) or die(f"{url} isn't a GitHub remote")
    if (path / ANSWERS).exists():
        print(f"✓ {show(path)} is already adopted (template updates: harbor sync)")
        return
    if state(path).changed:
        die(f"{show(path)} has uncommitted changes; commit or stash them, then adopt")
    skip = [f for f in TEMPLATE_FILES if (path / f).exists()]
    copier(path, slug, skip=skip)
    write_ignores(load(path))
    run(["git", "-C", path, "add", "-A"])
    run(["git", "-C", path, "commit", "--quiet", "-m", "harbor: adopt meta repo"])
    kept = f" (kept your {', '.join(skip)})" if skip else ""
    print(f"✓ adopted {show(path)}{kept}")


def cmd_adopt(args):
    path = Path(args.path).expanduser().resolve() if args.path else Path.cwd().resolve()
    root = root_of(path) or die(f"{show(path)} isn't inside a root under {show(BASE)}")
    account(root)
    adopt(path)


def cmd_init(args):
    login = args.account or active_login()
    root = BASE / f"{login}-meta"
    slug = f"{login}/{login}-meta"
    acct = account(root)
    if root.exists():
        adopt(root)
    elif acct.gh("repo", "view", slug, "--json", "name", check=False).returncode == 0:
        BASE.mkdir(parents=True, exist_ok=True)
        acct.git("clone", "--quiet", gh_url(slug), root)
        print(f"✓ cloned your root {slug} → {show(root)}")
        adopt(root)
    else:
        BASE.mkdir(parents=True, exist_ok=True)
        create_meta(acct, root, slug, f"Root meta repo for {login}")
    bind_identity(acct)
    print(f"\nRoot for {login}: {show(root)}\nNext: harbor sync, then harbor status")


def update(acct: Account, path: Path, label: str, push: bool = False) -> None:
    """Fetch, then rebase onto upstream only if nothing local can be lost.
    push=True (meta repos only) also pushes harbor's own manifest commits."""
    s = state(path, acct, fetch=True)
    if s.note == "fetch failed":
        msg = "! fetch failed (offline, or no access as " + acct.login + ")"
    elif s.changed:
        msg = f"· skipped: {s.changed} uncommitted change(s)"
    elif s.upstream is None:
        msg = f"· {s.branch} has no upstream"
    elif not s.behind:
        msg = "✓ up to date" + (f", ↑{s.ahead} unpushed" if s.ahead else "")
    elif acct.git("rebase", "--quiet", "@{u}", cwd=path, check=False).returncode:
        acct.git("rebase", "--abort", cwd=path, check=False)
        msg = f"! {s.branch} conflicts with upstream, left untouched (↓{s.behind} ↑{s.ahead})"
    else:
        msg = f"✓ rebased onto {s.behind} new commit(s)" + (f", ↑{s.ahead} unpushed" if s.ahead else "")
    if push and s.ahead and not s.changed and s.upstream and "!" not in msg:
        ok = acct.git("push", "--quiet", cwd=path, check=False).returncode == 0
        msg += f" → {'pushed' if ok else '! push failed'}"
    print(f"{label:<36} {msg}")


def sync_meta(acct: Account, meta: Path, clones: dict, depth: int = 0):
    pad = "  " * depth
    if msg := update_template(meta):
        print(f"{pad + meta.name + '/':<36} {msg}")
    update(acct, meta, pad + meta.name + "/", push=True)
    node = load(meta)
    for c in node.children:
        label = pad + "  " + c.name
        if not c.path.exists():
            if not c.url:
                print(f"{label:<36} ! no url in mani.yaml")
                continue
            if elsewhere := clones.get(norm(c.url)):
                print(f"{label:<36} ! already cloned at {show(elsewhere[0])} → harbor add {show(elsewhere[0])}")
                continue
            acct.git("clone", "--quiet", c.url, c.path, check=False)
            print(f"{label:<36} {'✓ cloned' if is_clone(c.path) else '! clone failed'}")
            if (c.path / "mani.yaml").exists():
                sync_meta(acct, c.path, clones, depth + 1)
        elif not is_clone(c.path):
            print(f"{label:<36} ! exists but isn't a git repo")
        elif (c.path / "mani.yaml").exists():
            sync_meta(acct, c.path, clones, depth + 1)
        else:
            update(acct, c.path, label)
    write_ignores(load(meta))
    if commit(meta, "harbor: update ignore blocks", names=(".gitignore", ".ignore")):
        print(f"{pad + meta.name + '/':<36} ✓ committed updated .gitignore/.ignore (pushed on next sync)")


def cmd_sync(args):
    acct, meta = here(args.into)
    sync_meta(acct, meta, survey().clones)


def main():
    p = argparse.ArgumentParser(
        prog="harbor",
        description="One tree of meta repos per GitHub account; every repo cloned exactly once.")
    p.add_argument("--version", action="version", version=f"harbor {version()} (template {template_ref() or 'latest tag'})")
    sub = p.add_subparsers(dest="cmd", metavar="command")

    s = sub.add_parser("status", help="everything you have, where it lives, and whether it's safe to work on (default)")
    s.add_argument("--offline", action="store_true", help="don't fetch first")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("init", help="set up (or adopt) the root meta repo for a GitHub account")
    s.add_argument("account", nargs="?", help="defaults to the active gh account")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("sync", help="clone what's missing, fetch everything, rebase clean branches")
    s.add_argument("--in", dest="into", metavar="META", help="meta repo to sync (default: current)")
    s.set_defaults(func=cmd_sync)

    s = sub.add_parser("add", help="add a repo: owner/repo, a GitHub URL, or a path to an existing clone (moved in)")
    s.add_argument("repo")
    s.add_argument("--name", help="folder/project name (default: repo name)")
    s.add_argument("--in", dest="into", metavar="META", help="meta repo to add to (default: current)")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("new", help="create a nested meta repo (GitHub + local), refusing duplicates")
    s.add_argument("name")
    s.add_argument("--description")
    s.add_argument("--in", dest="into", metavar="META", help="parent meta repo (default: current)")
    s.set_defaults(func=cmd_new)

    s = sub.add_parser("adopt", help="bring an existing meta repo under the template (keeps your files)")
    s.add_argument("path", nargs="?")
    s.set_defaults(func=cmd_adopt)

    args = p.parse_args()
    try:
        (getattr(args, "func", None) or (lambda a: cmd_status(argparse.Namespace(offline=False))))(args)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
