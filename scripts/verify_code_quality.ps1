<#
.SYNOPSIS
    Code Quality Verification Script - One-click check for all code issues
.DESCRIPTION
    Runs all code quality checks for frontend and backend:
    - ESLint code check
    - TypeScript type check
    - Unit tests
    - Python code format and type check
.PARAMETER SkipTests
    Skip test execution, only do static checks
.PARAMETER Fix
    Auto-fix fixable issues
.EXAMPLE
    .\verify_code_quality.ps1
    .\verify_code_quality.ps1 -SkipTests
    .\verify_code_quality.ps1 -Fix
#>

param(
    [switch]$SkipTests,
    [switch]$Fix
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Code Quality Verification Tool v1.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()

function Test-Command {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action,
        [string]$SuccessMessage,
        [string]$ErrorMessage
    )
    
    Write-Host "[$Name] " -NoNewline -ForegroundColor Yellow
    Write-Host "Running..."
    
    try {
        & $Action
        if ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE) {
            Write-Host "[$Name] " -NoNewline -ForegroundColor Green
            Write-Host $SuccessMessage
            return $true
        } else {
            Write-Host "[$Name] " -NoNewline -ForegroundColor Red
            Write-Host $ErrorMessage
            $script:errors += "[$Name] $ErrorMessage"
            return $false
        }
    } catch {
        Write-Host "[$Name] " -NoNewline -ForegroundColor Red
        Write-Host "Failed: $_"
        $script:errors += "[$Name] Failed: $_"
        return $false
    }
}

Set-Location $projectRoot

# ==========================================
# Frontend Checks
# ==========================================
Write-Host ""
Write-Host ">>> Frontend Code Check (PC)" -ForegroundColor Magenta
Write-Host "----------------------------------------"

# 1. ESLint Check
if ($Fix) {
    Invoke-Step "ESLint" {
        npm run lint 2>&1
    } "Code check done (auto-fixed)" "Code check found issues"
} else {
    Invoke-Step "ESLint" {
        npx eslint . --max-warnings=0 2>&1
    } "Code check passed" "Code check found issues"
}

# 2. TypeScript Type Check
Invoke-Step "TypeScript" {
    npm run typecheck 2>&1
} "Type check passed" "Type check found issues"

# 3. Frontend Unit Tests
if (-not $SkipTests) {
    Invoke-Step "Vitest" {
        npm run test:run 2>&1
    } "Unit tests passed" "Unit tests failed"
}

# ==========================================
# H5 Frontend Checks
# ==========================================
Write-Host ""
Write-Host ">>> H5 Frontend Code Check" -ForegroundColor Magenta
Write-Host "----------------------------------------"

$h5Path = Join-Path $projectRoot "H5"
if (Test-Path $h5Path) {
    Push-Location $h5Path
    
    Invoke-Step "H5-ESLint" {
        npm run lint 2>&1
    } "H5 code check passed" "H5 code check found issues"
    
    Invoke-Step "H5-TypeScript" {
        npm run typecheck 2>&1
    } "H5 type check passed" "H5 type check found issues"
    
    Pop-Location
}

# ==========================================
# Backend Checks
# ==========================================
Write-Host ""
Write-Host ">>> Backend Code Check (Python)" -ForegroundColor Magenta
Write-Host "----------------------------------------"

$backendPath = Join-Path $projectRoot "backend-python"
if (Test-Path $backendPath) {
    Push-Location $backendPath
    
    # Check Python environment
    $venvPath = Join-Path $backendPath "venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (Test-Path $activateScript) {
        & $activateScript
    }
    
    # 1. Black Format Check
    if (Test-Command "black") {
        if ($Fix) {
            Invoke-Step "Black" {
                black app/ 2>&1
            } "Code formatting done" "Code formatting failed"
        } else {
            Invoke-Step "Black" {
                black --check --diff app/ 2>&1
            } "Format check passed" "Format check found issues"
        }
    } else {
        Write-Host "[Black] " -NoNewline -ForegroundColor Yellow
        Write-Host "Not installed, skipping"
        $script:warnings += "[Black] black not installed, skipping format check"
    }
    
    # 2. isort Check
    if (Test-Command "isort") {
        if ($Fix) {
            Invoke-Step "isort" {
                isort app/ 2>&1
            } "Import sorting done" "Import sorting failed"
        } else {
            Invoke-Step "isort" {
                isort --check-only --diff app/ 2>&1
            } "Import order check passed" "Import order check found issues"
        }
    } else {
        Write-Host "[isort] " -NoNewline -ForegroundColor Yellow
        Write-Host "Not installed, skipping"
        $script:warnings += "[isort] isort not installed, skipping import check"
    }
    
    # 3. Ruff Lint Check (replaces flake8, faster and more features)
    if (Test-Command "ruff") {
        if ($Fix) {
            Invoke-Step "Ruff" {
                ruff check app/ --fix 2>&1
            } "Code lint fixed" "Code lint found issues"
        } else {
            Invoke-Step "Ruff" {
                ruff check app/ 2>&1
            } "Code lint check passed" "Code lint check found issues"
        }
    } else {
        Write-Host "[Ruff] " -NoNewline -ForegroundColor Yellow
        Write-Host "Not installed, skipping"
        $script:warnings += "[Ruff] ruff not installed, skipping lint check"
    }
    
    # 4. mypy Type Check
    if (Test-Command "mypy") {
        Invoke-Step "mypy" {
            mypy app/ --ignore-missing-imports 2>&1
        } "Python type check passed" "Python type check found issues"
    } else {
        Write-Host "[mypy] " -NoNewline -ForegroundColor Yellow
        Write-Host "Not installed, skipping"
        $script:warnings += "[mypy] mypy not installed, skipping type check"
    }
    
    # 5. pytest Tests
    if (-not $SkipTests -and (Test-Command "pytest")) {
        Invoke-Step "pytest" {
            pytest tests/ -v --tb=short 2>&1
        } "Backend unit tests passed" "Backend unit tests failed"
    }
    
    Pop-Location
}

# ==========================================
# Summary Report
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Verification Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($warnings.Count -gt 0) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  [!] $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($errors.Count -gt 0) {
    Write-Host "Errors:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  [X] $err" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Verification FAILED! Found $($errors.Count) issues" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[OK] All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tip: Run this script before committing code" -ForegroundColor Gray
    exit 0
}
