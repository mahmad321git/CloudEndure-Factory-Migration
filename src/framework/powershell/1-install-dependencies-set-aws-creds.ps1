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

# Installing dependencies.
powershell.exe ..\migration_execution_server\setup\1-install-dependencies.ps1

# Xlsx Parser.
powershell.exe ..\migration_execution_server\setup\2-parse-xlsx-sheet.ps1 -config_file_name $config_file_name

# Setting up AWS Credentials.
powershell.exe ..\migration_execution_server\setup\3-aws-credentials.ps1

Write-Output ""
Write-Output "Type '.\powershell\2-deploy-infrastructure.ps1' to start deployment script."
