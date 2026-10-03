"""harbor: scaffold a meta repo."""

import platform
import re
import shutil
import subprocess
import sys

SLUG_RE = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")
TEMPLATE = "gh:kbhatiya999/harbor"


def ask(label, default=""):
    hint = f" [{default}]" if default else ""
    return input(f"{label}{hint}: ").strip() or default


def step(title, args, cwd=None):
    print(f"▸ {title}…", end=" ", flush=True)
    try:
        r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
        ok, out = r.returncode == 0, (r.stderr or r.stdout).strip()
    except OSError as e:
        ok, out = False, str(e)
    print("✓" if ok else "✗")
    if not ok:
        sys.exit(out or 1)


def first_available(options):
    return next((o for o in options if shutil.which(o[0])), None)


def install_copier():
    cmd = first_available([
        ["uv", "tool", "install", "copier"],
        ["pipx", "install", "copier"],
        ["pip3", "install", "--user", "copier"],
        ["pip", "install", "--user", "copier"],
    ])
    if not cmd:
        sys.exit("No Python package manager found. Install copier: https://copier.readthedocs.io")
    step("Installing copier", cmd)


def install_mise():
    if platform.system() == "Windows":
        cmd = first_available([
            ["winget", "install", "--id", "jdx.mise", "--silent"],
            ["scoop", "install", "mise"],
        ])
        if not cmd:
            sys.exit("Install mise manually: https://mise.jdx.dev/getting-started.html")
    else:
        cmd = ["sh", "-c", "curl -fsSL https://mise.run | sh"]
    step("Installing mise", cmd)


def main():
    try:
        print("harbor setup: create a meta repo (mani · mise · copier)\n")

        slug = ask("GitHub slug (owner/repo)")
        while not SLUG_RE.match(slug):
            print("  must be owner/repo, e.g. kbhatiya999/my-meta")
            slug = ask("GitHub slug (owner/repo)")
        repo = slug.rsplit("/", 1)[-1]

        desc = ask("Description", f"{repo} meta repo")
        fnox = ask("Include fnox? (y/n)", "y").lower().startswith("y")
        dest = ask("Create in", f"./{repo}")
        print()

        if not shutil.which("copier"):
            install_copier()
        step("Scaffolding repo", [
            "copier", "copy", TEMPLATE, dest,
            "--data", f"github_slug={slug}",
            "--data", f"description={desc}",
            "--data", f"use_fnox={'true' if fnox else 'false'}",
            "--defaults", "--overwrite",
        ])

        if not shutil.which("mise"):
            install_mise()
        step("mise install", ["mise", "install"], cwd=dest)
        step("mise run sync", ["mise", "run", "sync"], cwd=dest)
    except (KeyboardInterrupt, EOFError):
        sys.exit(1)

    print(f"""
Done! Meta repo {repo} is ready.

  cd {dest}
  mise run hello    # verify task runner
  mise run status   # git status across sub-repos
  mise run pull     # pull all sub-repos

Pull future template updates with: copier update""")


if __name__ == "__main__":
    main()
