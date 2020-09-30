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

# Xlsx Parser.
powershell.exe ..\migration_execution_server\setup\2-parse-xlsx-sheet.ps1 -config_file_name $config_file_name
