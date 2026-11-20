Target amd64-unicode
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"
!include "payload.nsh"

!define APP_NAME "G-Helper"
!include "version.nsh"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\GHelper-SourceSetup"

Name "${APP_NAME} ${APP_VER}"
OutFile "output/GHelper-${APP_VER}-Offline-Setup-x64.exe"
InstallDir "$PROGRAMFILES64\G-Helper"
InstallDirRegKey HKLM "${UNINSTALL_KEY}" "InstallLocation"
RequestExecutionLevel admin
CRCCheck force
SetCompressor /SOLID lzma
ShowInstDetails show
ShowUninstDetails show
VIProductVersion "${FILE_VER}"
VIAddVersionKey "ProductName" "G-Helper"
VIAddVersionKey "CompanyName" "G-Helper (seerge)"
VIAddVersionKey "FileDescription" "G-Helper ${APP_VER} Windows x64 Setup"
VIAddVersionKey "FileVersion" "${APP_VER}"
VIAddVersionKey "LegalCopyright" "G-Helper contributors"

!define MUI_ICON "GHelper.ico"
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_NOAUTOCLOSE
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "payload/LICENSE-GHelper.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "English"

LangString Core ${LANG_GERMAN} "G-Helper, .NET Desktop Runtime, ASUS-Treiber und PawnIO"
LangString Core ${LANG_ENGLISH} "G-Helper, .NET Desktop Runtime, ASUS driver and PawnIO"
LangString MenuLink ${LANG_GERMAN} "Verknüpfung im Startmenü"
LangString MenuLink ${LANG_ENGLISH} "Start menu shortcut"
LangString DeskLink ${LANG_GERMAN} "Verknüpfung auf dem Desktop"
LangString DeskLink ${LANG_ENGLISH} "Desktop shortcut"
LangString Unsupported ${LANG_GERMAN} "Dieses Setup benötigt natives Windows x64 ab Windows 10 Build 19045."
LangString Unsupported ${LANG_ENGLISH} "This setup requires native x64 Windows 10 build 19045 or later."
LangString PrereqFailed ${LANG_GERMAN} "Eine Voraussetzung konnte nicht installiert werden. Details stehen im Installationsfenster."
LangString PrereqFailed ${LANG_ENGLISH} "A prerequisite could not be installed. See the installation details."
LangString BadFolder ${LANG_GERMAN} "Bitte wähle einen neuen oder leeren Zielordner. Für einen Ortswechsel einer bestehenden Setup-Installation deinstalliere diese zuerst."
LangString BadFolder ${LANG_ENGLISH} "Choose a new or empty folder. To move an existing Setup installation, uninstall it first."
LangString CopyFailed ${LANG_GERMAN} "G-Helper konnte nicht vollständig geschrieben werden. Prüfe die Ordnerrechte und schließe eine laufende G-Helper-Instanz."
LangString CopyFailed ${LANG_ENGLISH} "G-Helper could not be written completely. Check folder permissions and close any running G-Helper instance."
LangString Legacy ${LANG_GERMAN} "Zuerst die frühere G-Helper-Installation mit mitgelieferten .NET-Bibliotheken über Windows deinstallieren. Einstellungen bleiben erhalten."
LangString Legacy ${LANG_ENGLISH} "First uninstall the previous self-contained G-Helper package through Windows. User settings are preserved."

Function .onInit
  SetRegView 64
  SetShellVarContext all
  ${IfNot} ${IsNativeAMD64}
  ${OrIfNot} ${AtLeastBuild} 19045
    MessageBox MB_OK|MB_ICONSTOP "$(Unsupported)" /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
  ReadRegStr $0 HKLM "${UNINSTALL_KEY}" "InstallLocation"
  ${If} $0 != ""
  ${AndIf} ${FileExists} "$0\hostfxr.dll"
    MessageBox MB_OK|MB_ICONSTOP "$(Legacy)" /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
FunctionEnd

; Erlaubt Wiederinstallation am registrierten Ort. Fremde Dateien bleiben geschützt.
Function ValidateTarget
  ClearErrors
  ReadRegStr $0 HKLM "${UNINSTALL_KEY}" "InstallLocation"
  ${If} $0 == $INSTDIR
    Return
  ${EndIf}
  ${If} $0 != ""
    SetErrors
    Return
  ${EndIf}
  ClearErrors
  FindFirst $0 $1 "$INSTDIR\*"
  ${IfNot} ${Errors}
    ${Do}
      ${If} $1 != "."
      ${AndIf} $1 != ".."
        FindClose $0
        SetErrors
        Return
      ${EndIf}
      FindNext $0 $1
    ${LoopUntil} ${Errors}
    FindClose $0
  ${EndIf}
  ClearErrors
FunctionEnd

Function .onVerifyInstDir
  Call ValidateTarget
  ${If} ${Errors}
    Abort
  ${EndIf}
FunctionEnd

Function InstallPrerequisites
  InitPluginsDir
  ClearErrors
  SetOutPath "$PLUGINSDIR"
  File "RuntimeSetup.exe"
  File "AsusSetup.exe"
  File "PawnIO_setup.exe"
  File "prerequisites.json"
  File "install-prerequisites.ps1"
  ${If} ${Errors}
    StrCpy $0 "extract-error"
  ${Else}
    nsExec::ExecToLog '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$PLUGINSDIR\install-prerequisites.ps1"'
    Pop $0
  ${EndIf}
  Delete "$PLUGINSDIR\RuntimeSetup.exe"
  Delete "$PLUGINSDIR\AsusSetup.exe"
  Delete "$PLUGINSDIR\PawnIO_setup.exe"
  Delete "$PLUGINSDIR\prerequisites.json"
  Delete "$PLUGINSDIR\install-prerequisites.ps1"
  ${If} $0 == "3010"
    SetRebootFlag true
  ${ElseIf} $0 != "0"
    DetailPrint "Prerequisites exit code: $0"
    MessageBox MB_OK|MB_ICONSTOP "$(PrereqFailed)" /SD IDOK
    SetErrorLevel 2
    Abort
  ${EndIf}
FunctionEnd

Section "$(Core)"
  SectionIn RO
  ; Erneute Zielprüfung ist auch für /S und /D notwendig.
  Call ValidateTarget
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONSTOP "$(BadFolder)" /SD IDOK
    SetErrorLevel 1
    Abort
  ${EndIf}
  Call InstallPrerequisites
  ClearErrors
  !insertmacro CopyGHelperPayload
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONSTOP "$(CopyFailed)" /SD IDOK
    SetErrorLevel 3
    Abort
  ${EndIf}
  SetOutPath "$INSTDIR"
  WriteUninstaller "$INSTDIR\GHelper-Uninstall.exe"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayName" "G-Helper"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayVersion" "${APP_VER}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "Publisher" "G-Helper (seerge)"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\GHelper.exe"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\GHelper-Uninstall.exe"'
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoRepair" 1
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONSTOP "$(CopyFailed)" /SD IDOK
    SetErrorLevel 3
    Abort
  ${EndIf}
SectionEnd

Section "$(MenuLink)" MenuShortcut
  CreateDirectory "$SMPROGRAMS\G-Helper"
  CreateShortCut "$SMPROGRAMS\G-Helper\G-Helper.lnk" "$INSTDIR\GHelper.exe"
SectionEnd

Section /o "$(DeskLink)" DesktopShortcut
  CreateShortCut "$DESKTOP\G-Helper.lnk" "$INSTDIR\GHelper.exe"
SectionEnd

Function .onInstSuccess
  IfRebootFlag 0 +2
  SetErrorLevel 3010
FunctionEnd

Section "Uninstall"
  SetRegView 64
  SetShellVarContext all
  ; Nur die konkret installierten Dateien entfernen. Benutzerdaten und PawnIO bleiben erhalten.
  !insertmacro RemoveGHelperPayload
  Delete /REBOOTOK "$INSTDIR\GHelper-Uninstall.exe"
  Delete "$SMPROGRAMS\G-Helper\G-Helper.lnk"
  RMDir "$SMPROGRAMS\G-Helper"
  Delete "$DESKTOP\G-Helper.lnk"
  DeleteRegKey HKLM "${UNINSTALL_KEY}"
  RMDir /REBOOTOK "$INSTDIR"
SectionEnd
