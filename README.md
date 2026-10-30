# MiKey

Vietnamese and German typing for macOS, Windows, and Linux. Forked from [Vikey](https://github.com/trungdq88/Vikey) by Tony Dinh.

## Features

### Vietnamese Mode (Telex)
- **Telex** with modern or classic tone placement (hoà / hòa), spell checking
- **Auto switch:** Automatically detects and switches between Vietnamese and English
- **Programming-aware:** `var`, `const`, `git push`, `obj.dir` stay unchanged
- **Undo:** Press Delete right after an automatic fix to undo it

### German Mode (coming soon)
- Type umlauts easily: `ae` → `ä`, `oe` → `ö`, `ue` → `ü`
- Eszett support: `ss` → `ß` (optional)

## Telex Guide

| Keys | Result |
|------|--------|
| aa | â |
| aw | ă |
| ee | ê |
| oo | ô |
| ow | ơ |
| uw | ư |
| dd | đ |
| s | sắc (´) |
| f | huyền (`) |
| r | hỏi (?) |
| x | ngã (~) |
| j | nặng (.) |
| z | remove tone |

## Build

### macOS
Requires Xcode and [XcodeGen](https://github.com/yonaskolb/XcodeGen).

```sh
xcodegen generate
xcodebuild -project MiKey.xcodeproj -scheme MiKey -configuration Release build
```

### Windows
Requires Visual Studio with C++ support.

```sh
cd Windows
cmake -B build
cmake --build build --config Release
```

### Linux
Requires IBus development libraries.

```sh
cd Linux
cmake -B build
cmake --build build
sudo cmake --install build
```

## Credits

MiKey is based on [Vikey](https://github.com/trungdq88/Vikey) by [Tony Dinh](https://tonydinh.com), which is based on [OpenKey](https://github.com/tuyenvm/OpenKey) by Tuyen Mai.

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).
