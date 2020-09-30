################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
## 
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
################################################################################
param (
     [string] $WaveId,
     [string] $LaunchType
     )

## Reading configs.
$configs = (Get-Content -Raw -Path config\basics.json | ConvertFrom-Json)

## Modify config.json to update the values.
$install_python_folder = $configs.INSTALL_PYTHON_FOLDER

$PSpwd = (Get-Location).Path


################################################################################
## Starting Failover.
################################################################################

Write-Output "Starting failover..."
& $install_python_folder\python.exe python\automate_failover.py --WaveId $WaveId --LaunchType $LaunchType


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'

