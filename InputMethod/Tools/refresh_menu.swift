// Tells every process that keeps the list of input sources that it changed, so the input menu in the menu bar
// shows a just-installed MiKey without logging out.
// usage: swift refresh_menu.swift
import Foundation

let center = DistributedNotificationCenter.default()
for name in ["com.apple.Carbon.TISNotifyEnabledKeyboardInputSourcesChanged",
             "com.apple.Carbon.TISNotifyEnabledNonKeyboardInputSourcesChanged",
             "com.apple.Carbon.TISNotifySelectedKeyboardInputSourceChanged",
             "AppleEnabledInputSourcesChangedNotification",
             "com.apple.HIToolbox.enabledInputSourcesChanged"] {
    center.postNotificationName(NSNotification.Name(name), object: nil, userInfo: nil, deliverImmediately: true)
}
RunLoop.current.run(until: Date().addingTimeInterval(0.5))
print("notifications posted")
