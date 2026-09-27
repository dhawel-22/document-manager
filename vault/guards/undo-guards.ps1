# undo-guards.ps1: takes the guards out of the protected folder, back to how
# things were before build step 3. Ernie runs it in an administrator
# PowerShell; see README.md. Nothing is deleted: the files move to a
# dated backup folder in Ernie's home folder.
#Requires -RunAsAdministrator
param(
    [string]$Target = 'C:\Program Files\ClaudeCode',
    [string]$BackupRoot = $env:USERPROFILE
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Target)) { "Nothing to undo: $Target doesn't exist."; exit 0 }

$Backup = Join-Path $BackupRoot ('guards-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $Backup -Force | Out-Null

# The settings file comes out first, so Claude Code stops calling the check script.
$settings = Join-Path $Target 'managed-settings.json'
if (Test-Path -LiteralPath $settings) { Move-Item -LiteralPath $settings -Destination $Backup }
Get-ChildItem -LiteralPath $Target -Force | Move-Item -Destination $Backup
Remove-Item -LiteralPath $Target

"Guards taken out of $Target."
"The files are kept in $Backup"
