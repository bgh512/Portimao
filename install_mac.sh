#!/bin/sh
# Installs the Portimao Mac app in the user's own Applications folder and opens it. Paste
# this line into Terminal (no password is asked, and macOS shows no warning, as curl
# puts no download flag on what it fetches):
#     curl -fsSL https://raw.githubusercontent.com/bgh512/Portimao/main/install_mac.sh | bash
# Run again, it puts the newest version in place of the one there. Everything is in
# functions and main is called on the last line, so a download cut off half-way runs
# nothing; nothing is read from the keyboard, as the script itself comes in that way.
# --no-open installs without opening the app (launchers/mac_app_mover.py uses it).

# ---- CONSTANTS ----
# PORTIMAO_RELEASE_URL replaces the download address in the tests
RELEASE_URL="${PORTIMAO_RELEASE_URL:-https://github.com/bgh512/Portimao/releases/latest/download}"
# the zips the Mac check puts on the Releases page (.github/workflows/mac_check.yml)
APPLE_SILICON_ZIP='Portimao-mac-apple-silicon.zip'
INTEL_ZIP='Portimao-mac-intel.zip'
APPLICATIONS="$HOME/Applications"
APP="$APPLICATIONS/Portimao.app"
OLDEST_MACOS=14  # the numpy and scipy builds the app carries need macOS 14
WORK=''  # the hidden download folder, made by main


# ---- INSTALL HELPERS ----


# ---- _cleaner ----
# Deletes the hidden download folder, with the old app when it was replaced; run however
# the script ends.
_cleaner() {
    if [ -n "$WORK" ]; then
        rm -rf "$WORK"
    fi
}


# ---- _downloader ----
# Downloads the zip of the app; shows curl's progress bar when Terminal shows it.
_downloader() {
    if [ -t 2 ]; then
        curl -fL --progress-bar --connect-timeout 20 --speed-limit 1000 --speed-time 60 \
            -o "$2" "$1"
    else
        curl -fsSL --connect-timeout 20 --speed-limit 1000 --speed-time 60 -o "$2" "$1"
    fi
}


# ---- _failer ----
# Prints one sentence that says what went wrong and what to do, then stops.
_failer() {
    printf '%s\n' "$1" >&2
    exit 1
}


# ---- _mac_checker ----
# Stops unless this is a Mac with macOS 14 or newer; an unreadable version is let through.
_mac_checker() {
    if [ "$(uname -s 2>/dev/null)" != 'Darwin' ]; then
        _failer 'This line installs Portimao on a Mac: on Windows and Linux, follow the README instead.'
    fi
    version="$(sw_vers -productVersion 2>/dev/null)"
    major="${version%%.*}"
    case "$major" in
        '' | *[!0-9]*) return ;;
    esac
    if [ "$major" -lt "$OLDEST_MACOS" ]; then
        _failer "Portimao needs macOS $OLDEST_MACOS or newer, and this Mac has macOS $version: update macOS (System Settings > General > Software Update), then paste the line again."
    fi
}


# ---- _open_checker ----
# Stops when Portimao is open from the place it is installed to.
_open_checker() {
    if pgrep -f "$APP/Contents/MacOS/" >/dev/null 2>&1; then
        _failer 'Portimao is open: close it (Cmd + Q), then paste the line again.'
    fi
}


# ---- _version_reader ----
# Gives the version of the installed app from its Info.plist, or nothing.
_version_reader() {
    plutil -extract CFBundleShortVersionString raw -o - "$APP/Contents/Info.plist" 2>/dev/null
}


# ---- _zip_namer ----
# Names the zip for this Mac's chip; an Apple Silicon Mac is found under Rosetta too.
_zip_namer() {
    if [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = '1' ]; then
        printf '%s\n' "$APPLE_SILICON_ZIP"
    else
        printf '%s\n' "$INTEL_ZIP"
    fi
}


# ---- MAIN FUNCTIONS ----


# ---- app_fetcher ----
# Downloads the zip for this Mac into the hidden folder and unpacks it with ditto, which
# keeps the app's links and signature; stops when the app is not whole.
app_fetcher() {
    zip_name="$(_zip_namer)"
    case "$zip_name" in
        "$APPLE_SILICON_ZIP") chip='Apple Silicon' ;;
        *) chip='Intel' ;;
    esac
    printf '%s\n' "Downloading Portimao for $chip Macs ..."
    if ! _downloader "$RELEASE_URL/$zip_name" "$WORK/$zip_name"; then
        _failer 'Portimao could not be downloaded: check the internet connection, then paste the line again.'
    fi
    printf '%s\n' 'Unpacking it ...'
    mkdir -p "$WORK/unpacked"
    if ! ditto -x -k "$WORK/$zip_name" "$WORK/unpacked" \
        || [ ! -f "$WORK/unpacked/Portimao.app/Contents/Info.plist" ] \
        || [ ! -f "$WORK/unpacked/Portimao.app/Contents/MacOS/Portimao" ]; then
        _failer 'The download was not a whole Portimao app: paste the line again.'
    fi
}


# ---- app_opener ----
# Opens the app as a click does, passing on the check switch when it is set (the Mac check
# follows the app through to its self-test).
app_opener() {
    if [ -n "$PORTIMAO_SELF_TEST" ]; then
        open -n --env "PORTIMAO_SELF_TEST=$PORTIMAO_SELF_TEST" "$APP"
    else
        open "$APP"
    fi
}


# ---- app_placer ----
# Puts the new app in place; the old one is kept in the hidden folder until the new one
# is in, and put back when it cannot be.
app_placer() {
    if [ -e "$APP" ] && ! mv "$APP" "$WORK/old.app"; then
        _failer "The Portimao in $APPLICATIONS could not be replaced: close it (Cmd + Q), then paste the line again."
    fi
    if ! mv "$WORK/unpacked/Portimao.app" "$APP"; then
        if [ -e "$WORK/old.app" ]; then
            mv "$WORK/old.app" "$APP"
        fi
        _failer "Portimao could not be put in $APPLICATIONS: check that you can change that folder, then paste the line again."
    fi
}


# ---- main ----
# Checks the Mac, downloads the app for its chip, puts it in the user's own Applications
# folder and opens it.
main() {
    opens='yes'
    for argument in "$@"; do
        case "$argument" in
            --no-open) opens='no' ;;
        esac
    done
    _mac_checker
    _open_checker
    if ! mkdir -p "$APPLICATIONS"; then
        _failer "The folder $APPLICATIONS could not be made: check that you can change your home folder, then paste the line again."
    fi
    # the download goes beside the app, so putting it in place is only a rename
    if ! WORK="$(mktemp -d "$APPLICATIONS/.Portimao-install.XXXXXX")"; then
        WORK=''
        _failer "A folder for the download could not be made in $APPLICATIONS: check that you can change that folder, then paste the line again."
    fi
    trap _cleaner EXIT
    trap 'exit 1' HUP INT TERM
    app_fetcher
    app_placer
    version="$(_version_reader)"
    if [ "$opens" = 'no' ]; then
        printf '%s\n' "Portimao${version:+ V$version} is installed in your Applications folder."
        return
    fi
    app_opener
    printf '%s\n' "Portimao${version:+ V$version} is installed in your Applications folder and is opening. From now on, open it from Launchpad or Spotlight (Cmd + Space, type Portimao); it updates itself."
}


main "$@"
