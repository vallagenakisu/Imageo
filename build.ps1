# Photo Editor - Build Script for Windows
# This script creates a standalone .exe file

Write-Host "Photo Editor - Build Script" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = pip list | Select-String "pyinstaller"

if (-not $pyinstallerCheck) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Red
    pip install pyinstaller
} else {
    Write-Host "PyInstaller is already installed." -ForegroundColor Green
}

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host ""

# Build the executable
pyinstaller --name="PhotoEditor" `
            --windowed `
            --onefile `
            --hidden-import=cv2 `
            --hidden-import=numpy `
            --hidden-import=PyQt5 `
            --clean `
            main.py

Write-Host ""
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Your executable is located in:" -ForegroundColor Yellow
Write-Host "  .\dist\PhotoEditor.exe" -ForegroundColor White
Write-Host ""
Write-Host "You can now distribute this .exe file." -ForegroundColor Green
Write-Host "It includes all dependencies and can run without Python installed." -ForegroundColor Green
Write-Host ""

# Open dist folder
$openFolder = Read-Host "Do you want to open the dist folder? (Y/N)"
if ($openFolder -eq "Y" -or $openFolder -eq "y") {
    if (Test-Path ".\dist") {
        explorer.exe ".\dist"
    }
}
