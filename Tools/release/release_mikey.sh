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
mkdir -p $DIST

echo "== checks"
Tools/autoswitch/check.sh > $DIST/check.log 2>&1 || { tail -30 $DIST/check.log; echo "FAIL: Tools/autoswitch/check.sh"; exit 1; }
python3 Tools/autoswitch/test/run_de.py > $DIST/de.log 2>&1 || { grep -v ^PASS $DIST/de.log; echo "FAIL: de_cases"; exit 1; }
grep -E "rules:|german:" $DIST/check.log $DIST/de.log

echo "== macOS input method (universal)"
BUILDNUM=$(git rev-list --count HEAD)
UNIVERSAL=1 VERSION=$VER BUILD=$BUILDNUM Tools/build_inputmethod.sh
APP=$ROOT/build/InputMethod/MiKey.app

echo "== package"
PKGROOT=$ROOT/build/pkgroot
rm -rf $PKGROOT && mkdir -p "$PKGROOT/Library/Input Methods" $ROOT/build/pkgscripts
cp -R $APP "$PKGROOT/Library/Input Methods/"
cat > $ROOT/build/pkgscripts/postinstall <<'SH'
#!/bin/sh
# the running input method (an older MiKey) is replaced: macOS starts the new one on the next key
pkill -f "Input Methods/MiKey.app/Contents/MacOS/MiKey" 2>/dev/null || true
exit 0
SH
chmod +x $ROOT/build/pkgscripts/postinstall
PKG=$DIST/MiKey-$VER-macOS.pkg
SIGNARGS=()
[ -n "$MIKEY_INSTALLER_ID" ] && SIGNARGS=(--sign "$MIKEY_INSTALLER_ID" --timestamp)
pkgbuild --root $PKGROOT --identifier com.mikey.inputmethod.MiKey.pkg --version $VER \
         --scripts $ROOT/build/pkgscripts --install-location / $SIGNARGS $PKG
if [ -n "$MIKEY_NOTARY_PROFILE" ] && [ -n "$MIKEY_INSTALLER_ID" ]; then
  xcrun notarytool submit $PKG --keychain-profile "$MIKEY_NOTARY_PROFILE" --wait
  xcrun stapler staple $PKG
  NOTARIZED=yes
fi
(cd $ROOT/build/InputMethod && ditto -c -k --keepParent MiKey.app $DIST/MiKey-$VER-macOS.zip)

echo "== update signature + appcast item"
python3 Tools/release/mikey_appcast.py $VER $DIST

echo
echo "Release $VER is ready in $DIST:"
ls -la $DIST | grep -v log
[ -z "$MIKEY_INSTALLER_ID" ] && echo "NOTE: unsigned package (no Developer ID): users open it with right-click > Open, or allow it in Privacy & Security."
[ -z "$NOTARIZED" ] && echo "NOTE: not notarized."

if [ "$PUBLISH" = "--publish" ]; then
  echo "== publish v$VER"
  command -v gh >/dev/null && gh auth status >/dev/null 2>&1 || { echo "gh is not logged in: run 'gh auth login' first"; exit 1; }
  git tag -a "v$VER" -m "MiKey $VER"
  git push origin "v$VER"
  NOTES=$DIST/notes.md
  [ -f $NOTES ] || NOTES=/dev/null
  gh release create "v$VER" $DIST/MiKey-$VER-macOS.pkg $DIST/MiKey-$VER-macOS.zip --title "MiKey $VER" --notes-file $NOTES
  echo "Published. GitHub Actions adds the Windows installers to the release (workflow 'windows')."
else
  echo "Nothing published. Run again with --publish to tag and create the GitHub release."
fi
