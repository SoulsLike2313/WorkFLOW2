Option Explicit

Dim shell, fso, scriptDir, psScript
Dim repoRoot, branch, commitMessage
Dim cmd
Dim exitCode

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
psScript = fso.BuildPath(scriptDir, "auto_sync.ps1")

repoRoot = ""
branch = ""
commitMessage = ""

If WScript.Arguments.Count > 0 Then repoRoot = WScript.Arguments(0)
If WScript.Arguments.Count > 1 Then branch = WScript.Arguments(1)
If WScript.Arguments.Count > 2 Then commitMessage = WScript.Arguments(2)

cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & psScript & """"

If Len(repoRoot) > 0 Then
    cmd = cmd & " -RepoRoot """ & repoRoot & """"
End If

If Len(branch) > 0 Then
    cmd = cmd & " -Branch """ & branch & """"
End If

If Len(commitMessage) > 0 Then
    cmd = cmd & " -CommitMessage """ & commitMessage & """"
End If

' 0 = hidden window, True = wait until process exits
exitCode = shell.Run(cmd, 0, True)
WScript.Quit exitCode
