#!/bin/sh
# The Mac report: prints, and copies to the clipboard, what is needed to find out why
# Portimao does not start on a Mac. It only reads: nothing on the Mac is changed.
# The Mac app carries a copy and runs it for its Copy details button; the report then
# describes the app. To run the app's copy from Terminal, paste this line:
#     sh ~/Applications/Portimao.app/Contents/Resources/launchers/mac_report.sh
# A Portimao folder run from source (developers, Macs older than macOS 14) has its own
# copy: type sh and a space, drag this file onto the window, press Enter.

# ---- CONSTANTS ----
FOLDER="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)"
REAL_FOLDER="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd -P)"
# Inside the app the report is in Portimao.app/Contents, and the user's own things
# (the logs among them) are in the Portimao folder in the home folder.
case "$FOLDER/" in
    *.app/Contents/*)
        APP="${FOLDER%%.app/Contents*}.app"
        OWN_FOLDER="$HOME/Portimao"
        ;;
    *)
        APP=''
        OWN_FOLDER="$FOLDER"
        ;;
esac
FORM_LINK='https://github.com/bgh512/Portimao/issues/new?template=mac_problem.yml'
LOG_LINES=30
FRAMEWORK='/Library/Frameworks/Python.framework/Versions'
# the packages the launcher checks for (REQUIRED_IMPORTS in launchers/bootstrap.pyw)
PACKAGES='numpy pandas scipy matplotlib xlsxwriter openpyxl PIL'
# asks a Python for its version, its kind of chip and its Tk; Tcl() opens no window
PYTHON_CHECK='import platform
try:
    import tkinter
    tk = "Tk %s (Tcl %s)" % (tkinter.TkVersion,
                             tkinter.Tcl().call("info", "patchlevel"))
except Exception as error:
    tk = "no Tk (%s)" % type(error).__name__
print("Python %s, %s, %s" % (platform.python_version(), platform.machine(), tk))'
# looks for each package without importing it, so nothing is run or written
PACKAGE_CHECK="import importlib.util
missing = [name for name in '$PACKAGES'.split()
           if importlib.util.find_spec(name) is None]
print('missing ' + ', '.join(missing) if missing else 'all there')"


# ---- REPORT HELPERS ----


# ---- _command_finder ----
# Says whether a command exists on this computer.
_command_finder() {
    command -v "$1" >/dev/null 2>&1
}


# ---- _environment_describer ----
# Describes the launcher's own Python environment (.venv_unix) and its packages.
_environment_describer() {
    environment="$FOLDER/.venv_unix"
    if [ ! -d "$environment" ]; then
        printf '%s\n' 'Environment (.venv_unix): not made yet'
        return
    fi
    made_from="$(sed -n 's/^home *= *//p' "$environment/pyvenv.cfg" 2>/dev/null)"
    finished='no'
    if [ -f "$environment/.complete" ]; then
        finished='yes'
    fi
    printf '%s\n' 'Environment (.venv_unix):' \
                  "  made from: ${made_from:-unknown}" \
                  "  set-up finished: $finished" \
                  "  its Python: $(_python_describer "$environment/bin/python")"
    if [ -x "$environment/bin/python" ]; then
        packages="$("$environment/bin/python" -I -B -c "$PACKAGE_CHECK" 2>&1 | tail -n 1)"
        printf '%s\n' "  packages: $packages"
    fi
}


# ---- _file_time_finder ----
# Gives the time a file last changed (Linux's stat first, then the Mac's own).
_file_time_finder() {
    if changed="$(stat -c '%y' "$1" 2>/dev/null)"; then
        printf '%s\n' "$changed" | cut -c 1-16
    else
        stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$1" 2>/dev/null || printf '%s\n' 'unknown'
    fi
}


# ---- _flag_describer ----
# Says whether a file or folder carries macOS's download flag (quarantine).
_flag_describer() {
    if [ ! -e "$1" ]; then
        printf '%s\n' 'missing'
    elif ! _command_finder xattr; then
        printf '%s\n' 'unknown (no xattr here)'
    elif xattr -p com.apple.quarantine "$1" >/dev/null 2>&1; then
        printf '%s\n' 'yes'
    else
        printf '%s\n' 'no'
    fi
}


# ---- _guarded_folder_namer ----
# Names the folder guarded by macOS that a path is in, or says no.
_guarded_folder_namer() {
    case "$1/" in
        "$HOME/Documents/"*) printf '%s\n' 'yes, Documents' ;;
        "$HOME/Desktop/"*) printf '%s\n' 'yes, Desktop' ;;
        "$HOME/Downloads/"*) printf '%s\n' 'yes, Downloads' ;;
        "$HOME/Library/Mobile Documents/"*) printf '%s\n' 'yes, iCloud Drive' ;;
        /Volumes/*) printf '%s\n' 'yes, an external or network drive' ;;
        *) printf '%s\n' 'no' ;;
    esac
}


# ---- _log_shower ----
# Shows the end of one of Portimao's logs, with the time it last changed.
_log_shower() {
    printf '%s\n' "== $1 =="
    if [ -f "$OWN_FOLDER/$1" ]; then
        printf '%s\n' "(last changed $(_file_time_finder "$OWN_FOLDER/$1"); its last $LOG_LINES lines)"
        tail -n "$LOG_LINES" "$OWN_FOLDER/$1"
    else
        printf '%s\n' '(no such file)'
    fi
}


# ---- _python_describer ----
# Asks one Python for its version, chip and Tk; -B and -I keep it from writing anything.
_python_describer() {
    if [ ! -x "$1" ]; then
        printf '%s\n' 'cannot be run'
    elif answer="$("$1" -I -B -c "$PYTHON_CHECK" 2>&1)"; then
        printf '%s\n' "$answer" | tail -n 1
    else
        printf '%s\n' "did not run: $(printf '%s\n' "$answer" | tail -n 1)"
    fi
}


# ---- _python_lister ----
# Lists, one per line, every Python the launcher may try, in the order it tries them.
_python_lister() {
    printf '%s\n' "$FRAMEWORK/Current/bin/python3"
    for python in "$FRAMEWORK"/3.*/bin/python3; do
        printf '%s\n' "$python"
    done
    printf '%s\n' /opt/homebrew/bin/python3 /usr/local/bin/python3
    command -v python3
    printf '%s\n' /usr/bin/python3
}


# ---- _signature_describer ----
# Checks the app's signature (this only reads); gives ok, or codesign's last words.
_signature_describer() {
    if ! _command_finder codesign; then
        printf '%s\n' 'unknown (no codesign here)'
    elif answer="$(codesign --verify --deep --strict "$1" 2>&1)"; then
        printf '%s\n' 'ok'
    else
        printf '%s\n' "$answer" | tail -n 1
    fi
}


# ---- _version_finder ----
# Gives Portimao's version as the program finds it (program_version_reader).
_version_finder() {
    if [ -s "$FOLDER/.style/VERSION" ]; then
        head -n 1 "$FOLDER/.style/VERSION" | tr -d '\r '
    else
        title="$(sed -n '1s/.*(V\([0-9.]*\))[[:space:]]*$/\1/p' "$FOLDER/QUESTION_FLOW.md" 2>/dev/null)"
        printf '%s\n' "${title:-unknown}"
    fi
}


# ---- MAIN FUNCTIONS ----


# ---- app_reporter ----
# Reports where the app is, how macOS sees it and whether its own folder can be written.
app_reporter() {
    copy='no'
    case "$APP" in
        */AppTranslocation/*) copy='yes' ;;
    esac
    own='missing'
    if [ -d "$OWN_FOLDER" ] && [ -w "$OWN_FOLDER" ]; then
        own='there, can be written to'
    elif [ -d "$OWN_FOLDER" ]; then
        own='there, cannot be written to'
    fi
    printf '%s\n' '== Portimao app ==' \
                  "Where: $APP" \
                  "Opened from a temporary copy macOS made: $copy" \
                  "In a folder macOS guards: $(_guarded_folder_namer "$APP")" \
                  "Version: V$(_version_finder)" \
                  "Download flag: $(_flag_describer "$APP")" \
                  "Signature: $(_signature_describer "$APP")" \
                  "Own folder ($OWN_FOLDER): $own"
}


# ---- folder_reporter ----
# Reports where the Portimao folder is, how it was installed and what macOS flags on it.
folder_reporter() {
    printf '%s\n' '== Portimao folder ==' "Where: $FOLDER"
    if [ "$REAL_FOLDER" != "$FOLDER" ]; then
        printf '%s\n' "Really: $REAL_FOLDER"
    fi
    guarded="$(_guarded_folder_namer "$FOLDER")"
    if [ "$guarded" = 'no' ]; then
        guarded="$(_guarded_folder_namer "$REAL_FOLDER")"
    fi
    printf '%s\n' "In a folder macOS guards: $guarded" "Version: V$(_version_finder)"
    if [ -f "$FOLDER/.git/HEAD" ]; then
        branch="$(sed -n 's|^ref: refs/heads/||p' "$FOLDER/.git/HEAD" | tr -d '\r')"
        printf '%s\n' "Installed with git, branch ${branch:-unknown}"
    else
        printf '%s\n' 'Installed from a zip file (not a git clone)'
    fi
    printf '%s\n' 'Download flag:'
    for item in '' run.sh launchers/bootstrap.pyw; do
        printf '%s\n' "  ${item:-the folder}: $(_flag_describer "$FOLDER/$item")"
    done
    desktop_file='missing'
    if [ -f "$HOME/Desktop/Portimao.command" ]; then
        desktop_file='there'
    fi
    printf '%s\n' "Portimao file on the Desktop: $desktop_file"
    _environment_describer
}


# ---- mac_reporter ----
# Reports the macOS version, the chip and the parts of macOS the launcher depends on.
mac_reporter() {
    printf '%s\n' '== Mac =='
    if _command_finder sw_vers; then
        printf '%s\n' "macOS: $(sw_vers -productVersion) (build $(sw_vers -buildVersion))"
    else
        printf '%s\n' "macOS: none, this is not a Mac ($(uname -sr))"
    fi
    chip="$(sysctl -n machdep.cpu.brand_string 2>/dev/null)"
    rosetta='no'
    if [ "$(sysctl -n sysctl.proc_translated 2>/dev/null)" = '1' ]; then
        rosetta='yes'
    fi
    printf '%s\n' "Chip: ${chip:-unknown} ($(uname -m)); Terminal under Rosetta: $rosetta"
    if _command_finder spctl; then
        printf '%s\n' "Gatekeeper: $(spctl --status 2>&1)"
    fi
    if developer="$(xcode-select -p 2>/dev/null)"; then
        printf '%s\n' "Command line developer tools: installed ($developer)"
    else
        printf '%s\n' 'Command line developer tools: not installed'
    fi
}


# ---- main ----
# Makes the report, prints it and, in Terminal, copies it to the clipboard.
main() {
    if [ -z "$FOLDER" ]; then
        printf '%s\n' 'The Portimao folder could not be opened. If macOS asked whether' \
                      'Terminal may open it, click Allow, then run the line again.'
        exit 1
    fi
    report="$(report_maker 2>&1)"
    printf '%s\n\n' "$report"
    # the help goes to the error stream, so the app copies only the report
    if [ -t 1 ] && _command_finder pbcopy; then
        printf '%s\n' "$report" | pbcopy
        printf '%s\n' 'The report is copied. Paste it (Cmd + V) into the "Mac problem" form:' >&2
    else
        printf '%s\n' 'Select the report above, copy it (Cmd + C) and paste it into the' \
                      '"Mac problem" form:' >&2
    fi
    printf '%s\n' "$FORM_LINK" \
                  'It shows where the Portimao folder is, which includes your Mac user' \
                  'name; change it before sending if you prefer.' >&2
}


# ---- pythons_reporter ----
# Reports each Python the launcher may use, with its version, chip and Tk.
pythons_reporter() {
    printf '%s\n' '== Pythons (in the order the launcher tries them) =='
    seen='|'
    found=0
    while IFS= read -r python; do
        case "$seen" in
            *"|$python|"*) continue ;;
        esac
        seen="$seen$python|"
        if [ -z "$python" ] || [ ! -e "$python" ]; then
            continue
        fi
        found=$((found + 1))
        # without the developer tools, Apple's python3 only asks to install them
        if [ "$python" = '/usr/bin/python3' ] && [ "$(uname -s)" = 'Darwin' ] \
            && ! xcode-select -p >/dev/null 2>&1; then
            printf '%s\n' "$python: Apple's stand-in for the developer tools; not run"
            continue
        fi
        link=''
        if [ -L "$python" ]; then
            link=" (-> $(readlink "$python"))"
        fi
        printf '%s\n' "$python$link: $(_python_describer "$python")"
    done <<EOF
$(_python_lister)
EOF
    if [ "$found" -eq 0 ]; then
        printf '%s\n' 'No Python 3 found.'
    fi
}


# ---- report_maker ----
# Puts the parts of the report together: of the app, or of the folder with its launcher.
report_maker() {
    printf '%s\n\n' "Portimao Mac report, $(date '+%Y-%m-%d %H:%M')"
    mac_reporter
    printf '\n'
    if [ -n "$APP" ]; then
        app_reporter
        printf '\n'
        _log_shower logs/launch.log
        printf '\n'
        _log_shower logs/update.log
        printf '\n'
        _log_shower logs/move_to_app.log
        return
    fi
    folder_reporter
    printf '\n'
    pythons_reporter
    printf '\n'
    _log_shower logs/launch.log
    printf '\n'
    _log_shower logs/launcher_errors.log
}


main "$@"
