Unicode true
!include "MUI2.nsh"
Name "TechPartner Spreadsheet Check"
OutFile "dist\TechPartner-Spreadsheet-Check-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\TechPartner Spreadsheet Check"
RequestExecutionLevel user
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section
 SetOutPath "$INSTDIR"
 File "dist\TechPartner-Spreadsheet-Check.exe"
 File "USER-GUIDE.txt"
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 CreateShortcut "$DESKTOP\TechPartner Spreadsheet Check.lnk" "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 CreateShortcut "$SMPROGRAMS\TechPartner Spreadsheet Check.lnk" "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck" "DisplayName" "TechPartner Spreadsheet Check"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck" "UninstallString" '"$INSTDIR\Uninstall.exe"'
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck" "DisplayVersion" "0.3.0"
SectionEnd
Section "Uninstall"
 Delete "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 Delete "$INSTDIR\USER-GUIDE.txt"
 Delete "$INSTDIR\Uninstall.exe"
 Delete "$DESKTOP\TechPartner Spreadsheet Check.lnk"
 Delete "$SMPROGRAMS\TechPartner Spreadsheet Check.lnk"
 DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck"
 RMDir "$INSTDIR"
SectionEnd
