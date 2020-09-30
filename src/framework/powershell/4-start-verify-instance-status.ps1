################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
## 
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
################################################################################

## Reading configs.
$configs = (Get-Content -Raw -Path config\basics.json | ConvertFrom-Json)

## Modify config.json to update the values.
$install_python_folder = $configs.INSTALL_PYTHON_FOLDER

$PSpwd = (Get-Location).Path


################################################################################
## Updating cloudendure_projectname list in Migration Factory.
################################################################################

Write-Output "Starting Verification of Instance Status..."
& $install_python_folder\python.exe python\start_verify_instance_status.py


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'

