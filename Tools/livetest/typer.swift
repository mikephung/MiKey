// Live typing for the MiKey input method: selects an input source and types text as real key presses,
// using the key codes of the keyboard layout in use (QWERTZ, Swiss German...), so ä ö ü come from their own keys.
// usage: typer select <bundle id>          select an input source
//        typer type "<text>"               type it ('|' = Return, '<' = Backspace, '{optz}' = ⌥Z)
//        typer current                     print the selected input source and the layout under it
// The process that runs it needs the Accessibility permission (System Settings > Privacy & Security).
import Carbon
import Foundation

func prop<T>(_ src: TISInputSource, _ key: CFString) -> T? {
    guard let p = TISGetInputSourceProperty(src, key) else { return nil }
    return Unmanaged<AnyObject>.fromOpaque(p).takeUnretainedValue() as? T
}

func select(_ bundle: String) -> Bool {
    let filter = [kTISPropertyBundleID as String: bundle] as CFDictionary
    guard let list = TISCreateInputSourceList(filter, false)?.takeRetainedValue() as? [TISInputSource], let s = list.first else { return false }
    return TISSelectInputSource(s) == noErr
}

/// character -> (key code, shift, option) for the current keyboard layout
func keyMap() -> [Character: (CGKeyCode, Bool, Bool)] {
    var map: [Character: (CGKeyCode, Bool, Bool)] = [:]
    guard let src = TISCopyCurrentKeyboardLayoutInputSource()?.takeRetainedValue(),
          let data: CFData = prop(src, kTISPropertyUnicodeKeyLayoutData) else { return map }
    let layout = unsafeBitCast(CFDataGetBytePtr(data), to: UnsafePointer<UCKeyboardLayout>.self)
    for (shift, option) in [(false, false), (true, false), (false, true), (true, true)] {
        let mods: UInt32 = ((shift ? UInt32(shiftKey) : 0) | (option ? UInt32(optionKey) : 0)) >> 8
        for code in 0..<128 {
            var dead: UInt32 = 0
            var chars = [UniChar](repeating: 0, count: 4)
            var n = 0
            UCKeyTranslate(layout, UInt16(code), UInt16(kUCKeyActionDown), mods, UInt32(LMGetKbdType()),
                           OptionBits(kUCKeyTranslateNoDeadKeysBit), &dead, 4, &n, &chars)
            guard n == 1, let ch = String(utf16CodeUnits: chars, count: n).first else { continue }
            if map[ch] == nil { map[ch] = (CGKeyCode(code), shift, option) }
        }
    }
    return map
}

let source = CGEventSource(stateID: .hidSystemState)
func press(_ code: CGKeyCode, shift: Bool = false, option: Bool = false) {
    var flags: CGEventFlags = []
    if shift { flags.insert(.maskShift) }
    if option { flags.insert(.maskAlternate) }
    for down in [true, false] {
        let e = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: down)!
        e.flags = flags
        e.post(tap: .cghidEventTap)
        usleep(12_000)
    }
    usleep(25_000)
}

func pressCmd(_ code: CGKeyCode) {
    for down in [true, false] {
        let e = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: down)!
        e.flags = .maskCommand
        e.post(tap: .cghidEventTap)
        usleep(12_000)
    }
    usleep(60_000)
}

let args = CommandLine.arguments
guard args.count >= 2 else { print("usage: typer select <id> | type <text> | current"); exit(2) }
switch args[1] {
case "select":
    exit(select(args[2]) ? 0 : 1)
case "current":
    let s = TISCopyCurrentKeyboardInputSource().takeRetainedValue()
    let l = TISCopyCurrentKeyboardLayoutInputSource().takeRetainedValue()
    print((prop(s, kTISPropertyInputSourceID) as String?) ?? "?", "/", (prop(l, kTISPropertyInputSourceID) as String?) ?? "?")
case "type":
    if !AXIsProcessTrusted() { fputs("typer: this process needs the Accessibility permission\n", stderr); exit(3) }
    let map = keyMap()
    var text = Substring(args[2])
    while let ch = text.first {
        if text.hasPrefix("{optz}") { let z = map["z"]!; press(z.0, option: true); text = text.dropFirst(6); continue }
        // ⌘A / ⌘C / ⌘V for clearing and reading any text field
        if text.hasPrefix("{cmd") && text.count >= 6 {
            let k = text[text.index(text.startIndex, offsetBy: 4)]
            if let code = map[k]?.0 { pressCmd(code) }
            text = text.dropFirst(6); continue
        }
        if text.hasPrefix("{del}") { press(51); text = text.dropFirst(5); continue }
        text = text.dropFirst()
        switch ch {
        case "|": press(36)
        case "<": press(51)
        default:
            guard let k = map[ch] else { fputs("typer: no key for \(ch)\n", stderr); exit(4) }
            press(k.0, shift: k.1, option: k.2)
        }
    }
default:
    exit(2)
}
