################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
##
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
################################################################################

# Update following if necessary.
$branch = 'develop'

$dependency_folder = 'migration_dependencies'
$download_git_url = 'https://github.com/git-for-windows/git/releases/download/v2.28.0.windows.1/Git-2.28.0-64-bit.exe'
$install_git_folder = "C:\$dependency_folder\git"

$PSpwd = (Get-Location).Path
$base_path = $PSpwd
$xlsx_config_location = 'cloud-migration-automation-framework\xlsx_config'
$script_execution_location = 'cloud-migration-automation-framework\src\framework'


################################################################################
## Installing `git`.
################################################################################

Write-Output ''
Write-Output '####### Installing Git #######'

## Downloading git setup.
Write-Output 'Downloading git...'
$InstallerGit = $env:TEMP + "\git_installer.exe";
try {
   Invoke-WebRequest $download_git_url -OutFile $InstallerGit
}
catch {
   [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
   Invoke-WebRequest $download_git_url -OutFile $InstallerGit
}

## Installing git.
Write-Output 'Installing git...'
Start-Process $InstallerGit -argumentlist " /VERYSILENT /NORESTART /DIR=$install_git_folder /ALLUSERS" -Wait

################################################################################
## Cloning the repository.
################################################################################

if (!(Test-Path $base_path)) {
    New-Item $base_path -ItemType "directory"
} else {
	if ($base_path -ne $PSpwd) {
		Remove-Item -Recurse $base_path
        New-Item $base_path -ItemType "directory"
	}
}

Set-Location $base_path

& $install_git_folder\bin\git.exe clone -b $branch --single-branch "https://@bitbucket.org/northbay/cloud-migration-automation-framework.git"


################################################################################
## Internal use only.
################################################################################

$basics = @{
    INSTALL_PYTHON_FOLDER = "C:\$dependency_folder\Python37"
    DOWNLOAD_PYTHON_URL = 'https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe'
}

################################################################################
## Setting location and install paths.
################################################################################

if (!(Test-Path $base_path\$script_execution_location\config\)) {
    New-Item $base_path\$script_execution_location\config\ -ItemType "directory"
}

Write-Output $basics | ConvertTo-Json | Out-File $base_path\$script_execution_location\config\basics.json -Encoding utf8

Set-Location $base_path\$script_execution_location


Write-Output "Please make sure to copy your config.xlsx file to $base_path\$script_execution_location\config"

Write-Output "Repository cloned..."
Write-Output "Type '.\powershell\1-install-dependencies-set-aws-creds.ps1' to install dependencies."
