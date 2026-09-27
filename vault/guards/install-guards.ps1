# install-guards.ps1: copies the reviewed guards from this folder into the
# protected folder (guards plan, build step 3). Ernie runs it in an
# administrator PowerShell; see README.md. Afterwards the tamper check
# must say ALL SAME. undo-guards.ps1 takes the guards out again.
#Requires -RunAsAdministrator
param([string]$Target = 'C:\Program Files\ClaudeCode')

$ErrorActionPreference = 'Stop'
$Source = $PSScriptRoot

# The check script goes in first: once the settings file lands, Claude Code
# starts calling it.
New-Item -ItemType Directory -Path (Join-Path $Target 'hooks') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $Source 'check-command.ps1') -Destination (Join-Path $Target 'hooks\check-command.ps1') -Force
Copy-Item -LiteralPath (Join-Path $Source 'managed-settings.json') -Destination (Join-Path $Target 'managed-settings.json') -Force

"Installed into $Target :"
Get-ChildItem -LiteralPath $Target -Recurse -File | ForEach-Object { '  ' + $_.FullName.Substring($Target.Length).TrimStart('\') }
'Next: run tamper-check.ps1. It must say ALL SAME.'
