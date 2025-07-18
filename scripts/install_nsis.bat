@echo off
echo NSIS Installer for Windows
echo =========================

echo Checking if NSIS is already installed...
makensis /VERSION >nul 2>&1
if %errorlevel% == 0 (
    echo NSIS is already installed!
    makensis /VERSION
    goto :end
)

echo NSIS not found. Installing...

echo Checking for winget...
winget --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using winget to install NSIS...
    winget install NSIS.NSIS
    if %errorlevel% == 0 (
        echo NSIS installed successfully via winget!
        goto :verify
    ) else (
        echo winget installation failed, trying alternative method...
    )
)

echo Checking for Chocolatey...
choco --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using Chocolatey to install NSIS...
    choco install nsis -y
    if %errorlevel% == 0 (
        echo NSIS installed successfully via Chocolatey!
        goto :verify
    ) else (
        echo Chocolatey installation failed.
    )
)

echo Manual installation required.
echo Please download and install NSIS from: https://nsis.sourceforge.io/Download
echo Or run: python scripts/install_nsis.py
goto :end

:verify
echo Verifying installation...
makensis /VERSION >nul 2>&1
if %errorlevel% == 0 (
    echo NSIS installation verified successfully!
    makensis /VERSION
    echo.
    echo You can now build Windows installers using the build_installer.py script.
) else (
    echo NSIS installation verification failed.
    echo Please restart your terminal or computer and try again.
)

:end
pause 