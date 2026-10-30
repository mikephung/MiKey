#!/bin/zsh
# MiKey release: checks, macOS package, appcast entry, then (with --publish) the git tag and GitHub release.
# Windows installers are built by GitHub Actions (.github/workflows/windows.yml) from the same tag and uploaded
# to the same release.
#
# usage: Tools/release/release_mikey.sh <version>             build + check, nothing is published
#        Tools/release/release_mikey.sh <version> --publish   also tag v<version>, push it, create the GitHub release
#
# Optional (without them the package is unsigned and macOS asks the user to allow it once):
#   MIKEY_SIGN_ID="Developer ID Application: …"   MIKEY_INSTALLER_ID="Developer ID Installer: …"
#   MIKEY_NOTARY_PROFILE=<notarytool keychain profile>
# Update signatures use ~/.mikey/release/ed25519_private.pem (never in the repo).
set -e
cd "$(dirname "$0")/../.."
ROOT=$PWD
VER=$1
[ -n "$VER" ] || { echo "usage: $0 <version> [--publish]"; exit 2; }
PUBLISH=$2
DIST=$ROOT/dist/$VER
# the tag must be the code the files are built from: nothing uncommitted (the test binaries check.sh rebuilds
# and the site's generated feed are ignored)
if [ "$PUBLISH" = "--publish" ] && ! git diff --quiet HEAD -- . ':!Tools/autoswitch/driver/bench' ':!Tools/autoswitch/driver/drvlazy' \
     ':!Tools/autoswitch/touch/touchsim' ':!site-mikey/appcast.xml'; then
  git status --short | grep -v '^??'
  echo "FAIL: commit these changes first, the release tag would not contain them"; exit 1
fi
mkdir -p $DIST

# one version everywhere: project.yml is what the Windows and Linux builds read (CI names their files from it)
if ! grep -q "MARKETING_VERSION: \"$VER\"" project.yml; then
  if [ "$PUBLISH" = "--publish" ]; then echo "FAIL: set MARKETING_VERSION: \"$VER\" in project.yml and commit it first"; exit 1; fi
  sed -i '' "s/MARKETING_VERSION: \"[^\"]*\"/MARKETING_VERSION: \"$VER\"/" project.yml
  echo "project.yml: MARKETING_VERSION set to $VER (commit it before --publish)"
fi

echo "== checks"
Tools/autoswitch/check.sh > $DIST/check.log 2>&1 || { tail -30 $DIST/check.log; echo "FAIL: Tools/autoswitch/check.sh"; exit 1; }
python3 Tools/autoswitch/test/run_de.py > $DIST/de.log 2>&1 || { grep -v ^PASS $DIST/de.log; echo "FAIL: de_cases"; exit 1; }
grep -E "rules:|german:" $DIST/check.log $DIST/de.log

echo "== macOS input method (universal)"
BUILDNUM=$(git rev-list --count HEAD)
UNIVERSAL=1 VERSION=$VER BUILD=$BUILDNUM Tools/build_inputmethod.sh
APP=$ROOT/build/InputMethod/MiKey.app

echo "== package"
# MiKey goes into the logged-in user's ~/Library/Input Methods (installed per user it shows up in the input menu
# at once; in /Library/Input Methods macOS only takes a new input method after the next log in). The package puts
# the app in a staging folder; postinstall copies it for the user and turns it on.
PKGROOT=$ROOT/build/pkgroot
STAGE="Library/Application Support/MiKey"
rm -rf $PKGROOT $ROOT/build/pkgscripts $ROOT/build/pkgres && mkdir -p "$PKGROOT/$STAGE" $ROOT/build/pkgscripts $ROOT/build/pkgres
ditto --noextattr --noqtn --norsrc "$APP" "$PKGROOT/$STAGE/MiKey.app"
# com.apple.provenance (set by the local build tools, not removable) still makes pkgbuild store a few ._
# AppleDouble files; harmless (verified after the build: codesign --verify --deep --strict on the unpacked app)
cat > $ROOT/build/pkgscripts/postinstall <<'SH'
#!/bin/sh
# Runs as root. Copies MiKey from the staging folder into the logged-in user's ~/Library/Input Methods.
STAGED="/Library/Application Support/MiKey/MiKey.app"
LOG=/tmp/mikey-install.log
echo "== $(date) MiKey postinstall" >> $LOG
USER_NAME=$(stat -f %Su /dev/console)
if [ -z "$USER_NAME" ] || [ "$USER_NAME" = "root" ] || [ "$USER_NAME" = "loginwindow" ]; then
  echo "no logged-in user: nothing copied" >> $LOG; exit 0
fi
USER_ID=$(id -u "$USER_NAME")
USER_HOME=$(dscl . -read "/Users/$USER_NAME" NFSHomeDirectory 2>/dev/null | awk '{print $2}')
[ -d "$USER_HOME" ] || { echo "no home for $USER_NAME" >> $LOG; exit 0; }
DEST="$USER_HOME/Library/Input Methods"
# was MiKey the active input source? Then it is again afterwards
SELECT=""
if sudo -u "$USER_NAME" defaults read com.apple.HIToolbox AppleSelectedInputSources 2>/dev/null | grep -q "com.mikey.inputmethod.MiKey"; then SELECT="select"; fi
# the running MiKey (an older version) stops; macOS starts the new one on the next key
pkill -f "Input Methods/MiKey.app/Contents/MacOS/MiKey" 2>/dev/null || true
# 1.0.1 and 1.0.2 installed into /Library/Input Methods: one copy only, the user's
SYS="/Library/Input Methods/MiKey.app"
if [ -d "$SYS" ] && [ "$(defaults read "$SYS/Contents/Info" CFBundleIdentifier 2>/dev/null)" = "com.mikey.inputmethod.MiKey" ]; then
  rm -rf "$SYS"; echo "removed the older copy in /Library/Input Methods" >> $LOG
fi
# the user's copy, replaced in place (same path as before: an upgrade keeps its place in the input menu)
sudo -u "$USER_NAME" mkdir -p "$DEST"
rm -rf "$DEST/MiKey.app"
ditto "$STAGED" "$DEST/MiKey.app"
chown -R "$USER_NAME":staff "$DEST/MiKey.app"
echo "installed $DEST/MiKey.app" >> $LOG
launchctl asuser "$USER_ID" sudo -u "$USER_NAME" "$DEST/MiKey.app/Contents/MacOS/mikey-register" "$DEST/MiKey.app" $SELECT --wait >> $LOG 2>&1 || true
# The input menu in the menu bar only lists a new input method after the next log in (macOS 15; restarting
# TextInputMenuAgent, TextInputSwitcher, SystemUIServer or posting the TIS notifications does not help, tested):
# the closing page asks for one log out on the first install. Updates keep the same path and need none.
exit 0
SH
chmod +x $ROOT/build/pkgscripts/postinstall
# never "relocate": without this, Installer puts the app over any other copy with the same bundle id it finds
pkgbuild --analyze --root $PKGROOT $ROOT/build/pkgcomponents.plist >/dev/null
/usr/libexec/PlistBuddy -c "Set :0:BundleIsRelocatable false" $ROOT/build/pkgcomponents.plist
pkgbuild --root $PKGROOT --component-plist $ROOT/build/pkgcomponents.plist --identifier com.mikey.inputmethod.MiKey.pkg --version $VER \
         --scripts $ROOT/build/pkgscripts --install-location / $ROOT/build/MiKey-component.pkg
# the installer's last page: what to do next, in Vietnamese, German and English
cat > $ROOT/build/pkgres/conclusion.html <<HTML
<!doctype html><html><head><meta charset="utf-8"><style>body{font:13px -apple-system,sans-serif;line-height:1.5}h3{margin:12px 0 4px}.step{font-size:14px}</style></head><body>
<h3>Đã cài xong MiKey $VER</h3>
<p class="step"><b>Lần cài đầu tiên: đăng xuất rồi đăng nhập lại</b> ( › Đăng xuất). Sau đó chọn <b>MiKey</b> trong menu bàn phím trên thanh menu.</p>
<p>Nâng cấp từ bản cũ thì không cần đăng xuất. Chuyển nhanh Việt ↔ Anh/Đức: ⌥Z.</p>
<h3>MiKey $VER ist installiert</h3>
<p class="step"><b>Bei der ersten Installation: einmal ab- und wieder anmelden</b> ( › Abmelden). Danach <b>MiKey</b> im Eingabemenü in der Menüleiste wählen.</p>
<p>Bei einem Update ist kein Abmelden nötig. Umschalten Vietnamesisch ↔ Englisch/Deutsch: ⌥Z.</p>
<h3>MiKey $VER is installed</h3>
<p class="step"><b>First install: log out and back in once</b> ( › Log Out). Then pick <b>MiKey</b> in the input menu in the menu bar.</p>
<p>Updates need no log out. Switch Vietnamese ↔ English/German: ⌥Z.</p>
</body></html>
HTML
cat > $ROOT/build/distribution.xml <<XML
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
  <title>MiKey $VER</title>
  <conclusion file="conclusion.html" mime-type="text/html"/>
  <options customize="never" require-scripts="false" hostArchitectures="arm64,x86_64"/>
  <volume-check><allowed-os-versions><os-version min="13.0"/></allowed-os-versions></volume-check>
  <choices-outline><line choice="mikey"/></choices-outline>
  <choice id="mikey" visible="false"><pkg-ref id="com.mikey.inputmethod.MiKey.pkg"/></choice>
  <pkg-ref id="com.mikey.inputmethod.MiKey.pkg" version="$VER">MiKey-component.pkg</pkg-ref>
</installer-gui-script>
XML
PKG=$DIST/MiKey-$VER-macOS.pkg
SIGNARGS=()
[ -n "$MIKEY_INSTALLER_ID" ] && SIGNARGS=(--sign "$MIKEY_INSTALLER_ID" --timestamp)
productbuild --distribution $ROOT/build/distribution.xml --resources $ROOT/build/pkgres --package-path $ROOT/build $SIGNARGS $PKG
if [ -n "$MIKEY_NOTARY_PROFILE" ] && [ -n "$MIKEY_INSTALLER_ID" ]; then
  xcrun notarytool submit $PKG --keychain-profile "$MIKEY_NOTARY_PROFILE" --wait
  xcrun stapler staple $PKG
  NOTARIZED=yes
fi
(cd $ROOT/build/InputMethod && ditto -c -k --keepParent MiKey.app $DIST/MiKey-$VER-macOS.zip)
# .dmg: what most Mac users expect to download; it holds the installer and a short read-me
DMGSRC=$ROOT/build/dmgsrc
rm -rf $DMGSRC && mkdir -p $DMGSRC
cp $PKG "$DMGSRC/Cài đặt MiKey.pkg"
cp $ROOT/Tools/uninstall_mikey.sh "$DMGSRC/Gỡ MiKey - Uninstall.sh"
printf 'MiKey %s\n\n1. Bấm đúp "Cài đặt MiKey.pkg".\n   Nếu macOS báo không mở được: System Settings > Privacy & Security > Open Anyway.\n2. System Settings > Keyboard > Input Sources > Edit… > + > Vietnamese > MiKey.\n3. Lần cài đầu tiên: đăng xuất rồi đăng nhập lại một lần.\n4. Chọn MiKey trong menu bàn phím trên thanh menu.\n\nGỡ MiKey: mở Terminal, gõ  sh  rồi kéo file \"Gỡ MiKey - Uninstall.sh\" vào, bấm Enter.\n\nHướng dẫn đầy đủ: https://mikey.mikephung.com/download/\n\n---\n1. Double-click "Cài đặt MiKey.pkg" (install MiKey).\n2. System Settings > Keyboard > Input Sources > Edit… > + > Vietnamese > MiKey.\n3. First install: log out and back in once.\n4. Pick MiKey in the input menu.\n' $VER > "$DMGSRC/Đọc trước - Read me.txt"
DMG=$DIST/MiKey-$VER-macOS.dmg
hdiutil create -volname "MiKey $VER" -srcfolder $DMGSRC -fs HFS+ -format UDZO -ov $DMG >/dev/null
[ -n "$MIKEY_SIGN_ID" ] && codesign --sign "$MIKEY_SIGN_ID" --timestamp $DMG
hdiutil verify $DMG >/dev/null && echo "dmg: ok"

echo "== update signature + appcast item"
python3 Tools/release/mikey_appcast.py $VER $DIST

echo
echo "Release $VER is ready in $DIST:"
ls -la $DIST | grep -v log
[ -z "$MIKEY_INSTALLER_ID" ] && echo "NOTE: unsigned package (no Developer ID): users allow it once in System Settings > Privacy & Security > Open Anyway."
[ -z "$NOTARIZED" ] && echo "NOTE: not notarized."

if [ "$PUBLISH" = "--publish" ]; then
  echo "== publish v$VER"
  command -v gh >/dev/null && gh auth status >/dev/null 2>&1 || { echo "gh is not logged in: run 'gh auth login' first"; exit 1; }
  git tag -a "v$VER" -m "MiKey $VER"
  git push origin "v$VER"
  NOTES=$DIST/notes.md
  [ -f $NOTES ] || NOTES=/dev/null
  gh release create "v$VER" $DIST/MiKey-$VER-macOS.dmg $DIST/MiKey-$VER-macOS.pkg $DIST/MiKey-$VER-macOS.zip --title "MiKey $VER" --notes-file $NOTES
  echo "Published. GitHub Actions adds the Windows installers to the release (workflow 'windows')."
else
  echo "Nothing published. Run again with --publish to tag and create the GitHub release."
fi
