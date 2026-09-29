; Public beta installer. Core remains per-user and does not alter WoW files.
#ifndef SourceDir
  #error SourceDir must name the packaged DpsLab directory
#endif
#ifndef OutputDir
  #error OutputDir must name an existing output directory
#endif

[Setup]
AppId={{E6390355-CCB4-42EE-8E53-5A493E6AE4DA}
AppName=DpsFoundry Core
AppVersion=0.2.0-beta.1
AppPublisher=DpsFoundry contributors
DefaultDirName={autopf}\DpsFoundry Core
DefaultGroupName=DpsFoundry Core
DisableProgramGroupPage=yes
LicenseFile={#SourceDir}\_internal\LICENSE
SetupIconFile={#SourceDir}\_internal\dpslab\assets\dpsfoundry-core.ico
OutputDir={#OutputDir}
OutputBaseFilename=DpsFoundry-Core-0.2.0-beta.1-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayName=DpsFoundry Core
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "pt_BR"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceDir}\_internal\DpsLabAddon\*"; DestDir: "{app}\DpsLabAddon"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DpsFoundry Core"; Filename: "{app}\DpsLab.exe"; IconFilename: "{app}\DpsLab.exe"
Name: "{autodesktop}\DpsFoundry Core"; Filename: "{app}\DpsLab.exe"; IconFilename: "{app}\DpsLab.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\DpsLab.exe"; Description: "Launch DpsFoundry Core"; Flags: nowait postinstall skipifsilent
