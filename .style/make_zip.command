#!/bin/sh
# Creates <project-folder-name>_export.zip in the project root (the folder above
# .style/) with the project's relevant files, for example to upload to claude.ai. It
# holds the files git tracks plus new files git is not ignoring, minus the patterns in
# .style/zipignore. The zip never contains .git, style/, .venv or earlier export zips.
# macOS: double-click .style/make_zip.command. Linux: run .style/make_zip.sh.
# Windows: .style\make_zip.bat. Or run the VS Code task "Make export zip".
# Add the word nopause (.style/make_zip.sh nopause) to skip the final pause.
cd "$(dirname "$0")/.." || exit 1
PY=""
for candidate in python3 python; do
    if "$candidate" -c "import sys" >/dev/null 2>&1; then
        PY=$candidate
        break
    fi
done
if [ -z "$PY" ]; then
    echo "make_zip needs Python 3. On macOS run: xcode-select --install"
    STATUS=1
else
    "$PY" - <<'PYTHON'
import fnmatch
import os
import subprocess
import zipfile
from pathlib import Path

ALWAYS_LEFT_OUT = {'.git', 'style', '.venv', 'venv', '__pycache__', 'node_modules'}

root = Path.cwd()
name = root.name
zip_path = root / f'{name}_export.zip'
patterns = []
ignore_file = root / '.style' / 'zipignore'
if ignore_file.is_file():
    lines = ignore_file.read_text(encoding='utf-8').splitlines()
    patterns = [line.strip() for line in lines
                if line.strip() and not line.strip().startswith('#')]


def is_left_out(relative):
    parts = relative.split('/')
    if any(part in ALWAYS_LEFT_OUT for part in parts[:-1]):
        return True
    if parts[-1].endswith(('_export.zip', '.pyc')):
        return True
    folders = ['/'.join(parts[:count]) for count in range(1, len(parts))]
    for pattern in patterns:
        if pattern.endswith('/'):
            clean = pattern.strip('/')
            if '/' in clean or pattern.startswith('/'):
                if any(fnmatch.fnmatch(folder, clean) for folder in folders):
                    return True
            elif any(fnmatch.fnmatch(part, clean) for part in parts[:-1]):
                return True
        elif fnmatch.fnmatch(relative, pattern.lstrip('/')):
            return True
        elif '/' not in pattern and fnmatch.fnmatch(parts[-1], pattern):
            return True
    return False


# ---- 1 List the files ------------------------------------------------------------------
try:
    result = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-files', '-z',
                             '--cached', '--others', '--exclude-standard'],
                            capture_output=True, text=True, check=False)
    is_repo = result.returncode == 0
except FileNotFoundError:
    is_repo = False
if is_repo:
    files = [file for file in result.stdout.split('\0') if file]
else:
    files = [str(path.relative_to(root)).replace(os.sep, '/')
             for path in root.rglob('*') if path.is_file()]

# ---- 2 Drop the files that are not needed -----------------------------------------------
kept = [file for file in sorted(set(files))
        if not is_left_out(file) and (root / file).is_file()]
if not kept:
    print('No files to zip.')
    raise SystemExit(1)

# ---- 3 Create the zip -------------------------------------------------------------------
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in kept:
        archive.write(root / file, f'{name}/{file}')
size = zip_path.stat().st_size / 1024 / 1024
print(f'Created {zip_path.name} ({len(kept)} files, {size:.2f} MB)')
PYTHON
    STATUS=$?
fi
if [ "$1" != "nopause" ]; then
    printf 'Press Enter to close...'
    read -r _
fi
exit $STATUS
