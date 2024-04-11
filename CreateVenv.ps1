$CurrentFolder = Get-Location | Split-Path -Leaf
$EnvFolder = "$CurrentFolder-venv"
Write-Host "Using virtual environment directory: [$EnvFolder]"

if (Test-Path $EnvFolder -PathType Container) {
    Write-Host "Virtual environment already exists. Activating virtual environment..."
    Invoke-Expression "./$EnvFolder/Scripts/Activate.ps1"
} else {
    Write-Host "Virtual environment not found. Creating virtual environment and installing dependencies..."

    python -m venv $EnvFolder `
        && Invoke-Expression "./$EnvFolder/Scripts/Activate.ps1" `
        && pip install -r requirements.txt

    pip install .
}