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

Write-Output "Updating project names in Migration Factory..."
& $install_python_folder\python.exe python\update_migration_factory_attributes.py


################################################################################
## Starting automation scripts workflow.
################################################################################

Write-Output "Starting Automated Migration Workflow..."
& $install_python_folder\python.exe python\start_automation_scripts_execution.py


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'

