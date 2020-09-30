################################################################################
## This script is written for PowerShell.
## This script must be executed as an Administrator.
## 
## Run the following if shell execution is Restricted.
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
################################################################################

## Reading configs.
$configs = (Get-Content -Raw -Path config\config.json | ConvertFrom-Json)
$basics = (Get-Content -Raw -Path config\basics.json | ConvertFrom-Json)

## Modify config.json to update the values.
$install_python_folder = $basics.INSTALL_PYTHON_FOLDER

$PSpwd = (Get-Location).Path

################################################################################
## Function to standardize AWS Credential setting process.
################################################################################

function set_aws_credentials {
    param (
        $file,
        $username,
        $profile_name,
        $region
    )

    $has_username_column = $FALSE
    $has_username = $FALSE

    $creds = (Get-Content -Raw -Path $file | ConvertFrom-Csv)
    $creds_columns = $creds | Get-member -MemberType 'NoteProperty' | Select-Object -ExpandProperty 'Name'

    foreach ($column in $creds_columns) {
        if ($column -eq 'User name') {
            $has_username_column = $TRUE            
            break
        }
    }

    if ($has_username_column) {
        foreach ($cred in $creds) {
            if ($username -eq $cred.'User name') {
                $has_username = $TRUE

                & $install_python_folder\python.exe -m awscli configure set aws_access_key_id $cred.'Access key ID' --profile $profile_name
                & $install_python_folder\python.exe -m awscli configure set aws_secret_access_key $cred.'Secret access key' --profile $profile_name
                & $install_python_folder\python.exe -m awscli configure set region $region --profile $profile_name

                break
            }
        }
    }

    if (!$has_username) {
        & $install_python_folder\python.exe -m awscli configure set aws_access_key_id $creds[0].'Access key ID' --profile $profile_name
        & $install_python_folder\python.exe -m awscli configure set aws_secret_access_key $creds[0].'Secret access key' --profile $profile_name
        & $install_python_folder\python.exe -m awscli configure set region $region --profile $profile_name
    }
    
    
}

################################################################################
## Configuring AWS Credentials.
################################################################################

Write-Output ''
Write-Output '####### Configuring AWS Credentials #######'
Write-Output ''

# Setting master credentials...
try {
    Write-Output 'Setting master credentials...'
    set_aws_credentials $configs.AWS_MASTER_CREDS_FILE $configs.AWS_MASTER_USERNAME $configs.AWS_MASTER_PROFILE $configs.AWS_MASTER_REGION
} Catch {
    Write-Host 'Unable to set MASTER credentials...' -BackgroundColor Red
}

# Setting migration credentials...
try {
    Write-Output 'Setting migration credentials...'
    set_aws_credentials $configs.AWS_MIGRATION_CREDS_FILE $configs.AWS_MIGRATION_USERNAME $configs.AWS_MIGRATION_PROFILE $configs.AWS_MIGRATION_REGION
} Catch {
    Write-Host 'Unable to set MIGRATION credentials...' -BackgroundColor Red
}

# Setting dr credentials...
try {
    Write-Output 'Setting dr credentials...'
    set_aws_credentials $configs.AWS_DR_CREDS_FILE $configs.AWS_DR_USERNAME $configs.AWS_DR_PROFILE $configs.AWS_DR_REGION
} Catch {
    Write-Host 'Unable to set DR credentials...' -BackgroundColor Red
}


################################################################################
## Finishing the script.
################################################################################

Set-Location $PSpwd


Write-Output ''
Write-Output '####### COMPLETED #######'
