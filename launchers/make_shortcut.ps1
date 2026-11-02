# Creates the Albufeira shortcuts (Desktop and Start menu). Called by bootstrap.pyw the first time it runs.
# Arguments: the program folder, the program that runs the launcher (pythonw.exe) and the launcher script.
param([string]$Folder, [string]$Target, [string]$Script)
try {
    $icon = Join-Path $Folder 'assets\icon.ico'
    $shell = New-Object -ComObject WScript.Shell
    foreach ($place in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
        if (-not $place -or -not (Test-Path $place)) { continue }
        $link = $shell.CreateShortcut((Join-Path $place 'Albufeira.lnk'))
        $link.TargetPath = $Target
        $link.Arguments = '"' + $Script + '"'
        $link.WorkingDirectory = $Folder
        $link.IconLocation = "$icon,0"
        $link.Description = 'Albufeira: convert chamber .paf files to figures and data'
        $link.Save()
    }
} catch {
    # A missing shortcut must never stop the program from starting.
}
