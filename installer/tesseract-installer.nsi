# Tesseract OCR Installation Script
# This script installs Tesseract OCR silently

!include "MUI2.nsh"
!include "LogicLib.nsh"

Name "Tesseract OCR Installer"
OutFile "tesseract-installer.exe"
InstallDir "$PROGRAMFILES64\Tesseract-OCR"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Tesseract OCR" SecTesseract
    SetOutPath "$INSTDIR"
    
    ; Extract Tesseract files
    File /r "tesseract\*.*"
    
    ; Add to PATH
    EnVar::SetHKLM
    EnVar::AddValue "Path" "$INSTDIR"
    
    ; Write registry information
    WriteRegStr HKLM "SOFTWARE\Tesseract-OCR" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "SOFTWARE\Tesseract-OCR" "Version" "5.3.3"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Write registry information for add/remove programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tesseract-OCR" "DisplayName" "Tesseract OCR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tesseract-OCR" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tesseract-OCR" "DisplayVersion" "5.3.3"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tesseract-OCR" "Publisher" "UB-Mannheim"
SectionEnd

Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "Path" "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "SOFTWARE\Tesseract-OCR"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tesseract-OCR"
SectionEnd
