
################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
##
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
################################################################################

## Reading basics.
$basics = (Get-Content -Raw -Path config\basics.json | ConvertFrom-Json)

## Modify config.json to update the values.
$download_python_url = $basics.DOWNLOAD_PYTHON_URL
$install_python_folder = $basics.INSTALL_PYTHON_FOLDER

$PSpwd = (Get-Location).Path

################################################################################
## Writing install paths before progressing.
################################################################################

Write-Output ''
Write-Output "PYTHON ~"
Write-Output "      DOWNLOAD URL: $download_python_url"
Write-Output "    INSTALL FOLDER: $install_python_folder"


################################################################################
## Installing `Python 3.7`.
################################################################################

Write-Output ''
Write-Output '####### Python #######'

## Downloading Python setup.
Write-Output 'Downloading Python...'
$InstallerPython = $env:TEMP + "\python_installer.exe";
try {
    Invoke-WebRequest $download_python_url -OutFile $InstallerPython
}
catch {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest $download_python_url -OutFile $InstallerPython
}

## Installing Python.
Write-Output 'Installing Python...'
Start-Process $InstallerPython -argumentlist "/quiet DefaultAllUsersTargetDir=$install_python_folder InstallAllUsers=1 PrependPath=1" -Wait
Remove-Item $InstallerPython;


## Installing required libraries.
Write-Output 'Installing Python libraries...'
& $install_python_folder\python.exe -m pip install requests paramiko boto3 awscli openpyxl

Write-Output 'Python installation complete.'


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'

Write-Output ''
Write-Output 'Installtions complete script complete.'
Write-Output ''
