@echo off
rem Creates <project-folder-name>_export.zip in the project root (the folder above
rem .style\) with the project's relevant files, for example to upload to claude.ai. It
rem holds the files git tracks plus new files git is not ignoring, minus the patterns in
rem .style\zipignore. The zip never contains .git, style\, .venv or earlier export
rem zips. make_zip.command (macOS) and make_zip.sh (Linux) do the same, and so does the
rem VS Code task "Make export zip". Add the word nopause to skip the final pause.
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = Get-Content -Raw -LiteralPath '%~f0'; Invoke-Expression $s.Substring($s.IndexOf('#'+'PS#'))"
if /i not "%~1"=="nopause" pause
exit /b
#PS#
$alwaysLeftOut = @('.git', 'style', '.venv', 'venv', '__pycache__', 'node_modules')

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root = (Get-Location).Path
$name = Split-Path -Leaf $root
$zipPath = Join-Path $root "$($name)_export.zip"
$patterns = @()
$ignoreFile = Join-Path (Join-Path $root '.style') 'zipignore'
if (Test-Path -LiteralPath $ignoreFile) {
    $patterns = @(Get-Content -LiteralPath $ignoreFile | ForEach-Object { $_.Trim() } |
                  Where-Object { $_ -and -not $_.StartsWith('#') })
}

function Test-LeftOut([string]$relative) {
    $parts = $relative -split '/'
    $leaf = $parts[$parts.Count - 1]
    $folderParts = @()
    if ($parts.Count -gt 1) { $folderParts = $parts[0..($parts.Count - 2)] }
    foreach ($part in $folderParts) { if ($alwaysLeftOut -contains $part) { return $true } }
    if ($leaf -like '*_export.zip' -or $leaf -like '*.pyc') { return $true }
    $folders = @()
    for ($i = 0; $i -lt $folderParts.Count; $i++) {
        $folders += ($folderParts[0..$i] -join '/')
    }
    foreach ($pattern in $patterns) {
        if ($pattern.EndsWith('/')) {
            $clean = $pattern.Trim('/')
            if ($clean.Contains('/') -or $pattern.StartsWith('/')) {
                foreach ($folder in $folders) { if ($folder -like $clean) { return $true } }
            } else {
                foreach ($part in $folderParts) { if ($part -like $clean) { return $true } }
            }
        } elseif ($relative -like $pattern.TrimStart('/')) {
            return $true
        } elseif (-not $pattern.Contains('/') -and $leaf -like $pattern) {
            return $true
        }
    }
    return $false
}

# ---- 1 List the files ----------------------------------------------------------------
$isRepo = $false
if (Get-Command git -ErrorAction SilentlyContinue) {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
    $isRepo = ($LASTEXITCODE -eq 0)
}
if ($isRepo) {
    $files = @(git -c core.quotepath=false ls-files --cached --others --exclude-standard)
} else {
    $files = @(Get-ChildItem -Recurse -File -Force | ForEach-Object {
        $_.FullName.Substring($root.Length + 1) -replace '\\', '/'
    })
}

# ---- 2 Drop the files that are not needed ---------------------------------------------
$kept = @($files | Sort-Object -Unique | Where-Object {
    -not (Test-LeftOut $_) -and (Test-Path -LiteralPath (Join-Path $root $_) -PathType Leaf)
})
if ($kept.Count -eq 0) {
    Write-Host 'No files to zip.'
    exit 1
}

# ---- 3 Create the zip -----------------------------------------------------------------
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
$archive = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
try {
    foreach ($file in $kept) {
        [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $archive, (Join-Path $root $file), "$name/$file", 'Optimal')
    }
} finally {
    $archive.Dispose()
}
$size = [math]::Round((Get-Item -LiteralPath $zipPath).Length / 1MB, 2)
Write-Host "Created $(Split-Path -Leaf $zipPath) ($($kept.Count) files, $size MB)"
