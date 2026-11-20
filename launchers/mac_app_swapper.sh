#!/bin/sh
# Puts the new Portimao app in place of the old one once the old one has closed, then
# opens it. The app starts it itself (utils_shared/app_updater.py), with sh -c and the
# text of this file, so nothing is read from the app being replaced.
# Arguments: the old app's process id, the app, the new app (in the update folder beside
# the app), the update log, then the command that opens the app.

# ---- CONSTANTS ----
WAIT_STEPS=300  # steps of 0.2 s: the old app has 60 s to close


# ---- SWAP HELPERS ----


# ---- _closing_waiter ----
# Waits for the old app to close; fails when it is still open after 60 s.
_closing_waiter() {
    step=0
    while kill -0 "$PID" 2>/dev/null; do
        step=$((step + 1))
        if [ "$step" -gt "$WAIT_STEPS" ]; then
            return 1
        fi
        sleep 0.2
    done
}


# ---- _line_logger ----
# Adds a line, with the date and time, to the update log.
_line_logger() {
    printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >>"$LOG" 2>/dev/null
}


# ---- MAIN FUNCTIONS ----


# ---- app_swapper ----
# Moves the old app into the update folder and the new one into its place; puts the old
# one back when the new one cannot be moved in. Fails when the app was not replaced.
app_swapper() {
    old="$(dirname "$NEW_APP")/old.app"
    rm -rf "$old"
    if ! problem="$(mv "$APP" "$old" 2>&1)"; then
        _line_logger "The old app could not be moved away, so it is kept: $problem"
        return 1
    fi
    if ! problem="$(mv "$NEW_APP" "$APP" 2>&1)"; then
        mv "$old" "$APP"
        _line_logger "The new app could not be moved in, so the old one is put back: $problem"
        return 1
    fi
    _line_logger 'The new app is in place.'
    if ! problem="$(rm -rf "$old" 2>&1)"; then
        _line_logger "The old app could not be deleted; the next start tries again: $problem"
    fi
}


# ---- main ----
# Waits for the old app to close, swaps the apps and opens the app.
main() {
    PID="$1"
    APP="$2"
    NEW_APP="$3"
    LOG="$4"
    shift 4
    if ! _closing_waiter; then
        _line_logger 'The old app did not close within 60 s, so it is kept and nothing is opened.'
        exit 1
    fi
    app_swapper
    # the new app, or the old one when the swap failed
    "$@"
}


main "$@"
