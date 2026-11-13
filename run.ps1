# Create venv if needed
if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv..."
    python -m venv .\.venv
    $new = $true
}

# Activate venv if needed
if (-not $env:VIRTUCAL_ENV) {
    Write-Host "Activating virtual enviroment..." -ForegroundColor Cyan
    . .\.venv\Scripts\Activate.ps1
}

# Install requirements if new
if ($new) {
    if (Test-Path "requirements.txt") {
        pip install -r requirements
    } else {
        Write-Host "Unable to find requirements.txt..." -ForegroundColor Cyan
    }
}

# Run the detectors/imputors
Write-Host "Importing stream..." -ForegroundColor Cyan
python stream.py

# Display report
Write-Host " ===== Report ===== " -ForegroundColor Cyan
python report.py