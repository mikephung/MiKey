// Registers an installed MiKey input method with macOS and turns it on (adds it to the input menu).
// Built into MiKey.app as Contents/MacOS/mikey-register; the .pkg postinstall runs it as the logged-in user,
// so MiKey shows up right away without logging out.
//
// usage: mikey-register [path to MiKey.app] [select] [--wait]
//   select  also make MiKey the active input source
//   --wait  keep checking for ~25 s and register again if macOS drops MiKey. Needed after an upgrade: macOS
//           handles the removal of the old copy (same bundle id) a few seconds late and then takes the input
//           source out of the list, undoing a registration made right before.
import Carbon
import Foundation

let args = CommandLine.arguments
let positional = args.dropFirst().filter { !$0.hasPrefix("-") && $0 != "select" }
let path = positional.first ?? NSHomeDirectory() + "/Library/Input Methods/MiKey.app"
let wait = args.contains("--wait")
let select = args.contains("select")
let bundleID = "com.mikey.inputmethod.MiKey"

func listed() -> [TISInputSource] {
    let filter = [kTISPropertyBundleID as String: bundleID] as CFDictionary
    return TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource] ?? []
}
func isEnabled(_ s: TISInputSource) -> Bool {
    guard let p = TISGetInputSourceProperty(s, kTISPropertyInputSourceIsEnabled) else { return false }
    return CFBooleanGetValue(Unmanaged<CFBoolean>.fromOpaque(p).takeUnretainedValue())
}
/// Registers the bundle and enables every input source it provides. Returns true when MiKey is listed and enabled.
func registerAndEnable() -> Bool {
    let st = TISRegisterInputSource(URL(fileURLWithPath: path) as CFURL)
    print("register \(path): \(st == noErr ? "ok" : "status \(st)")")
    var found: [TISInputSource] = []
    for _ in 0..<20 {   // the system can take a moment to list a just-registered input method
        found = listed()
        if !found.isEmpty { break }
        usleep(250_000)
    }
    for s in found where !isEnabled(s) { print("enable: \(TISEnableInputSource(s) == noErr ? "ok" : "failed")") }
    return !listed().isEmpty && listed().allSatisfy(isEnabled)
}

/// A process keeps the input source list it read first, so a check in this process can be out of date. Ask a fresh
/// copy of this program (--check): exit status 0 = MiKey is listed and enabled.
func freshCheck() -> Bool {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: args[0])
    p.arguments = ["--check"]
    p.standardOutput = FileHandle.nullDevice
    do { try p.run() } catch { return false }
    p.waitUntilExit()
    return p.terminationStatus == 0
}

if args.contains("--check") { exit(!listed().isEmpty && listed().allSatisfy(isEnabled) ? 0 : 1) }

var ok = registerAndEnable()
if wait {
    // done when MiKey stays listed and enabled for 5 checks in a row, 3 s apart; at most 14 rounds (~40 s)
    var stable = 0
    for round in 1...14 {
        sleep(3)
        if freshCheck() { stable += 1; if stable >= 5 { break } }
        else { stable = 0; print("round \(round): macOS dropped MiKey, registering again"); _ = registerAndEnable() }
    }
    ok = freshCheck()
}
if !ok {
    print("MiKey is not listed: log out and back in, then add it in System Settings > Keyboard > Input Sources")
    exit(1)
}
if select, let s = listed().first { print("select: \(TISSelectInputSource(s) == noErr ? "ok" : "failed")") }
print("MiKey is enabled")
