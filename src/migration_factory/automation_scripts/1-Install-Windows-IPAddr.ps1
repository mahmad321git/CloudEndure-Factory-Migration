param ($reinstall = "No",
  $API_Token,
  $Servername,
  $username,
  $password)

# Read Server name #

function agent-install {
  Param($key, $account, $creds)
  $ScriptPath = "c:\Scripts\"
  if ($account -ne "") {
    foreach ($machine in $account) {
      if ($reinstall -eq 'Yes' -or ($reinstall -eq 'No' -and (!(Invoke-Command -Credential $creds -ComputerName $machine -ScriptBlock { Test-path "c:\Program Files (x86)\CloudEndure\dist\windows_service_wrapper.exe" })))) {
        write-host "--------------------------------------------------------"
        write-host "- Installing CloudEndure for:   $machine -" -BackgroundColor Blue
        write-host "--------------------------------------------------------"
        if (!(Invoke-Command -Credential $creds -ComputerName $machine -ScriptBlock { Test-path "c:\Scripts\" })) { Invoke-Command -Credential $creds -ComputerName $machine -ScriptBlock { New-Item -Path "c:\Scripts\" -ItemType directory } }
        Invoke-Command -Credential $creds -ComputerName $machine -ScriptBlock { (New-Object System.Net.WebClient).DownloadFile("https://console.cloudendure.com/installer_win.exe", "C:\Scripts\installer_win.exe") }
        $fileexist = Invoke-Command -Credential $creds -ComputerName $machine -ScriptBlock { Test-path "c:\Scripts\installer_win.exe" }
        if ($fileexist -eq "true") {
          $message = "** Successfully downloaded CloudEndure for: " + $machine + " **"
          Write-Host $message
        }
        $command = $ScriptPath + "installer_win.exe -t " + $key + " --no-prompt" + " --skip-dotnet-check"
        $scriptblock2 = $executioncontext.invokecommand.NewScriptBlock($command)
        Invoke-Command -Credential $creds -ComputerName $machine -ScriptBlock $scriptblock2
        write-host
        write-host "** CloudEndure installation finished for : $machine **" 
        write-host
      }
      else {
        $message = "CloudEndure agent already installed for machine: " + $machine + " , please reinstall manually if required"
        write-host $message -BackgroundColor Red
      }
    }
  }
}

$secure_password = ConvertTo-SecureString -String $password -AsPlainText -Force

$creds = New-Object System.Management.Automation.PSCredential $username,$secure_password
agent-install $API_Token $Servername $creds