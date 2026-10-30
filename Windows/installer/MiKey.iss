; MiKey for Windows installer (Inno Setup 6). Per-user, no admin prompt, so the app can update itself.
;   iscc /DVersion=1.0.0 /DArch=x64 /DSrc=..\build\App MiKey.iss
#ifndef Version
  #define Version "0.0.0"
#endif
#ifndef Arch
  #define Arch "x64"
#endif
#ifndef Src
  #define Src "..\build\App"
#endif
[Setup]
; its own id: MiKey and Vikey can be installed side by side
AppId={{DF79296D-7A08-43D3-9B90-BCA92FE3AE08}
AppName=MiKey
AppVersion={#Version}
AppVerName=MiKey {#Version}
AppPublisher=Mike Phung
AppPublisherURL=https://mikey.mikephung.com
AppSupportURL=https://github.com/mikephung/MiKey/issues
AppUpdatesURL=https://github.com/mikephung/MiKey/releases
VersionInfoVersion={#Version}
DefaultDirName={localappdata}\Programs\MiKey
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=.\out
OutputBaseFilename=MiKey-{#Version}-{#Arch}-Setup
SetupIconFile=..\App\MiKey.ico
UninstallDisplayIcon={app}\MiKey.exe
UninstallDisplayName=MiKey
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
CloseApplicationsFilter=MiKey.exe
RestartApplications=no
LicenseFile=..\..\LICENSE
#if Arch == "arm64"
ArchitecturesAllowed=arm64
ArchitecturesInstallIn64BitMode=arm64
#else
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#endif
[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
[Messages]
; the few screens people see, in Vietnamese like the app
WelcomeLabel1=Cài đặt MiKey
WelcomeLabel2=MiKey {#Version} sẽ được cài cho tài khoản của bạn, không cần quyền quản trị.%n%nBấm Next để tiếp tục.
FinishedHeadingLabel=Đã cài xong MiKey
FinishedLabel=MiKey nằm ở khay hệ thống (góc dưới bên phải). Bấm Alt+Z để chuyển Việt ↔ Anh/Đức.
ConfirmUninstall=Gỡ MiKey khỏi máy?
[Files]
Source: "{#Src}\MiKey.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\MiKey"; Filename: "{app}\MiKey.exe"
[Registry]
; the app's own "open at login" entry goes away with the app
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "MiKey"; Flags: uninsdeletevalue dontcreatekey
[Run]
Filename: "{app}\MiKey.exe"; Description: "Mở MiKey"; Flags: nowait postinstall skipifsilent
; a self-update (MiKey runs the installer silently with /RELAUNCH=1) brings the app back
Filename: "{app}\MiKey.exe"; Flags: nowait; Check: ShouldRelaunch
[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/IM MiKey.exe /F"; Flags: runhidden; RunOnceId: "KillMiKey"
[Code]
function ShouldRelaunch: Boolean;
begin
  Result := ExpandConstant('{param:RELAUNCH|0}') = '1';
end;
