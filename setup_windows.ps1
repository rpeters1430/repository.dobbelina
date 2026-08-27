<#
    Unified environment setup for Cumination on Windows.
    Run from an elevated PowerShell prompt:

        powershell -ExecutionPolicy Bypass -File "./setup_windows.ps1"

    Installs: Python 3, git, ImageMagick, pngquant (if available), and Python test dependencies.
#>

$ErrorActionPreference = 'Stop'

# Ensure process execution policy allows activating the venv script
try {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force -ErrorAction SilentlyContinue
} catch {
    # Ignore if restricted by policy
}

$repoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $repoRoot) { $repoRoot = Get-Location }

$primaryVenvPath = Join-Path $repoRoot '.venv'
$windowsVenvPath = Join-Path $repoRoot '.venv-win'

function Require-Admin {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Warning 'Script is running without Administrator privileges. Package installation via winget/choco may require elevation.'
    }
}

function Update-SessionPath {
    $machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
    $paths = @()
    if ($machinePath) { $paths += ($machinePath -split ';') }
    if ($userPath) { $paths += ($userPath -split ';') }
    if ($env:Path) { $paths += ($env:Path -split ';') }
    $env:Path = ($paths | Where-Object { [bool]$_ -and (Test-Path $_) } | Select-Object -Unique) -join ';'
}

function Command-Exists {
    param(
        [Parameter(Mandatory = $true)][string]$Name
    )
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-WithWinget {
    param(
        [string]$Id,
        [string]$Name
    )
    if (Command-Exists -Name 'winget') {
        Write-Host "Installing $Name via winget..." -ForegroundColor Cyan
        try {
            & winget install --id $Id -e --source winget --accept-package-agreements --accept-source-agreements
            if ($LASTEXITCODE -eq 0) {
                Update-SessionPath
                return $true
            }
        } catch {
            return $false
        }
    }
    return $false
}

function Install-WithChoco {
    param(
        [string]$Package,
        [string]$Name
    )
    if (Command-Exists -Name 'choco') {
        Write-Host "Installing $Name via Chocolatey..." -ForegroundColor Cyan
        try {
            & choco install -y $Package
            if ($LASTEXITCODE -eq 0) {
                Update-SessionPath
                return $true
            }
        } catch {
            return $false
        }
    }
    return $false
}

function Ensure-Tool {
    param(
        [string]$CheckCommand,
        [string]$WingetId,
        [string]$ChocoName,
        [string]$DisplayName
    )

    Update-SessionPath

    if (Command-Exists -Name $CheckCommand) {
        Write-Host "$DisplayName already installed." -ForegroundColor Green
        return
    }

    $installed = (Install-WithWinget -Id $WingetId -Name $DisplayName) -or (Install-WithChoco -Package $ChocoName -Name $DisplayName)
    
    Update-SessionPath

    if (-not $installed -and -not (Command-Exists -Name $CheckCommand)) {
        throw "Unable to install $DisplayName automatically. Run PowerShell as Administrator or install it manually and re-run the script."
    }
    Write-Host "$DisplayName installed successfully." -ForegroundColor Green
}

function Test-PythonExecutable {
    param(
        [Parameter(Mandatory = $true)][string]$PythonPath
    )

    if (-not (Test-Path $PythonPath)) {
        return $false
    }

    try {
        & $PythonPath --version *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Test-WindowsVenv {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if (-not (Test-Path $Path)) {
        return $false
    }

    $pythonExe = Join-Path $Path 'Scripts\python.exe'
    $activatePs1 = Join-Path $Path 'Scripts\Activate.ps1'

    if (-not (Test-Path $pythonExe) -or -not (Test-Path $activatePs1)) {
        return $false
    }

    return (Test-PythonExecutable -PythonPath $pythonExe)
}

function Ensure-PythonEnv {
    $targetVenv = $primaryVenvPath
    $isLinuxVenv = (Test-Path (Join-Path $primaryVenvPath 'bin\activate')) -or (Test-Path (Join-Path $primaryVenvPath 'bin\python'))

    if ($isLinuxVenv) {
        Write-Host "Detected non-Windows (Linux/WSL) environment in .venv. Using Windows-specific environment in .venv-win." -ForegroundColor Yellow
        $targetVenv = $windowsVenvPath
    }

    # If the target venv directory exists but is incomplete/broken, remove it
    if (Test-Path $targetVenv) {
        if (-not (Test-WindowsVenv -Path $targetVenv)) {
            Write-Warning "Existing virtual environment at '$targetVenv' is invalid or corrupted. Recreating it..."
            Remove-Item -Path $targetVenv -Recurse -Force
        }
    }

    # Create venv if not present
    if (-not (Test-Path $targetVenv)) {
        Write-Host "Creating virtual environment at $targetVenv..." -ForegroundColor Cyan
        python -m venv $targetVenv
        if ($LASTEXITCODE -ne 0 -or -not (Test-WindowsVenv -Path $targetVenv)) {
            throw "Failed to create Python virtual environment at '$targetVenv'."
        }
    }

    $activatePath = Join-Path $targetVenv 'Scripts\Activate.ps1'
    if (-not (Test-Path $activatePath)) {
        throw "Activation script not found at '$activatePath'."
    }

    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    . $activatePath

    $venvPython = Join-Path $targetVenv 'Scripts\python.exe'
    Write-Host "Upgrading pip and installing dependencies..." -ForegroundColor Cyan
    & $venvPython -m pip install --upgrade pip
    
    $reqFile = Join-Path $repoRoot 'requirements-test.txt'
    if (Test-Path $reqFile) {
        & $venvPython -m pip install -r $reqFile
    }

    Write-Host "`nEnvironment ready. Activate later with:`n`n    . `"$activatePath`"`n" -ForegroundColor Green
}

Require-Admin

Ensure-Tool -CheckCommand 'git' -WingetId 'Git.Git' -ChocoName 'git' -DisplayName 'Git'
Ensure-Tool -CheckCommand 'python' -WingetId 'Python.Python.3' -ChocoName 'python' -DisplayName 'Python 3'
Ensure-Tool -CheckCommand 'magick' -WingetId 'ImageMagick.ImageMagick' -ChocoName 'imagemagick' -DisplayName 'ImageMagick'

try {
    Ensure-Tool -CheckCommand 'pngquant' -WingetId 'Kornelski.pngquant' -ChocoName 'pngquant' -DisplayName 'pngquant'
} catch {
    Write-Warning "pngquant could not be installed automatically. The logo scripts will still work without it."
}

Ensure-PythonEnv

Write-Host "Setup complete. Run 'pytest' inside the activated virtual environment to execute tests." -ForegroundColor Green
