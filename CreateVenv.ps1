$CurrentFolder = Get-Location | Split-Path -Leaf
$EnvFolder = "$CurrentFolder-venv"

Write-Host "Using virtual environment directory of $EnvFolder"
if (Test-Path $EnvFolder) {
    Write-Host "Virtual environment directory already exists. Activating virtual environment."
    Invoke-Expression "./$EnvFolder/Scripts/Activate.ps1"
} else {
    Write-Host "Creating virtual environment at directory $EnvFolder"
    python -m venv $EnvFolder `
        && Invoke-Expression "./$EnvFolder/Scripts/Activate.ps1" `
        && pip install -r requirements.txt `
    
    python setup.py install
}