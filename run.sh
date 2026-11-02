#!/usr/bin/env bash
# Mac and Linux: starts Albufeira without keeping a terminal open (the first run sets things up).
cd "$(dirname "$0")" || exit 1
PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
    echo "Python 3.9 or newer was not found."
    echo "Mac:   install it from https://www.python.org/downloads/"
    echo "Linux: install it with your package manager, e.g.  sudo apt install python3 python3-venv python3-pip python3-tk"
    exit 1
fi
nohup "$PY" launchers/bootstrap.pyw >/dev/null 2>&1 &
