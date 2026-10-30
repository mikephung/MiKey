#!/bin/zsh
# Builds the MiKey input method (a real macOS input source) with the Command Line Tools only.
# usage: Tools/build_inputmethod.sh            -> build/InputMethod/MiKey.app
#        Tools/build_inputmethod.sh install    -> also installs to ~/Library/Input Methods and turns it on
set -e
cd "$(dirname "$0")/.."
ROOT=$PWD
B=$ROOT/build/InputMethod/obj
APP=$ROOT/build/InputMethod/MiKey.app
SDK=$(xcrun --sdk macosx --show-sdk-path)
ARCH=$(uname -m)
FLAGS=(-arch $ARCH -isysroot $SDK -mmacosx-version-min=13.0 -O2 -w -I$ROOT/Engine -I$ROOT/Engine/platforms)
rm -rf $APP
mkdir -p $B $APP/Contents/MacOS $APP/Contents/Resources

for f in Engine/Engine.cpp Engine/Vietnamese.cpp Engine/SmartSwitchKey.cpp Engine/Driver.cpp; do
  clang++ -std=c++17 $FLAGS -c $f -o $B/$(basename $f .cpp).o
done
for f in InputMethod/main.mm InputMethod/MiKeyInputController.mm; do
  clang++ -std=c++17 -fobjc-arc $FLAGS -c $f -o $B/$(basename $f .mm).o
done
clang++ $FLAGS $B/*.o -framework Cocoa -framework InputMethodKit -framework Carbon -o $APP/Contents/MacOS/MiKey

cp InputMethod/Info.plist $APP/Contents/Info.plist
swift InputMethod/Tools/make_icon.swift $APP/Contents/Resources/MiKeyMenu.tiff
# the name in the input menu, in every language macOS may be set to
for l in en de vi fr it; do
  mkdir -p $APP/Contents/Resources/$l.lproj
  printf '"CFBundleName" = "MiKey";\n"CFBundleDisplayName" = "MiKey";\n"com.mikey.inputmethod.MiKey" = "MiKey";\n' > $APP/Contents/Resources/$l.lproj/InfoPlist.strings
done
codesign --force --sign - $APP
echo "Built $APP"

if [ "$1" = install ]; then
  DEST=~/Library/Input\ Methods
  mkdir -p "$DEST"
  pkill -f "Input Methods/MiKey.app/Contents/MacOS/MiKey" 2>/dev/null || true   # only the input method, not the menu bar app; macOS restarts it on the next key
  rm -rf "$DEST/MiKey.app"
  cp -R $APP "$DEST/"
  swift InputMethod/Tools/register.swift "$DEST/MiKey.app" || true
  echo "Installed $DEST/MiKey.app"
fi
