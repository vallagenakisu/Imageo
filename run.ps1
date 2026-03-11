# Photo Editor - Installation and Run Script
# Automated setup for Windows

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Photo Editor - Setup & Run Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Check version
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "✗ Python 3.8+ required. Current version: $major.$minor" -ForegroundColor Red
            Write-Host "Please install Python 3.8 or higher from python.org" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from python.org" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Ask user what they want to do
Write-Host "What would you like to do?" -ForegroundColor Yellow
Write-Host "  1. Install dependencies only" -ForegroundColor White
Write-Host "  2. Install dependencies and run application" -ForegroundColor White
Write-Host "  3. Run application (dependencies already installed)" -ForegroundColor White
Write-Host "  4. Test installation" -ForegroundColor White
Write-Host "  5. Build executable (.exe)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
        Write-Host "Run this script again and choose option 2 or 3 to start the app." -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host ""
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "✓ Dependencies installed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Starting Photo Editor..." -ForegroundColor Yellow
        python main.py
    }
    
    "3" {
        Write-Host ""
        Write-Host "Starting Photo Editor..." -ForegroundColor Yellow
        python main.py
    }
    
    "4" {
        Write-Host ""
        Write-Host "Running installation tests..." -ForegroundColor Yellow
        python test_installation.py
    }
    
    "5" {
        Write-Host ""
        Write-Host "Building executable..." -ForegroundColor Yellow
        .\build.ps1
    }
    
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
