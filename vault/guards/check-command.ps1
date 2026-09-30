# check-command.ps1: the guards' check script (see README.md in this folder).
# Claude Code runs it before every command and file change (a PreToolUse hook)
# and passes what Claude is about to do as JSON on standard input.
# It answers in one of three ways:
#   block:  exit code 2, with the reason on standard error
#   ask:    JSON on standard output, so the app asks Ernie first
#   normal: no output and exit code 0, so the app's usual rules decide
# Any error blocks: the script fails closed (drill 19).
# Written for Windows PowerShell 5.1, which is built into Windows.

$ErrorActionPreference = 'Stop'

$ProjectRoot = 'd:/python/projects/document-manager'
$GuardsRoot = 'c:/program files/claudecode'
$AiAccount = 'dhawel-22-claude'
$AiEmail = '333494763+dhawel-22-claude@users.noreply.github.com'
$CommandTools = @('Bash', 'PowerShell', 'Monitor')
$FileTools = @('Edit', 'Write', 'NotebookEdit')
$PythonNames = '^(python[0-9.]*|pythonw|py|pip[0-9.]*|pipx|pytest|py\.test|uv|uvx|poetry)$'

function Block([string]$Reason) {
    [Console]::Error.WriteLine("Blocked by the guards: $Reason")
    exit 2
}

function Ask([string]$Reason) {
    $decision = @{
        hookEventName            = 'PreToolUse'
        permissionDecision       = 'ask'
        permissionDecisionReason = "The guards ask first: $Reason"
    }
    [Console]::Out.Write((@{ hookSpecificOutput = $decision } | ConvertTo-Json -Compress -Depth 3))
    exit 0
}

# Forward slashes, and Git Bash's /d/... written as d:/...
function ConvertTo-Plain([string]$Text) {
    if (-not $Text) { return '' }
    return [regex]::Replace($Text.Replace('\', '/'), '(^|[\s"''=(])/([a-zA-Z])/', '$1$2:/')
}

function Test-Inside([string]$Path, [string]$Root) {
    $p = (ConvertTo-Plain $Path).Trim().Trim('"', "'").TrimEnd('/').ToLowerInvariant()
    return ($p -eq $Root) -or $p.StartsWith($Root + '/')
}

# The statements in a command: split at new lines, ;, &&, ||, | and &
function Get-Segments([string]$Text) {
    return @(($Text -split '\r?\n|&&|\|\||;|\||&') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

# The words in a statement, with quotes and outer brackets removed
function Get-Tokens([string]$Segment) {
    $tokens = @()
    foreach ($m in [regex]::Matches($Segment, '(?:[^\s"'']+|"[^"]*"|''[^'']*'')+')) {
        $v = $m.Value.Replace('"', '').Replace("'", '').Trim('(', ')', '{', '}')
        if ($v) { $tokens += $v }
    }
    return ,$tokens
}

# A program's plain name: git for C:/Program Files/Git/cmd/git.exe
function Get-Name([string]$Token) {
    $name = ($Token.Trim('$', '@') -split '/')[-1].ToLowerInvariant()
    if ($name.EndsWith('.exe')) { $name = $name.Substring(0, $name.Length - 4) }
    return $name
}

function Test-GuardsFolder([string]$Text) {
    $t = $Text.ToLowerInvariant()
    return $t.Contains('claudecode') -and ($t -match 'program ?files|programw6432|progra~1')
}

function Test-AdminPrompt([string]$Text) {
    return ($Text -match '-verb\s*[:\s]\s*["'']?runas') -or
           ($Text -match '(^|[\s;&|(''"])(sudo|gsudo|runas)(\.exe)?([\s''"]|$)')
}

# For git: the -c settings, the subcommand and its arguments
function Get-GitCall($Tokens) {
    for ($i = 0; $i -lt $Tokens.Count; $i++) {
        if ((Get-Name $Tokens[$i]) -ne 'git') { continue }
        $configs = @()
        $j = $i + 1
        while ($j -lt $Tokens.Count -and $Tokens[$j].StartsWith('-')) {
            if ($Tokens[$j] -in @('-c', '--git-dir', '--work-tree', '--namespace')) {
                if ($Tokens[$j] -ceq '-c' -and $j + 1 -lt $Tokens.Count) { $configs += $Tokens[$j + 1] }
                $j += 2
            }
            else { $j += 1 }
        }
        if ($j -ge $Tokens.Count) { return $null }
        return @{ Configs = $configs; Sub = $Tokens[$j].ToLowerInvariant(); Args = @($Tokens | Select-Object -Skip ($j + 1)) }
    }
    return $null
}

function Get-GitHubLogin {
    $old = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $out = & gh api user --jq .login 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $out) { return '' }
        return ([string]$out).Trim()
    }
    catch { return '' }
    finally { $ErrorActionPreference = $old }
}

function Test-Push($Git) {
    $a = @($Git.Args)
    $positional = @()
    for ($k = 0; $k -lt $a.Count; $k++) {
        $x = $a[$k]
        if ($x -match '[<>]') { continue }
        if (($x -in @('--force', '--force-if-includes')) -or ($x -like '--force-with-lease*')) { return 'no force pushes (rule 6)' }
        if ($x -in @('--mirror', '--all', '--prune')) { return 'pushes that can overwrite or delete branches on GitHub are blocked (rule 6)' }
        if ($x -eq '--delete') { return 'no deleting branches on GitHub (rule 6)' }
        if ($x -in @('--repo', '--receive-pack', '--exec', '-o', '--push-option')) { $k++; continue }
        if ($x.StartsWith('--')) { continue }
        if ($x -cmatch '^-[a-zA-Z0-9]+$') {
            if ($x.Contains('f')) { return 'no force pushes (rule 6)' }
            if ($x.Contains('d')) { return 'no deleting branches on GitHub (rule 6)' }
            continue
        }
        $positional += $x
    }
    $refspecs = @($positional | Select-Object -Skip 1)
    if ($refspecs.Count -eq 0) { return 'a push must name its branch (rule 6)' }
    foreach ($r in $refspecs) {
        if ($r.StartsWith('+')) { return 'no force pushes (rule 6)' }
        if ($r.StartsWith(':')) { return 'no deleting branches on GitHub (rule 6)' }
        $target = $r
        if ($r.Contains(':')) { $target = $r.Substring($r.LastIndexOf(':') + 1) }
        if ($target -in @('main', 'refs/heads/main')) { return 'no pushing to main; changes reach main only through pull requests (rule 6)' }
        if ($target -eq 'HEAD') { return 'a push must name its branch (rule 6)' }
    }
    $helperReset = $Git.Configs -contains 'credential.helper='
    $helperGh = @($Git.Configs | Where-Object { $_ -eq 'credential.helper=!gh auth git-credential' }).Count -gt 0
    if (-not ($helperReset -and $helperGh)) { return "pushes only with the AI account's sign-in; use the push command in CLAUDE.md (rule 6)" }
    $login = Get-GitHubLogin
    if ($login -ne $AiAccount) { return "the GitHub tool isn't signed in as the AI account (it says '$login') (rule 6)" }
    return $null
}

function Test-Commit($Git) {
    foreach ($x in $Git.Args) {
        if ($x -like '--author*') { return 'commits only as the AI account (rule 6)' }
    }
    foreach ($c in $Git.Configs) {
        if (($c -match '^user\.name=(.*)$') -and ($Matches[1] -ne $AiAccount)) { return 'commits only as the AI account (rule 6)' }
        if (($c -match '^user\.email=(.*)$') -and ($Matches[1] -ne $AiEmail)) { return 'commits only as the AI account (rule 6)' }
    }
    return $null
}

# git config: reading is fine, anything that sets or removes a value is not
function Test-ConfigWrite($A) {
    foreach ($x in $A) {
        if ($x -like '--get*' -or $x -eq '--list' -or $x -ceq '-l') { return $false }
    }
    foreach ($x in $A) {
        if ($x -in @('--unset', '--unset-all', '--add', '--replace-all', '--rename-section', '--remove-section', '--edit', '-e')) { return $true }
    }
    $words = @($A | Where-Object { -not $_.StartsWith('-') -and $_ -notmatch '[<>]' })
    if ($words.Count -eq 0) { return $false }
    if ($words[0] -in @('get', 'list')) { return $false }
    if ($words[0] -in @('set', 'unset', 'rename-section', 'remove-section', 'edit')) { return $true }
    return $words.Count -ge 2
}

function Test-GitBlocked($Tokens) {
    $git = Get-GitCall $Tokens
    if (-not $git) { return $null }
    $a = @($git.Args)
    switch ($git.Sub) {
        'push' { return (Test-Push $git) }
        'commit' { return (Test-Commit $git) }
        'config' { if (Test-ConfigWrite $a) { return 'no changing Git settings; reading them is fine (rule 6)' } }
        'reset' { if ($a -contains '--hard') { return 'git reset --hard throws away unsaved work (rule 6)' } }
        'clean' { foreach ($x in $a) { if ($x -eq '--force' -or $x -cmatch '^-[a-zA-Z]*f') { return 'git clean deletes files (rule 6)' } } }
        'checkout' { if ($a -contains '--' -or $a -contains '.' -or $a -contains '-f' -or $a -contains '--force') { return 'git checkout would throw away unsaved work (rule 6)' } }
        'restore' { if (-not ($a -contains '--staged') -or $a -contains '--worktree' -or $a -contains '-W') { return 'git restore throws away unsaved work (rule 6)' } }
        'stash' { if ($a -contains 'drop' -or $a -contains 'clear') { return 'git stash drop or clear throws away saved work (rule 6)' } }
        'branch' {
            $force = @($a | Where-Object { $_ -ceq '-D' -or $_ -ceq '-f' -or $_ -eq '--force' }).Count -gt 0
            $delete = @($a | Where-Object { $_ -ceq '-d' -or $_ -ceq '-D' -or $_ -eq '--delete' }).Count -gt 0
            if ($force -and $delete) { return 'force-deleting a branch can lose work (rule 6)' }
        }
    }
    return $null
}

function Test-GhBlocked($Tokens) {
    for ($i = 0; $i -lt $Tokens.Count; $i++) {
        if ((Get-Name $Tokens[$i]) -ne 'gh') { continue }
        $rest = @($Tokens | Select-Object -Skip ($i + 1))
        $words = @($rest | Where-Object { -not $_.StartsWith('-') })
        $w0 = ''; $w1 = ''
        if ($words.Count -ge 1) { $w0 = $words[0].ToLowerInvariant() }
        if ($words.Count -ge 2) { $w1 = $words[1].ToLowerInvariant() }
        if ($w0 -eq 'pr' -and $w1 -eq 'merge') { return 'only Ernie merges pull requests (rule 6)' }
        if ($w0 -eq 'repo' -and $w1 -eq 'delete') { return 'deleting the repository on GitHub is blocked (rule 6)' }
        if ($w0 -eq 'auth' -and $w1 -ne 'status') { return 'only the AI account is signed in here; changing the GitHub sign-in is blocked (rule 6)' }
        if ($w0 -eq 'api') {
            $text = $rest -join ' '
            if ($text -match '/merges?\b') { return 'only Ernie merges pull requests (rule 6)' }
            if (($text -match 'git/refs') -and ($text -match '(-x|--method)\s*=?\s*delete')) { return 'no deleting branches on GitHub (rule 6)' }
        }
        return $null
    }
    return $null
}

# Deleting a folder with everything in it: rm -r, Remove-Item -Recurse, rd /s
function Test-Wipe($Tokens) {
    for ($i = 0; $i -lt $Tokens.Count; $i++) {
        $name = Get-Name $Tokens[$i]
        $rest = @($Tokens | Select-Object -Skip ($i + 1))
        if ($name -eq 'rm') {
            foreach ($x in $rest) {
                if (($x -eq '--recursive') -or (($x -match '^-[a-zA-Z]{1,4}$') -and ($x -match 'r'))) { return 'no wiping out a folder (rule 6)' }
            }
        }
        if ($name -in @('remove-item', 'ri', 'rm', 'rmdir', 'rd', 'del', 'erase')) {
            foreach ($x in $rest) {
                if ($x -match '^-r(e(c(u(r(s(e)?)?)?)?)?)?(:\$?true)?$') { return 'no wiping out a folder (rule 6)' }
                if ($x -eq '/s') { return 'no wiping out a folder (rule 6)' }
            }
        }
    }
    return $null
}

# The blocked list (rule 6), including commands quoted inside commands
function Test-Blocked([string]$Segment, [int]$Depth) {
    $tokens = Get-Tokens $Segment
    if ($tokens.Count -eq 0) { return $null }
    if ($Depth -lt 3) {
        foreach ($t in $tokens) {
            if ($t.Contains(' ')) {
                foreach ($inner in Get-Segments $t) {
                    $reason = Test-Blocked $inner ($Depth + 1)
                    if ($reason) { return $reason }
                }
            }
        }
    }
    $reason = Test-GitBlocked $tokens
    if ($reason) { return $reason }
    $reason = Test-GhBlocked $tokens
    if ($reason) { return $reason }
    return (Test-Wipe $tokens)
}

function Test-Python([string]$Text, [int]$Depth) {
    foreach ($segment in Get-Segments $Text) {
        foreach ($t in (Get-Tokens $segment)) {
            if ((Get-Name $t) -match $PythonNames) { return $true }
            if ($t -match '(^|/)\.?venv/(scripts|bin)/') { return $true }
            if ($Depth -lt 3 -and $t.Contains(' ') -and (Test-Python $t ($Depth + 1))) { return $true }
        }
    }
    return $false
}

try {
    $stdin = [Console]::OpenStandardInput()
    $buffer = New-Object System.IO.MemoryStream
    $stdin.CopyTo($buffer)
    $raw = [System.Text.Encoding]::UTF8.GetString($buffer.ToArray())
    if (-not $raw.Trim()) { Block 'the check script got no input, so it stopped the action (drill 19)' }
    $in = $raw | ConvertFrom-Json
    $tool = [string]$in.tool_name
    if (-not $tool) { Block "the check script couldn't tell what Claude is trying, so it stopped the action (drill 19)" }
    $mode = [string]$in.permission_mode
    $toolInput = $in.tool_input

    $command = ''
    if ($tool -in $CommandTools) {
        $command = [string]$toolInput.command
        if (-not $command) { $command = ($toolInput | ConvertTo-Json -Compress -Depth 5) }
    }
    $filePath = ''
    if ($tool -in $FileTools) {
        $filePath = [string]$toolInput.file_path
        if (-not $filePath) { $filePath = [string]$toolInput.notebook_path }
    }
    $plain = ConvertTo-Plain $command

    # Everywhere on this computer (rule 2)
    if ($filePath -and (Test-Inside $filePath $GuardsRoot)) { Block 'the installed guards can only be changed by Ernie (rule 2)' }
    if ($command) {
        if (Test-GuardsFolder $plain) { Block 'the installed guards can only be changed by Ernie (rule 2)' }
        if (Test-AdminPrompt $plain) { Block 'Claude may not start an administrator prompt (rule 2)' }
    }

    $here = (Test-Inside ([string]$in.cwd) $ProjectRoot) -or (Test-Inside ([string]$env:CLAUDE_PROJECT_DIR) $ProjectRoot)

    if (-not $here) {
        # Rule 5: a thread working elsewhere can't change this folder's files (blocked, not asked: drill 20)
        if ($filePath -and (Test-Inside $filePath $ProjectRoot)) { Block 'a thread working elsewhere is changing a file in the document-manager folder (rule 5)' }
        if ($command -and $plain.ToLowerInvariant().Contains($ProjectRoot)) { Block 'a command from a thread working elsewhere names the document-manager folder (rule 5)' }
        exit 0
    }

    # Only inside this folder
    if ($tool -eq 'mcp__ccd_session_mgmt__set_session_permission_mode') { Block 'only Ernie picks the mode (rule 3)' }
    if ($tool -eq 'mcp__ccd_pr__set_auto_merge') { Block 'only Ernie merges; auto-merge stays off (rule 6)' }

    if ($command) {
        if ($plain -match '\bgit_(author|committer)_(name|email)\b') { Block 'commits only as the AI account (rule 6)' }
        foreach ($segment in Get-Segments $plain) {
            $reason = Test-Blocked $segment 0
            if ($reason) { Block $reason }
        }
    }

    if ($mode -ne 'default' -and $mode -ne 'plan') {
        Block "this project runs in Manual mode only, and the mode is '$mode'. Ernie: please pick Manual in the mode selector next to the send button (rule 3)"
    }
    if ($mode -eq 'plan' -and ($command -or $filePath)) { Ask 'in Plan mode every command asks first (rule 3)' }
    if ($command -and (Test-Python $plain 0)) { Ask 'Python asks first in this project (rule 7)' }
    # The desktop app doesn't ask before file changes on its own (drill 1), so the check does
    if ($filePath -and (Test-Inside $filePath $ProjectRoot)) { Ask 'every file change in this project asks first (rule 4)' }
    exit 0
}
catch {
    Block "the check script hit an error ($($_.Exception.Message)), so it stopped the action (drill 19)"
}
