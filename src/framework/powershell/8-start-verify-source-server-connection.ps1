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
## Verifying server connection.
################################################################################

Write-Output "Verifying server connection..."
& $install_python_folder\python.exe python\start_verify_server_connection.py


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'

