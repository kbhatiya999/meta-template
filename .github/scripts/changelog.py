"""Cut a release in CHANGELOG.md and write the GitHub release notes.

Usage: python3 changelog.py <version> <notes-file> [<repo>]

Moves the Unreleased entry under "## [<version>] - <today>", updates the compare
links, and writes the release notes (the entry plus install instructions).
Fails if the Unreleased entry is empty.
"""

import datetime
import re
import sys
from pathlib import Path

version, notes_file = sys.argv[1], Path(sys.argv[2])
repo = sys.argv[3] if len(sys.argv) > 3 else "kbhatiya999/meta-template"
path = Path("CHANGELOG.md")
text = path.read_text()

m = re.search(r"^## \[Unreleased\]\n(.*?)(?=^## \[|^\[Unreleased\]:)", text, re.M | re.S)
if not m or not m.group(1).strip():
    sys.exit("CHANGELOG.md has no entry under ## [Unreleased]. Describe the changes there, then release.")
entry = m.group(1).strip()

previous = re.search(r"^## \[(\d[^\]]*)\]", text[m.end():], re.M).group(1)
today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()  # same day as the version
text = text[:m.start()] + f"## [Unreleased]\n\n## [{version}] - {today}\n\n{entry}\n\n" + text[m.end():]
text = re.sub(r"^\[Unreleased\]: .*$",
              f"[Unreleased]: https://github.com/{repo}/compare/v{version}...HEAD\n"
              f"[{version}]: https://github.com/{repo}/compare/v{previous}...v{version}",
              text, count=1, flags=re.M)
path.write_text(text)

notes_file.write_text(f"""{entry}

## Install or upgrade

```sh
uv tool install harbor-meta    # first time
uv tool upgrade harbor-meta    # already installed
harbor sync                    # moves every clean meta repo to template v{version}
```

Run this version without installing: `uvx harbor-meta@{version}`

Template only, without harbor: `copier copy --vcs-ref v{version} gh:{repo} <dir>`,
or `copier update` inside an existing meta repo.

[Documentation](https://kbhatiya999.github.io/meta-template/) ·
[Changelog](https://github.com/{repo}/blob/main/CHANGELOG.md) ·
[PyPI](https://pypi.org/project/harbor-meta/{version}/) ·
[Compare with v{previous}](https://github.com/{repo}/compare/v{previous}...v{version})
""")
print(f"Released {version} in CHANGELOG.md (previous: {previous})")
