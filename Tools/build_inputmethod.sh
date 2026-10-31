#!/bin/zsh
# Builds the MiKey input method (a real macOS input source) with the Command Line Tools only.
# usage: Tools/build_inputmethod.sh            -> build/InputMethod/MiKey.app (this Mac's architecture)
#        Tools/build_inputmethod.sh install    -> also installs to ~/Library/Input Methods and turns it on
#        UNIVERSAL=1 Tools/build_inputmethod.sh -> arm64 + x86_64 (for a release)
#        VERSION=1.0.1 BUILD=2 ...             -> version in Info.plist (default: InputMethod/Info.plist as is)
set -e
cd "$(dirname "$0")/.."
ROOT=$PWD
APP=$ROOT/build/InputMethod/MiKey.app
SDK=$(xcrun --sdk macosx --show-sdk-path)
if [ -n "$UNIVERSAL" ]; then ARCHS=(arm64 x86_64); else ARCHS=($(uname -m)); fi
rm -rf $APP
mkdir -p $APP/Contents/MacOS $APP/Contents/Resources

BINS=()
for ARCH in $ARCHS; do
  B=$ROOT/build/InputMethod/obj-$ARCH
  mkdir -p $B
  FLAGS=(-arch $ARCH -isysroot $SDK -mmacosx-version-min=13.0 -O2 -w -I$ROOT/Engine -I$ROOT/Engine/platforms)
  for f in Engine/Engine.cpp Engine/Vietnamese.cpp Engine/SmartSwitchKey.cpp Engine/Driver.cpp; do
    clang++ -std=c++17 $FLAGS -c $f -o $B/$(basename $f .cpp).o
  done
  for f in InputMethod/main.mm InputMethod/MiKeyInputController.mm; do
    clang++ -std=c++17 -fobjc-arc $FLAGS -c $f -o $B/$(basename $f .mm).o
  done
  clang++ $FLAGS $B/*.o -framework Cocoa -framework InputMethodKit -framework Carbon -o $B/MiKey
  BINS+=($B/MiKey)
done
lipo -create $BINS -output $APP/Contents/MacOS/MiKey
# the helper the .pkg runs after installing: registers MiKey and turns it on for the logged-in user
REGS=()
for ARCH in $ARCHS; do
  swiftc -O -target $ARCH-apple-macos13.0 -sdk $SDK InputMethod/Tools/register.swift -o $ROOT/build/InputMethod/obj-$ARCH/mikey-register
  REGS+=($ROOT/build/InputMethod/obj-$ARCH/mikey-register)
done
lipo -create $REGS -output $APP/Contents/MacOS/mikey-register

cp InputMethod/Info.plist $APP/Contents/Info.plist
if [ -n "$VERSION" ]; then
  /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" $APP/Contents/Info.plist
  /usr/libexec/PlistBuddy -c "Set :CFBundleVersion ${BUILD:-1}" $APP/Contents/Info.plist
fi
swift InputMethod/Tools/make_icon.swift $APP/Contents/Resources/MiKeyMenu.tiff
# the name in the input menu, in every language macOS may be set to
for l in en de vi fr it; do
  mkdir -p $APP/Contents/Resources/$l.lproj
  printf '"CFBundleName" = "MiKey";\n"CFBundleDisplayName" = "MiKey";\n"com.mikey.inputmethod.MiKey" = "MiKey";\n' > $APP/Contents/Resources/$l.lproj/InfoPlist.strings
done
cp LICENSE $APP/Contents/Resources/LICENSE.txt
# Developer ID when MIKEY_SIGN_ID is set (release), ad hoc otherwise
if [ -n "$MIKEY_SIGN_ID" ]; then
  codesign --force --options runtime --timestamp --sign "$MIKEY_SIGN_ID" $APP/Contents/MacOS/mikey-register
  codesign --force --options runtime --timestamp --sign "$MIKEY_SIGN_ID" $APP
else
  codesign --force --sign - $APP/Contents/MacOS/mikey-register   # nested code is signed first
  codesign --force --sign - $APP
fi
codesign --verify --deep --strict $APP
echo "Built $APP ($(lipo -archs $APP/Contents/MacOS/MiKey))"

if [ "$1" = install ]; then
  DEST=~/Library/Input\ Methods
  mkdir -p "$DEST"
  pkill -f "Input Methods/MiKey.app/Contents/MacOS/MiKey" 2>/dev/null || true   # only the input method, not the menu bar app; macOS restarts it on the next key
  rm -rf "$DEST/MiKey.app"
  cp -R $APP "$DEST/"
  "$DEST/MiKey.app/Contents/MacOS/mikey-register" "$DEST/MiKey.app" || true
  echo "Installed $DEST/MiKey.app"
fi
