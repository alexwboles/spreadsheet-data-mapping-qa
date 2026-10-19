Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!define PRODUCT_ID "TechPartner.SpreadsheetCheck.v1"
!ifndef PACKAGE_OUT
 !define PACKAGE_OUT "dist\TechPartner-Spreadsheet-Check-Setup.exe"
!endif
!ifndef PAYLOAD_EXE
 !define PAYLOAD_EXE "dist\TechPartner-Spreadsheet-Check.exe"
!endif
Name "TechPartner Spreadsheet Check"
OutFile "${PACKAGE_OUT}"
!ifdef QA_ROOT
 InstallDir "${QA_ROOT}"
!else
 InstallDir "$LOCALAPPDATA\Programs\TechPartner Spreadsheet Check"
!endif
RequestExecutionLevel user
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function .onInit
 ; Never honor a command-line /D override for an arbitrary user folder.
 !ifdef QA_ROOT
  StrCpy $INSTDIR "${QA_ROOT}"
 !else
  StrCpy $INSTDIR "$LOCALAPPDATA\Programs\TechPartner Spreadsheet Check"
 !endif
 IfFileExists "$INSTDIR\*" 0 init_done
 ReadINIStr $0 "$INSTDIR\install-marker.ini" "Install" "Product"
 ${If} $0 != "${PRODUCT_ID}"
  IfSilent +2
  MessageBox MB_OK|MB_ICONSTOP "The target folder already exists without a Spreadsheet Check ownership marker. No files were changed. Back up reports and use the previous installer's uninstall option before upgrading."
  SetErrorLevel 2
  Abort
 ${EndIf}
 init_done:
FunctionEnd

Section
 SetShellVarContext current
 ClearErrors
 SetOutPath "$INSTDIR"
 File /oname=TechPartner-Spreadsheet-Check.exe "${PAYLOAD_EXE}"
 File "USER-GUIDE.txt"
 IfErrors install_failed
 WriteINIStr "$INSTDIR\install-marker.ini" "Install" "Product" "${PRODUCT_ID}"
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 !ifdef QA_ROOT
 CreateDirectory "$INSTDIR\qa-shortcuts"
 CreateShortcut "$INSTDIR\qa-shortcuts\TechPartner Spreadsheet Check.lnk" "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 !else
 CreateShortcut "$DESKTOP\TechPartner Spreadsheet Check.lnk" "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 CreateShortcut "$SMPROGRAMS\TechPartner Spreadsheet Check.lnk" "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck" "DisplayName" "TechPartner Spreadsheet Check"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck" "UninstallString" '"$INSTDIR\Uninstall.exe"'
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck" "DisplayVersion" "0.3.1-review"
 !endif
 Goto install_done
 install_failed:
 SetErrorLevel 4
 Abort
 install_done:
SectionEnd

Function un.onInit
 !ifdef QA_ROOT
  ${If} $INSTDIR != "${QA_ROOT}"
 !else
  ${If} $INSTDIR != "$LOCALAPPDATA\Programs\TechPartner Spreadsheet Check"
 !endif
   SetErrorLevel 3
   Abort
  ${EndIf}
 ReadINIStr $0 "$INSTDIR\install-marker.ini" "Install" "Product"
 ${If} $0 != "${PRODUCT_ID}"
  SetErrorLevel 3
  Abort
 ${EndIf}
FunctionEnd

Section "Uninstall"
 SetShellVarContext current
 ; Remove only known application files, never recurse or remove user reports.
 Delete "$INSTDIR\TechPartner-Spreadsheet-Check.exe"
 Delete "$INSTDIR\USER-GUIDE.txt"
 Delete "$INSTDIR\install-marker.ini"
 Delete "$INSTDIR\Uninstall.exe"
 !ifdef QA_ROOT
 Delete "$INSTDIR\qa-shortcuts\TechPartner Spreadsheet Check.lnk"
 RMDir "$INSTDIR\qa-shortcuts"
 !else
 Delete "$DESKTOP\TechPartner Spreadsheet Check.lnk"
 Delete "$SMPROGRAMS\TechPartner Spreadsheet Check.lnk"
 DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TechPartnerSpreadsheetCheck"
 !endif
 RMDir "$INSTDIR"
SectionEnd
