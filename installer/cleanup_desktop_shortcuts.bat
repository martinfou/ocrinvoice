@echo off
REM Cleanup script for OCR Invoice Parser desktop shortcuts
REM This script removes any orphaned desktop shortcuts

echo Cleaning up OCR Invoice Parser desktop shortcuts...

REM Remove desktop shortcuts with various possible names
if exist "%USERPROFILE%\Desktop\OCR Invoice Parser.lnk" (
    del "%USERPROFILE%\Desktop\OCR Invoice Parser.lnk"
    echo Removed: OCR Invoice Parser.lnk
)

if exist "%USERPROFILE%\Desktop\OCRInvoiceParser.lnk" (
    del "%USERPROFILE%\Desktop\OCRInvoiceParser.lnk"
    echo Removed: OCRInvoiceParser.lnk
)

if exist "%PUBLIC%\Desktop\OCR Invoice Parser.lnk" (
    del "%PUBLIC%\Desktop\OCR Invoice Parser.lnk"
    echo Removed: OCR Invoice Parser.lnk (Public Desktop)
)

if exist "%PUBLIC%\Desktop\OCRInvoiceParser.lnk" (
    del "%PUBLIC%\Desktop\OCRInvoiceParser.lnk"
    echo Removed: OCRInvoiceParser.lnk (Public Desktop)
)

echo Desktop shortcut cleanup completed.
echo.
echo If you still see desktop shortcuts, you may need to:
echo 1. Refresh your desktop (F5)
echo 2. Restart Windows Explorer
echo 3. Manually delete the shortcut files
pause 