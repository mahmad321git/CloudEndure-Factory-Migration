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
## Shuting down all servers.
################################################################################

Write-Output "Updating project names in Migration Factory..."
& $install_python_folder\python.exe python\start_shutdown_all_servers.py

################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'

