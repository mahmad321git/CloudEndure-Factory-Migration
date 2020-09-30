################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
##
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
##
## TODO Add proper comments.
################################################################################


## Reading basics.
$basics = (Get-Content -Raw -Path config\basics.json | ConvertFrom-Json)

## Modify config.json to update the values.
$install_python_folder = $basics.INSTALL_PYTHON_FOLDER

$PSpwd = (Get-Location).Path


################################################################################
## To be updated
################################################################################

Write-Output 'Starting deployment script script...'
Set-Location ..\..
& $install_python_folder\python.exe aws_infra_deployment_script.py

################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output "Type '.\powershell\3-start_automation_scripts_execution.ps1' to start execution of migration scripts."
