# tamper-check.ps1: compares the installed guards with the reviewed copies in
# this folder and says "same" or "different" (see README.md, drill 13).
# Look-only: it changes nothing. Ends with "Result: ALL SAME" (exit code 0)
# or the number of differences (exit code 1).
param(
    [string]$InstalledDir = 'C:\Program Files\ClaudeCode',
    [string]$ReviewedDir = $PSScriptRoot,
    [string]$ProjectDir = 'D:\python\projects\document-manager'
)

$AiName = 'dhawel-22-claude'
$AiEmail = '333494763+dhawel-22-claude@users.noreply.github.com'

# Each installed file, and the reviewed copy in this folder it must match
$Pairs = [ordered]@{
    'managed-settings.json'   = 'managed-settings.json'
    'hooks\check-command.ps1' = 'check-command.ps1'
}

$script:problems = 0
function Report([string]$What, [string]$Result, [bool]$Ok) {
    '{0,-36} {1}' -f $What, $Result
    if (-not $Ok) { $script:problems++ }
}

"Tamper check, $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
"Installed guards: $InstalledDir"
''

# 1. The installed files match the reviewed copies, byte for byte
foreach ($installed in $Pairs.Keys) {
    $path = Join-Path $InstalledDir $installed
    $reviewed = Join-Path $ReviewedDir $Pairs[$installed]
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Report $installed 'MISSING' $false; continue }
    if (-not (Test-Path -LiteralPath $reviewed -PathType Leaf)) { Report $installed "can't find the reviewed copy" $false; continue }
    $a = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
    $b = (Get-FileHash -LiteralPath $reviewed -Algorithm SHA256).Hash
    if ($a -eq $b) { Report $installed "same (fingerprint $($a.Substring(0, 12)))" $true }
    else { Report $installed "DIFFERENT (installed $($a.Substring(0, 12)), reviewed $($b.Substring(0, 12)))" $false }
}

# 2. No other files in the guards folder; an extra settings file could loosen the guards
$expected = @($Pairs.Keys | ForEach-Object { (Join-Path $InstalledDir $_).ToLowerInvariant() })
$extra = @()
if (Test-Path -LiteralPath $InstalledDir) {
    $extra = @(Get-ChildItem -LiteralPath $InstalledDir -Recurse -File -Force |
        Where-Object { $expected -notcontains $_.FullName.ToLowerInvariant() })
}
if ($extra.Count -eq 0) { Report 'Other files in the guards folder' 'none' $true }
foreach ($f in $extra) { Report 'EXTRA FILE' $f.FullName.Substring($InstalledDir.Length).TrimStart('\') $false }

# 3. No Windows registry policy; one would outrank the protected file
foreach ($key in 'HKLM:\SOFTWARE\Policies\ClaudeCode', 'HKCU:\SOFTWARE\Policies\ClaudeCode') {
    $label = 'Registry policy ' + $key.Split(':')[0]
    if (Test-Path -LiteralPath $key) { Report $label 'PRESENT' $false }
    else { Report $label 'none' $true }
}

# 4. This project's Git name and email are the AI account's (guard 4)
$name = [string](& git -C $ProjectDir config --get user.name 2>$null)
$email = [string](& git -C $ProjectDir config --get user.email 2>$null)
if ($name -eq $AiName) { Report 'Project Git name' "$name (the AI account)" $true }
else { Report 'Project Git name' "'$name', NOT the AI account" $false }
if ($email -eq $AiEmail) { Report 'Project Git email' "the AI account's" $true }
else { Report 'Project Git email' "NOT the AI account's" $false }

''
if ($script:problems -eq 0) { 'Result: ALL SAME'; exit 0 }
"Result: $($script:problems) DIFFERENT"
exit 1
