param (
    [Parameter(Mandatory=$true)]
    [string]$InputDxf,
    [Parameter(Mandatory=$false)]
    [string]$OutputPng = "./output.png"
)

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

# Check for pythonocc-core and ezdxf
Write-Host "Checking for dependencies..." -ForegroundColor Cyan
python -c "import OCC; import ezdxf" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: pythonocc-core or ezdxf not found." -ForegroundColor Red
    Write-Host "Please install them using: conda install -c conda-forge pythonocc-core=7.7.0 ezdxf" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Open CASCADE Renderer..." -ForegroundColor Green
Write-Host "Input: $InputDxf"
Write-Host "Output: $OutputPng"

python renderer.py $InputDxf $OutputPng

if ($LASTEXITCODE -eq 0) {
    Write-Host "Rendering completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Rendering failed." -ForegroundColor Red
}
