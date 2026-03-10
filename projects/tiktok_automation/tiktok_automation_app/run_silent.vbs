Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonwPath = scriptDir & "\.venv\Scripts\pythonw.exe"
appPath = scriptDir & "\app.py"

If Not fso.FileExists(pythonwPath) Then
    MsgBox "Virtual environment not found. Run setup first in tiktok_automation_app.", 48, "Missing .venv"
    WScript.Quit 1
End If

shell.Run """" & pythonwPath & """ """ & appPath & """", 0, False
