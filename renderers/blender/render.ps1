param (
    [string]$DxfPath = "../../sample/floor_plan.dxf",
    [string]$OutputPath = "./render_output.png",
    [parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ExtraArgs
)

# Resolve paths to absolute
$DxfFullPath = Resolve-Path $DxfPath
$OutputFullPath = Join-Path (Get-Location) $OutputPath
$ScriptPath = Join-Path (Get-Location) "render_dxf.py"

Write-Host "--- Blender Render Automation ---"
Write-Host "DXF: $DxfFullPath"
Write-Host "Output: $OutputFullPath"
Write-Host "Extra Args: $ExtraArgs"

# Find Blender executable
$BlenderExe = "blender" # Default in PATH

# Check common install locations if not in PATH
if (-not (Get-Command $BlenderExe -ErrorAction SilentlyContinue)) {
    $FoundationPath = "C:\Program Files\Blender Foundation"
    if (Test-Path $FoundationPath) {
        # Search for any blender.exe in subfolders, prioritized by name (descending)
        $FoundBlenders = Get-ChildItem -Path $FoundationPath -Filter "blender.exe" -Recurse -ErrorAction SilentlyContinue | 
                         Sort-Object Name -Descending
        
        if ($FoundBlenders) {
            $BlenderExe = $FoundBlenders[0].FullName
        }
    }
}

if (-not (Get-Command $BlenderExe -ErrorAction SilentlyContinue) -and -not (Test-Path $BlenderExe)) {
    Write-Error "Blender executable not found. Please add Blender to your PATH or install it in 'C:\Program Files\Blender Foundation\'."
    exit 1
}

# Execute Blender in Background mode
& $BlenderExe --background --python $ScriptPath -- $DxfFullPath $OutputFullPath $ExtraArgs

Write-Host "--- Rendering Complete ---"
