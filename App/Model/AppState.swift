import AppKit
import Combine
import SwiftUI

/// App-wide state the menu bar and windows observe.
@MainActor
final class AppState: ObservableObject {
    static let shared = AppState()

    @Published private(set) var language: Int = Int(MiKeyCore.language())
    @Published private(set) var isRunning = false
    @Published var needsOnboarding = false

    private var permissionTimer: Timer?

    private init() {
        NotificationCenter.default.addObserver(forName: .MiKeyLanguageDidChange, object: nil, queue: .main) { [weak self] _ in
            Task { @MainActor in self?.language = Int(MiKeyCore.language()) }
        }
    }

    /// Starts the keyboard core when Accessibility is granted; otherwise shows onboarding and waits.
    func startIfPossible() {
        if MiKeyCore.isAccessibilityTrusted(), MiKeyCore.start() {
            isRunning = true
            needsOnboarding = false
            language = Int(MiKeyCore.language())
            permissionTimer?.invalidate()
            permissionTimer = nil
            return
        }
        isRunning = false
        needsOnboarding = true
        OnboardingWindow.show()
        if permissionTimer == nil {
            permissionTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
                Task { @MainActor in
                    if MiKeyCore.isAccessibilityTrusted() { AppState.shared.startIfPossible() }
                }
            }
        }
    }

    func setLanguage(_ value: Int) {
        MiKeyCore.setLanguageByUser(Int32(value))
        language = Int(MiKeyCore.language())
    }

    func toggleLanguage() { setLanguage(language == 1 ? 0 : 1) }
}

extension Notification.Name {
    static let MiKeyLanguageDidChange = Notification.Name(rawValue: "MiKeyLanguageDidChange")
}
