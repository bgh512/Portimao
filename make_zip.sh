#!/bin/sh
# Creates <project-folder-name>.zip in this folder containing only the relevant
# project files. What is left out is listed at the top of the Python part below.
# macOS: double-click make_zip.command. Linux: run ./make_zip.sh (or double-click it
# if your file manager runs scripts). Both files are the same script, and
# make_zip.bat does the same on Windows: keep the lists in all three alike.
# Add the word nopause (./make_zip.sh nopause) to skip the final pause.
cd "$(dirname "$0")" || exit 1
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
import os
import subprocess
import zipfile
from pathlib import Path

# ---- Settings you may want to edit ----------------------------------------------------
EXCLUDED_FOLDERS = {'.git', '.venv', 'venv', 'build', '__pycache__', 'logs', 'style',
                    '.vscode', '.claude', '.github', '.ruff_cache', '.pytest_cache',
                    '.mypy_cache'}
EXCLUDED_FILES = {'.clang-format', '.clang-tidy', '.style.yapf', 'ruff.toml',
                  'cspell.json', 'CLAUDE.md', '.gitignore', '.gitattributes',
                  '.gitmodules', '.DS_Store', 'Thumbs.db'}
# Any folder whose name ends in _data is always left out as well

root = Path.cwd()
name = root.name
zip_path = root / f'{name}.zip'

# ---- 1 List the files ------------------------------------------------------------------
# Inside a git repository: tracked files plus new files that are not git-ignored.
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
kept = []
for file in sorted(set(files)):
    parts = file.split('/')
    if any(part in EXCLUDED_FOLDERS or part.endswith('_data') for part in parts[:-1]):
        continue
    leaf = parts[-1]
    if leaf in EXCLUDED_FILES or leaf == zip_path.name or leaf.endswith('.pyc'):
        continue
    if (root / file).is_file():
        kept.append(file)
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
print(f'Created {zip_path} ({len(kept)} files, {size:.2f} MB)')
PYTHON
    STATUS=$?
fi
if [ "$1" != "nopause" ]; then
    printf 'Press Enter to close...'
    read -r _
fi
exit $STATUS
