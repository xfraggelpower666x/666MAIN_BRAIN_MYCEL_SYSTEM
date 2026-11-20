Option Explicit

Dim shell, fso, baseDir, scriptPath, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = baseDir & "\bootstrap\bootstrap.ps1"

If Not fso.FileExists(scriptPath) Then
  MsgBox "Bootstrap-Datei fehlt:" & vbCrLf & scriptPath, 16, "666 ChatBackup PC Tool"
  WScript.Quit 1
End If

command = "powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File """ & scriptPath & """ -Mode Run -LaunchHidden"
shell.Run command, 0, False
