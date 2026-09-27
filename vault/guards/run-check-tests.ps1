# run-check-tests.ps1: runs every case in check-command-tests.csv against the
# check script and shows pass or fail. Look-only: it changes no files.
# The check script runs in Windows PowerShell 5.1, the same way the app runs it.
param(
    [string]$Script = (Join-Path $PSScriptRoot 'check-command.ps1'),
    [string]$Tests = (Join-Path $PSScriptRoot 'check-command-tests.csv')
)

$HereDir = 'D:\python\projects\document-manager'
$ElsewhereDir = 'D:\python\projects\vsa_edge'
$Shell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'

function Invoke-Check([string]$InputText, [string]$ProjectDir) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Shell
    $psi.Arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$Script`""
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.EnvironmentVariables['CLAUDE_PROJECT_DIR'] = $ProjectDir
    $p = [System.Diagnostics.Process]::Start($psi)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($InputText)
    $p.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
    $p.StandardInput.Close()
    $out = $p.StandardOutput.ReadToEndAsync()
    $err = $p.StandardError.ReadToEndAsync()
    $p.WaitForExit()
    return @{ Code = $p.ExitCode; Out = $out.Result; Err = $err.Result }
}

$results = foreach ($row in (Import-Csv $Tests)) {
    $dir = $ElsewhereDir
    if ($row.where -like 'here*') { $dir = $HereDir }
    if ($row.tool -eq '(broken)') {
        $text = $row.input
    }
    else {
        $toolInput = $null
        if ($row.tool -in @('Bash', 'PowerShell', 'Monitor')) { $toolInput = @{ command = $row.input; description = 'test' } }
        elseif ($row.tool -eq 'Edit') { $toolInput = @{ file_path = $row.input; old_string = 'a'; new_string = 'b' } }
        elseif ($row.tool -eq 'Write') { $toolInput = @{ file_path = $row.input; content = 'test' } }
        elseif ($row.tool -like 'mcp__*') { $toolInput = $row.input | ConvertFrom-Json }
        $event = [ordered]@{
            session_id      = 'test'
            transcript_path = ''
            cwd             = $dir
            permission_mode = $row.mode
            hook_event_name = 'PreToolUse'
            tool_name       = $row.tool
            tool_input      = $toolInput
            tool_use_id     = 'toolu_test'
        }
        if ($row.where -like '*helper*') { $event['agent_id'] = 'test-agent'; $event['agent_type'] = 'general-purpose' }
        $text = $event | ConvertTo-Json -Compress -Depth 5
    }

    $r = Invoke-Check $text $dir
    $actual = 'error'
    $said = $r.Err.Trim()
    if ($r.Code -eq 2) { $actual = 'block' }
    elseif ($r.Code -eq 0 -and -not $r.Out.Trim()) { $actual = 'normal' }
    elseif ($r.Code -eq 0) {
        try {
            $d = ($r.Out | ConvertFrom-Json).hookSpecificOutput
            if ($d.permissionDecision -eq 'ask') { $actual = 'ask' }
            elseif ($d.permissionDecision -eq 'deny') { $actual = 'block' }
            $said = $d.permissionDecisionReason
        }
        catch { $said = $r.Out.Trim() }
    }
    $result = 'FAIL'
    if ($actual -eq $row.expected) { $result = 'PASS' }
    [pscustomobject]@{ id = $row.id; expected = $row.expected; actual = $actual; result = $result; said = $said }
}

$results | Format-Table id, expected, actual, result, said -AutoSize -Wrap
$passed = @($results | Where-Object { $_.result -eq 'PASS' }).Count
"Passed $passed of $(@($results).Count)"
if ($passed -ne @($results).Count) { exit 1 }
