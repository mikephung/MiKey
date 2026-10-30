#!/bin/sh
# Removes MiKey from this Mac: every copy of the input method, the installer's staging folder and its receipt.
# Your settings (Vietnamese/English, options) are kept, so a reinstall starts where you left off.
# usage: sh uninstall_mikey.sh        (asks for the administrator password for the copies outside your home folder)
set -e
ID=com.mikey.inputmethod.MiKey
echo "Removing MiKey..."
# the running input method
pkill -f "Input Methods/MiKey.app/Contents/MacOS/MiKey" 2>/dev/null || true
# the copy in your home folder (1.0.0, 1.0.3 and later)
if [ -d "$HOME/Library/Input Methods/MiKey.app" ]; then
  rm -rf "$HOME/Library/Input Methods/MiKey.app" && echo "  removed ~/Library/Input Methods/MiKey.app"
fi
# the shared copy (1.0.1, 1.0.2), the installer's staging folder and receipt: need the administrator password
NEED=""
[ -d "/Library/Input Methods/MiKey.app" ] && NEED=1
[ -d "/Library/Application Support/MiKey" ] && NEED=1
pkgutil --pkgs 2>/dev/null | grep -q "^$ID.pkg$" && NEED=1
if [ -n "$NEED" ]; then
  sudo sh -c "rm -rf '/Library/Input Methods/MiKey.app' '/Library/Application Support/MiKey'; pkgutil --forget $ID.pkg >/dev/null 2>&1 || true"
  echo "  removed /Library/Input Methods/MiKey.app, /Library/Application Support/MiKey and the installer receipt"
fi
echo "Done. Log out and back in so macOS takes MiKey out of the input menu."
