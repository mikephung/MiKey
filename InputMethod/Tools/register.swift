// Registers the installed MiKey input method with macOS and turns it on (adds it to the input menu).
// usage: swift register.swift ~/Library/Input\ Methods/MiKey.app [select]
import Carbon
import Foundation

let path = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : NSHomeDirectory() + "/Library/Input Methods/MiKey.app"
let url = URL(fileURLWithPath: path) as CFURL
let st = TISRegisterInputSource(url)
print("register: \(st == noErr ? "ok" : "status \(st)")")

let filter = [kTISPropertyBundleID as String: "com.mikey.inputmethod.MiKey"] as CFDictionary
guard let list = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource], !list.isEmpty else {
    print("MiKey not found among input sources yet: log out and back in, then add it in System Settings > Keyboard > Input Sources")
    exit(1)
}
for src in list {
    let e = TISEnableInputSource(src)
    print("enable: \(e == noErr ? "ok" : "status \(e)")")
    if CommandLine.arguments.contains("select") {
        let s = TISSelectInputSource(src)
        print("select: \(s == noErr ? "ok" : "status \(s)")")
    }
}
