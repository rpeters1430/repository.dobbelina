#!/usr/bin/env pwsh
# cherry_pick_with_tracking.ps1
#
# PowerShell version of cherry_pick_with_tracking.sh
# Cherry-pick commits from upstream and guide updates to UPSTREAM_SYNC.md

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, ValueFromRemainingArguments = $true)]
    [string[]]$UpstreamHashes
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$syncFile = Join-Path $repoRoot "UPSTREAM_SYNC.md"

if (-not $UpstreamHashes -or $UpstreamHashes.Count -eq 0) {
    Write-Host "Usage: .\scripts\cherry_pick_with_tracking.ps1 <upstream-commit-hash> [<upstream-commit-hash> ...]"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\scripts\cherry_pick_with_tracking.ps1 7bbe1c7"
    Write-Host "  .\scripts\cherry_pick_with_tracking.ps1 7bbe1c7 004f106 d92bd04"
    Write-Host ""
    Write-Host "This script will:"
    Write-Host "  1. Cherry-pick the commit(s) with -x flag (adds source reference)"
    Write-Host "  2. Prompt you to update UPSTREAM_SYNC.md"
    Write-Host "  3. Run tests (optional)"
    exit 1
}

Write-Host "================================================"
Write-Host "Cherry-Pick with Tracking (PowerShell)"
Write-Host "================================================"
Write-Host ""

Push-Location $repoRoot
try {
    foreach ($upstreamHash in $UpstreamHashes) {
        Write-Host "Processing: $upstreamHash"
        Write-Host ""

        Write-Host "--- Commit Details ---"
        git show --stat $upstreamHash | Select-Object -First 20
        Write-Host ""

        $reply = Read-Host "Cherry-pick this commit? (y/n)"
        if ($reply -notmatch "^[Yy]$") {
            Write-Host "Skipped $upstreamHash"
            Write-Host ""
            continue
        }

        Write-Host "Cherry-picking $upstreamHash..."
        git cherry-pick -x $upstreamHash
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Cherry-pick failed (likely conflicts)"
            Write-Host ""
            Write-Host "To resolve:"
            Write-Host "  1. Fix conflicts in the affected files"
            Write-Host "  2. git add <resolved-files>"
            Write-Host "  3. git cherry-pick --continue"
            Write-Host ""
            Write-Host "Or abort with:"
            Write-Host "  git cherry-pick --abort"
            exit 1
        }

        $forkHash = (git log -1 --format="%h").Trim()
        $commitMsg = (git log -1 --format="%s").Trim()
        $today = Get-Date -Format "yyyy-MM-dd"

        Write-Host ""
        Write-Host "--- New Fork Commit ---"
        Write-Host "Fork Hash: $forkHash"
        Write-Host "Message: $commitMsg"
        Write-Host ""

        $newEntry = "| `"$upstreamHash`" | $commitMsg | `"$forkHash`" | $today | Cherry-picked with -x |"
        Write-Host "Add this entry to UPSTREAM_SYNC.md:"
        Write-Host ""
        Write-Host $newEntry
        Write-Host ""

        $openReply = Read-Host "Open UPSTREAM_SYNC.md for editing? (y/n)"
        if ($openReply -match "^[Yy]$") {
            if (Test-Path $syncFile) {
                Start-Process notepad.exe $syncFile
            } else {
                Write-Host "UPSTREAM_SYNC.md not found. Please add the entry manually."
                Write-Host $newEntry
            }
        } else {
            Write-Host "Remember to manually update $syncFile with:"
            Write-Host $newEntry
        }

        Write-Host ""
        Write-Host "---"
        Write-Host ""
    }

    Write-Host "================================================"
    Write-Host "All Done!"
    Write-Host "================================================"
    Write-Host ""

    $runTests = Read-Host "Run tests now? (y/n)"
    if ($runTests -match "^[Yy]$") {
        Write-Host "Running tests..."
        python run_tests.py
    }

    Write-Host ""
    Write-Host "Complete! Don't forget to:"
    Write-Host "  1. Review UPSTREAM_SYNC.md"
    Write-Host "  2. Commit the tracking file if you updated it"
    Write-Host "  3. Push your changes"
    Write-Host ""
}
finally {
    Pop-Location
}
