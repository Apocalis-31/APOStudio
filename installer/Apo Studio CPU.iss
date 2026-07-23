#define MyAppName "APO Studio"
#define MyAppVersion "1.0.5.0"
#define MyAppPublisher "APO Studio"
#define MyAppExeName "APO Studio.exe"

[Setup]
AppId={{A9E2E2D4-5F74-4A9F-9E63-APOSTUDIO002}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
WizardImageFile=..\assets\branding\wizard.bmp
WizardSmallImageFile=..\assets\branding\wizard_small.bmp
LicenseFile=license.txt
InfoAfterFile=changelog.txt
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany=APO Studio
VersionInfoDescription=Assistant de création YouTube
VersionInfoProductName=APO Studio
VersionInfoCopyright=© 2026 APO Studio
UninstallDisplayName=APO Studio (CPU)
PrivilegesRequired=admin

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=output
OutputBaseFilename=APOStudio_Setup_CPU_{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

ArchitecturesInstallIn64BitMode=x64compatible

UninstallDisplayIcon={app}\{#MyAppExeName}

SetupIconFile=..\assets\branding\logo_transparence_AS.ico

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Files]
Source: "..\dist\APO Studio CPU\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\APO Studio"; Filename: "{app}\APO Studio.exe"
Name: "{autodesktop}\APO Studio"; Filename: "{app}\APO Studio.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\APO Studio.exe"; Description: "Lancer APO Studio"; Flags: nowait postinstall skipifsilent
