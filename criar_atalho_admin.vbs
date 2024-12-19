Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%") & "\Desktop\Gerenciador de Disco (Admin).lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "pythonw.exe"
oLink.Arguments = """" & WScript.Arguments(0) & """"
oLink.WorkingDirectory = oWS.ExpandEnvironmentStrings("%USERPROFILE%") & "\Documents\Projeto\BLACKBOX"
oLink.Description = "Gerenciador de Disco (Executar como Administrador)"
oLink.IconLocation = "pythonw.exe,0"
oLink.Save
