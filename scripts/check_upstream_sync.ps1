#!/usr/bin/env pwsh
# check_upstream_sync.ps1
#
# PowerShell version of check_upstream_sync.sh
# Checks for new commits in upstream and compares with fork tracking file.

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")

Write-Host "================================================"
Write-Host "Upstream Sync Checker (PowerShell)"
Write-Host "================================================"
Write-Host ""

Push-Location $repoRoot
try {
    $hasUpstream = git remote | Select-String -Quiet -Pattern "^upstream$"
    if (-not $hasUpstream) {
        Write-Host "Upstream remote not found. Adding it now..."
        git remote add upstream https://github.com/dobbelina/repository.dobbelina.git
        Write-Host "Upstream remote added"
    }

    Write-Host "Fetching latest commits from upstream..."
    git fetch upstream --quiet

    Write-Host ""
    Write-Host "================================================"
    Write-Host "New Upstream Commits (excluding version bumps)"
    Write-Host "================================================"
    Write-Host ""

    $newCommits = git log upstream/master --not origin/master --oneline --no-merges |
        Where-Object { $_ -notmatch "Bumped to v\." }

    if (-not $newCommits) {
        Write-Host "Fork is up to date with upstream!"
        Write-Host ""
        exit 0
    }

    $count = ($newCommits | Measure-Object).Count
    Write-Host "Found $count new commits"
    Write-Host ""
    Write-Host "| Hash    | Commit Message"
    Write-Host "|---------|---------------"
    foreach ($line in $newCommits) {
        $hash, $message = $line.Split(" ", 2)
        Write-Host "| $hash | $message"
    }

    Write-Host ""
    Write-Host "================================================"
    Write-Host "Integrated Commits Check"
    Write-Host "================================================"
    Write-Host ""

    $syncFile = Join-Path $repoRoot "UPSTREAM_SYNC.md"
    if (Test-Path $syncFile) {
        Write-Host "Checking UPSTREAM_SYNC.md for already integrated commits..."
        Write-Host ""
        foreach ($line in $newCommits) {
            $hash = $line.Split(" ", 2)[0]
            if (Select-String -Path $syncFile -Pattern $hash -Quiet) {
                Write-Host "$hash - Already tracked in UPSTREAM_SYNC.md"
            } else {
                Write-Host "$hash - NEW (not yet integrated)"
            }
        }
    } else {
        Write-Host "UPSTREAM_SYNC.md not found. All commits shown are potentially new."
    }

    Write-Host ""
    Write-Host "================================================"
    Write-Host "Next Steps"
    Write-Host "================================================"
    Write-Host ""
    Write-Host "1. Review commits listed as NEW above"
    Write-Host "2. For each commit you want to integrate:"
    Write-Host "   git cherry-pick -x <hash>"
    Write-Host ""
    Write-Host "3. After cherry-picking, update UPSTREAM_SYNC.md with:"
    Write-Host "   | `<upstream-hash>` | Message | `<fork-hash>` | $(Get-Date -Format yyyy-MM-dd) | Cherry-picked with -x |"
    Write-Host ""
    Write-Host "4. Run tests:"
    Write-Host "   python run_tests.py"
    Write-Host ""
    Write-Host "For detailed analysis, see CHERRY_PICK_ANALYSIS.md"
    Write-Host ""
}
finally {
    Pop-Location
}
