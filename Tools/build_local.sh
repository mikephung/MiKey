#!/bin/zsh
# Builds MiKey.app with the Command Line Tools only (no Xcode, no Sparkle).
# usage: Tools/build_local.sh [install]    -> build/MiKey.app (install: also copies it to ~/Applications)
set -e
cd "$(dirname "$0")/.."
ROOT=$PWD
B=$ROOT/build/obj
APP=$ROOT/build/MiKey.app
SDK=$(xcrun --sdk macosx --show-sdk-path)
ARCH=$(uname -m)
mkdir -p $B $APP/Contents/MacOS $APP/Contents/Resources
INC=(-I$ROOT/Engine -I$ROOT/Engine/platforms -I$ROOT/App/Core)

# C++ engine + Objective-C++ core
for f in Engine/Engine.cpp Engine/Vietnamese.cpp Engine/SmartSwitchKey.cpp Engine/Driver.cpp Engine/TouchModel.cpp; do
  o=$B/$(basename $f .cpp).o
  if [ ! -f $o ] || [ $f -nt $o ] || [ Engine/AutoSwitchData.h -nt $o ]; then
    clang++ -std=c++17 -O2 -w -arch $ARCH -isysroot $SDK -mmacosx-version-min=13.0 $INC -c $f -o $o
  fi
done
clang++ -std=c++17 -O2 -w -fobjc-arc -arch $ARCH -isysroot $SDK -mmacosx-version-min=13.0 $INC -c App/Core/VikeyCore.mm -o $B/VikeyCore.o

# Swift UI
swiftc -O -swift-version 5 -target $ARCH-apple-macos13.0 -sdk $SDK \
  -import-objc-header App/Core/MiKey-Bridging-Header.h -I App/Core \
  -parse-as-library -module-name MiKey \
  $(find App -name '*.swift') $B/*.o \
  -Xlinker -lc++ -framework Carbon -framework ApplicationServices -framework Cocoa -framework SwiftUI \
  -o $APP/Contents/MacOS/MiKey

# Bundle
sed -e 's/$(EXECUTABLE_NAME)/MiKey/' -e 's/$(PRODUCT_BUNDLE_IDENTIFIER)/com.mikey.app/' -e 's/$(PRODUCT_NAME)/MiKey/' \
    -e 's/$(MARKETING_VERSION)/1.0.0/' -e 's/$(CURRENT_PROJECT_VERSION)/1/' -e 's/$(MACOSX_DEPLOYMENT_TARGET)/13.0/' \
    App/Info.plist > $APP/Contents/Info.plist
cp App/Resources/Emoji.json App/Resources/Sounds/*.caf $APP/Contents/Resources/
if [ -f App/Resources/Assets.xcassets/AppIcon.appiconset/icon_1024.png ]; then
  I=$ROOT/build/AppIcon.iconset; rm -rf $I; mkdir -p $I
  S=App/Resources/Assets.xcassets/AppIcon.appiconset/icon_1024.png
  for s in 16 32 128 256 512; do
    sips -z $s $s $S --out $I/icon_${s}x${s}.png >/dev/null
    sips -z $((s*2)) $((s*2)) $S --out $I/icon_${s}x${s}@2x.png >/dev/null
  done
  iconutil -c icns $I -o $APP/Contents/Resources/AppIcon.icns && /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" $APP/Contents/Info.plist || true
fi
# A stable ad-hoc signature with the entitlements, so the Accessibility permission survives rebuilds as well as it can
codesign --force --deep --sign - --entitlements App/MiKey.entitlements $APP
echo "Built $APP"
if [ "$1" = install ]; then
  mkdir -p ~/Applications && rm -rf ~/Applications/MiKey.app && cp -R $APP ~/Applications/ && echo "Installed ~/Applications/MiKey.app"
fi
