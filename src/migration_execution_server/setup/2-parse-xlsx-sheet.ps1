param ($config_file_name='config.xlsx')

################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
## 
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
##
## TODO Add proper comments.
################################################################################

## Reading configs.
$configs = (Get-Content -Raw -Path config\basics.json | ConvertFrom-Json)

## Modify config.json to update the values.
$install_python_folder = $configs.INSTALL_PYTHON_FOLDER

$PSpwd = (Get-Location).Path


################################################################################
## Parsing configuration xlsx.
################################################################################

Write-Output 'Parsing config xlsx file...'
& $install_python_folder\python.exe ..\..\parser\excel_parser.py --ExcelFile ..\..\xlsx_config\$config_file_name --OutputFolder config\

Write-Output 'Parsing complete.'


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'
