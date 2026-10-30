import SwiftUI

struct MenuBarContent: View {
    @EnvironmentObject var state: AppState
    @AppStorage(PrefKey.autoSwitch) private var autoSwitch = 1
    @AppStorage(PrefKey.hotkey) private var hotkeyRaw = Hotkey.defaultValue

    var body: some View {
        if state.needsOnboarding {
            Button("Cấp quyền cho MiKey…") { OnboardingWindow.show() }
            Divider()
        }
        Toggle(isOn: Binding(get: { state.language == 1 }, set: { state.setLanguage($0 ? 1 : 0) })) {
            Text("Tiếng Việt   \(Hotkey(raw: hotkeyRaw).display)")
        }
        Toggle("Tự chuyển Anh/Việt", isOn: Binding(get: { autoSwitch == 1 }, set: { autoSwitch = $0 ? 1 : 0; Preferences.apply() }))
        Divider()
        Button("Mở MiKey…") { Windows.main.show() }
            .keyboardShortcut(",")
        Divider()
        Button("Hướng dẫn…") { OnboardingWindow.show() }
        Button("Gửi góp ý…") { Feedback.open() }
        Button("Kiểm tra cập nhật…") { Updater.shared.checkForUpdates() }
        Button("Giới thiệu MiKey") { AboutPanel.show() }
        Button("Thoát MiKey") { NSApp.terminate(nil) }
            .keyboardShortcut("q")
    }
}

/// Debug items, in the MiKey app menu only (not the menu bar icon).
struct DebugMenu: View {
    @AppStorage(PrefKey.typingLogEnabled) private var logEnabled = 0

    var body: some View {
        Menu("Gỡ lỗi") {
            Toggle("Ghi nhật ký gõ", isOn: Binding(get: { logEnabled == 1 }, set: { logEnabled = $0 ? 1 : 0; Preferences.apply() }))
            Button("Xem nhật ký gõ…") { Windows.history.show() }
                .disabled(logEnabled == 0)
        }
    }
}

/// Feedback URL
enum Feedback {
    static var url: URL {
        let v = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? ""
        return URL(string: "https://github.com/taaphmi3/MiKey/issues/new?title=Feedback&body=Version:\(v)")!
    }
    static func open() { NSWorkspace.shared.open(url) }
}
