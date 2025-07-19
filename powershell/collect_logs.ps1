# collect_logs.ps1

$logsDir = Join-Path $PSScriptRoot "..\logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    # Export Security log
    $securityLogPath = "$logsDir\security_log_$timestamp.json"
    Get-WinEvent -LogName Security -MaxEvents 100 | ConvertTo-Json -Depth 5 | Out-File -FilePath $securityLogPath -Encoding utf8
    Write-Output "✅ Security logs saved to $securityLogPath"
} else {
    Write-Output "⚠️  Not running as administrator. Skipping Security log collection."
}

# Export System log
$systemLogPath = "$logsDir\system_log_$timestamp.json"
Get-WinEvent -LogName System -MaxEvents 100 | ConvertTo-Json -Depth 5 | Out-File -FilePath $systemLogPath -Encoding utf8
Write-Output "✅ System logs saved to $systemLogPath"

# Export Application log
$applicationLogPath = "$logsDir\application_log_$timestamp.json"
Get-WinEvent -LogName Application -MaxEvents 100 | ConvertTo-Json -Depth 5 | Out-File -FilePath $applicationLogPath -Encoding utf8
Write-Output "✅ Application logs saved to $applicationLogPath"

Write-Host "Logs collected successfully!"
