#!/bin/zsh
# Builds, Developer ID signs, notarizes and staples a MiKey release for macOS.
#   MIKEY_IDENT="Developer ID Application: Name (TEAMID)" MIKEY_NOTARY_PROFILE=mikey-notary Tools/release/sign_mac.sh
# One-time setup of the notary profile (App Store Connect API key):
#   xcrun notarytool store-credentials mikey-notary --key AuthKey_XXXX.p8 --key-id XXXX --issuer <issuer-uuid>
# Output: dist/MiKey.app (stapled) and dist/MiKey-<version>.dmg (signed, notarized, stapled).
set -e
IDENT=${MIKEY_IDENT:?set MIKEY_IDENT to the Developer ID Application identity (security find-identity -v -p codesigning)}
PROFILE=${MIKEY_NOTARY_PROFILE:-mikey-notary}
cd "$(dirname "$0")/../.."
VER=$(grep 'MARKETING_VERSION' project.yml | grep -o '"[^"]*"' | tr -d '"')
echo "==> MiKey $VER"

echo "==> build (universal)"
xcodegen generate >/dev/null
rm -rf build/dd dist && mkdir -p dist
xcodebuild -project MiKey.xcodeproj -scheme MiKey -configuration Release -derivedDataPath build/dd \
  ARCHS="arm64 x86_64" ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY=- CODE_SIGNING_REQUIRED=NO build | grep -E "error:|BUILD" || true
APP=build/dd/Build/Products/Release/MiKey.app
[ "$(defaults read "$PWD/$APP/Contents/Info.plist" CFBundleShortVersionString)" = "$VER" ] || { echo "built version mismatch"; exit 1; }
lipo -archs "$APP/Contents/MacOS/MiKey"
cp -R "$APP" dist/

echo "==> sign + notarize app"
# Sparkle's helpers first (inside out, no --deep), then the app with its entitlements
SPK=dist/MiKey.app/Contents/Frameworks/Sparkle.framework/Versions/B
for x in $SPK/XPCServices/Installer.xpc $SPK/XPCServices/Downloader.xpc $SPK/Autoupdate $SPK/Updater.app; do
  [ -e "$x" ] && codesign --force --options runtime --timestamp --preserve-metadata=entitlements -s "$IDENT" "$x"
done
codesign --force --options runtime --timestamp -s "$IDENT" dist/MiKey.app/Contents/Frameworks/Sparkle.framework
codesign --force --options runtime --timestamp --entitlements App/MiKey.entitlements -s "$IDENT" dist/MiKey.app
codesign --verify --deep --strict dist/MiKey.app
ditto -c -k --keepParent dist/MiKey.app dist/MiKey.zip
xcrun notarytool submit dist/MiKey.zip --keychain-profile "$PROFILE" --wait | tail -1
xcrun stapler staple dist/MiKey.app | tail -1
rm dist/MiKey.zip

echo "==> DMG"
DMG=dist/MiKey-$VER.dmg
python3 Tools/release/dmg_background.py dist/dmg_bg.png
create-dmg --volname "MiKey" --volicon design/Vikey.icns \
  --background dist/dmg_bg.png --window-pos 200 120 --window-size 660 420 \
  --icon-size 128 --icon "MiKey.app" 170 190 --app-drop-link 490 190 \
  --hide-extension "MiKey.app" --no-internet-enable \
  --codesign "$IDENT" "$DMG" dist/MiKey.app >/dev/null || true
[ -f "$DMG" ] || { echo "dmg not created"; exit 1; }
xcrun notarytool submit "$DMG" --keychain-profile "$PROFILE" --wait | tail -1
xcrun stapler staple "$DMG" | tail -1

echo "==> verify"
spctl -a -vv -t exec dist/MiKey.app 2>&1 | tail -2
spctl -a -vv -t open --context context:primary-signature "$DMG" 2>&1 | tail -2
shasum -a 256 "$DMG"
echo "==> done: $DMG"
