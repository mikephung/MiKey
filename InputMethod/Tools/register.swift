// Registers an installed MiKey input method with macOS and turns it on (adds it to the input menu).
// Built into MiKey.app as Contents/MacOS/mikey-register; the .pkg postinstall runs it as the logged-in user,
// so MiKey shows up right away without logging out.
// usage: mikey-register [path to MiKey.app] [select]
import Carbon
import Foundation

let args = CommandLine.arguments
let path = args.count > 1 && !args[1].hasPrefix("-") && args[1] != "select" ? args[1]
         : NSHomeDirectory() + "/Library/Input Methods/MiKey.app"
let st = TISRegisterInputSource(URL(fileURLWithPath: path) as CFURL)
print("register \(path): \(st == noErr ? "ok" : "status \(st)")")

let filter = [kTISPropertyBundleID as String: "com.mikey.inputmethod.MiKey"] as CFDictionary
var list: [TISInputSource] = []
for _ in 0..<20 {   // the system can take a moment to list a just-registered input method
    list = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource] ?? []
    if !list.isEmpty { break }
    usleep(250_000)
}
if list.isEmpty {
    print("MiKey is not listed yet: log out and back in, then add it in System Settings > Keyboard > Input Sources")
    exit(1)
}
for src in list {
    let e = TISEnableInputSource(src)
    print("enable: \(e == noErr ? "ok" : "status \(e)")")
    if args.contains("select") {
        let s = TISSelectInputSource(src)
        print("select: \(s == noErr ? "ok" : "status \(s)")")
    }
}
