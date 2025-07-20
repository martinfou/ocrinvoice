; OCR Invoice Parser Windows Installer
; NSIS Script for creating Windows installer

; Include modern UI
!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

; Define application information
!define APP_NAME "OCR Invoice Parser"
!define APP_VERSION "1.3.17"
!define APP_PUBLISHER "OCR Invoice Parser Team"
!define APP_EXE "OCRInvoiceParser.exe"
!define APP_ICON "installer\icon.ico"
!define SETUP_ICON "installer\setup.ico"

; Define installer properties
Name "${APP_NAME}"
OutFile "OCRInvoiceParser-Windows-Setup-${APP_VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"

; Request application privileges
RequestExecutionLevel admin

; Set compression
SetCompressor /SOLID lzma

; Interface Settings
!define MUI_ABORTWARNING
; !define MUI_ICON "${SETUP_ICON}"
; !define MUI_UNICON "${SETUP_ICON}"
; !define MUI_WELCOMEFINISHPAGE_BITMAP "installer\welcome.bmp"
; !define MUI_UNWELCOMEFINISHPAGE_BITMAP "installer\welcome.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "../LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Version information
VIProductVersion "1.3.17.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "Copyright (c) 2024 ${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${APP_NAME} Setup"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${APP_VERSION}"

; Installer sections
Section "Main Application" SecMain
    SectionIn RO
    SetOutPath "$INSTDIR"
    
    ; Copy main executable and dependencies
    File "..\dist\OCRInvoiceParser.exe"
    
    ; Copy configuration files
    SetOutPath "$INSTDIR\config"
    File /r "..\config\*.*"
    
    ; Copy documentation
    SetOutPath "$INSTDIR\docs"
    File /r "..\docs\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Write registry information for add/remove programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; Write registry information for the application
    WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Documentation.lnk" "$INSTDIR\docs\user_guide\getting_started.md" "" "$INSTDIR\docs\user_guide\getting_started.md" 0
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
    
    ; Store the desktop shortcut path in registry for uninstaller
    WriteRegStr HKLM "Software\${APP_NAME}" "DesktopShortcut" "$DESKTOP\${APP_NAME}.lnk"
SectionEnd

Section "Tesseract OCR" SecTesseract
    ; Check if Tesseract is already installed
    ReadRegStr $0 HKLM "SOFTWARE\Tesseract-OCR" "InstallDir"
    ${If} $0 == ""
        ; Tesseract not found, install it silently
        DetailPrint "Installing Tesseract OCR..."
        
        ; Extract Tesseract files to temporary directory
        SetOutPath "$TEMP\tesseract"
        File /r "..\installer\tesseract\*.*"
        
        ; Run Tesseract installer silently with /SILENT flag to avoid prompts
        ExecWait '"$TEMP\tesseract\tesseract-installer.exe" /SILENT /NORESTART'
        
        ; Clean up temporary files
        RMDir /r "$TEMP\tesseract"
        
        DetailPrint "Tesseract OCR installation completed"
    ${Else}
        DetailPrint "Tesseract OCR is already installed - skipping installation"
    ${EndIf}
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove files and directories
    RMDir /r "$INSTDIR\config"
    RMDir /r "$INSTDIR\docs"
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    ; Remove start menu shortcuts
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Documentation.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove desktop shortcut using stored registry value
    ReadRegStr $0 HKLM "Software\${APP_NAME}" "DesktopShortcut"
    ${If} $0 != ""
        Delete "$0"
    ${EndIf}
    
    ; Also try common desktop shortcut names as fallback
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$DESKTOP\OCR Invoice Parser.lnk"
    Delete "$DESKTOP\OCRInvoiceParser.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd

; Function to check if Tesseract is installed
Function CheckTesseract
    ReadRegStr $0 HKLM "SOFTWARE\Tesseract-OCR" "InstallDir"
    ${If} $0 != ""
        ; Tesseract is already installed, unselect the section
        SectionSetFlags ${SecTesseract} 0
        SectionSetText ${SecTesseract} "Tesseract OCR (Already Installed)"
    ${Else}
        ; Tesseract not installed, select the section
        SectionSetFlags ${SecTesseract} ${SF_SELECTED}
        SectionSetText ${SecTesseract} "Tesseract OCR (Required)"
    ${EndIf}
FunctionEnd

; Initialize function
Function .onInit
    Call CheckTesseract
FunctionEnd 