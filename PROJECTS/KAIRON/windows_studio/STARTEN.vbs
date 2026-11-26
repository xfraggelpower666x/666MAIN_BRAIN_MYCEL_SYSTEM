Option Explicit

' Unsichtbarer Einstieg: kein dauerhaftes CMD- oder PowerShell-Konsolenfenster.
Dim shell, fso, root, ps, script, command, args, i
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(WScript.ScriptFullName)
ps = shell.ExpandEnvironmentStrings("%SystemRoot%") & "\System32\WindowsPowerShell\v1.0\powershell.exe"
script = fso.BuildPath(root, "STARTEN.ps1")

If Not fso.FileExists(ps) Then
    MsgBox "Windows PowerShell 5.1 wurde nicht gefunden.", vbCritical, "666 Universal Buildkit"
    WScript.Quit 1
End If

If Not fso.FileExists(script) Then
    MsgBox "STARTEN.ps1 wurde nicht gefunden:" & vbCrLf & script, vbCritical, "666 Universal Buildkit"
    WScript.Quit 1
End If

command = """" & ps & """ -NoLogo -NoProfile -STA -ExecutionPolicy Bypass -File """ & script & """"
For i = 0 To WScript.Arguments.Count - 1
    command = command & " """ & Replace(WScript.Arguments(i), """", """""") & """"
Next

shell.CurrentDirectory = root
' 0 = Fenster vollständig verstecken; False = asynchron starten.
shell.Run command, 0, False
