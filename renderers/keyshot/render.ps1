param (
    [string]$DxfPath = "../../sample/floor_plan.dxf",
    [string]$OutputPath = "./render_output.png"
)

# Resolve paths to absolute
$DxfFullPath = Resolve-Path $DxfPath
$OutputFullPath = Join-Path (Get-Location) $OutputPath
$ScriptPath = Join-Path (Get-Location) "render_dxf.py"

Write-Host "--- KeyShot Render Automation ---"
Write-Host "DXF: $DxfFullPath"
Write-Host "Output: $OutputFullPath"
Write-Host "Script: $ScriptPath`n"

# 1. Provide KeyShot executable path
# Check if KeyShot is in PATH
$KeyShotExe = "keyshot.exe"

# If not in PATH, look in common locations
if (-not (Get-Command $KeyShotExe -ErrorAction SilentlyContinue)) {
    # Check common install paths
    $SearchPaths = @(
        "C:\Program Files\KeyShot*\bin\keyshot.exe",
        "C:\Program Files\KeyShot*\keyshot.exe",
        "$env:LOCALAPPDATA\KeyShot*\bin\keyshot.exe",
        "$env:LOCALAPPDATA\KeyShot*\keyshot.exe"
    )
    
    foreach ($path in $SearchPaths) {
        $Found = Get-Item $path -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($Found) {
            $KeyShotExe = $Found.FullName
            break
        }
    }
}

# If still not found, search Program Files properly
if (-not (Get-Command $KeyShotExe -ErrorAction SilentlyContinue) -and -not (Test-Path $KeyShotExe)) {
    Write-Host "KeyShot executable not found automatically. Searching 'C:\Program Files' (this may take a few seconds)..." -ForegroundColor Yellow
    $Found = Get-ChildItem -Path "C:\Program Files\" -Filter "keyshot.exe" -Recurse -ErrorAction SilentlyContinue | 
             Sort-Object -Property LastWriteTime -Descending | Select-Object -First 1
    
    if ($Found) {
        $KeyShotExe = $Found.FullName
    }
}

# FINAL CHECK
if (-not (Get-Command $KeyShotExe -ErrorAction SilentlyContinue) -and -not (Test-Path $KeyShotExe)) {
    Write-Host "`n[ERROR] KeyShot 10+ not found in PATH or standard install folders." -ForegroundColor Red
    Write-Host "[ACTION] Please set the correct path in this script (render.ps1) or add 'keyshot.exe' to your PATH." -ForegroundColor Gray
    exit 1
}

Write-Host "Using KeyShot: $KeyShotExe"

# 2. Execute KeyShot in script mode
# NOTE: Depending on KeyShot version, '-script' flag is used to run Python scripts.
# We pass DXF path and Output path as CLI arguments to the script if supported.
& $KeyShotExe -script $ScriptPath -- "$DxfFullPath" "$OutputFullPath"

Write-Host "`n--- Rendering Complete ---"
