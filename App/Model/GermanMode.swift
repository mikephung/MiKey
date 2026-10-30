//
//  GermanMode.swift
//  MiKey
//
//  German umlaut input mode - converts ae/oe/ue to ä/ö/ü
//  This runs at Swift layer, separate from the Vietnamese C++ engine.
//

import Foundation

/// German typing mode: converts doubled vowels to umlauts.
/// Unlike Vietnamese Telex, German is simple enough to handle in Swift.
enum GermanMode {
    
    /// Converts German-style digraphs to umlauts.
    /// - ae → ä, Ae → Ä, AE → Ä
    /// - oe → ö, Oe → Ö, OE → Ö
    /// - ue → ü, Ue → Ü, UE → Ü
    /// - ss → ß (optional, controlled by setting)
    static func convert(_ text: String, convertSS: Bool = false) -> String {
        var result = text
        
        // Umlauts
        result = result.replacingOccurrences(of: "ae", with: "ä")
        result = result.replacingOccurrences(of: "Ae", with: "Ä")
        result = result.replacingOccurrences(of: "AE", with: "Ä")
        
        result = result.replacingOccurrences(of: "oe", with: "ö")
        result = result.replacingOccurrences(of: "Oe", with: "Ö")
        result = result.replacingOccurrences(of: "OE", with: "Ö")
        
        result = result.replacingOccurrences(of: "ue", with: "ü")
        result = result.replacingOccurrences(of: "Ue", with: "Ü")
        result = result.replacingOccurrences(of: "UE", with: "Ü")
        
        // Eszett (optional)
        if convertSS {
            result = result.replacingOccurrences(of: "ss", with: "ß")
            result = result.replacingOccurrences(of: "SS", with: "ẞ") // capital eszett
        }
        
        return result
    }
    
    /// Real-time conversion for a single character input.
    /// Returns the replacement if the last two chars form a convertible pair.
    /// - Parameters:
    ///   - buffer: Current word buffer (lowercase keys)
    ///   - newChar: The character just typed
    ///   - convertSS: Whether to convert ss to ß
    /// - Returns: (shouldReplace, replacement) - if shouldReplace is true, delete 1 char and insert replacement
    static func processKey(buffer: String, newChar: Character, convertSS: Bool = false) -> (shouldReplace: Bool, replacement: Character?) {
        guard buffer.count >= 1 else { return (false, nil) }
        
        let lastChar = buffer.last!.lowercased().first!
        let newLower = newChar.lowercased().first!
        let isUpperNew = newChar.isUppercase
        let isUpperLast = buffer.last!.isUppercase
        
        // Check for umlaut pairs
        switch (lastChar, newLower) {
        case ("a", "e"):
            return (true, isUpperLast ? "Ä" : "ä")
        case ("o", "e"):
            return (true, isUpperLast ? "Ö" : "ö")
        case ("u", "e"):
            return (true, isUpperLast ? "Ü" : "ü")
        case ("s", "s") where convertSS:
            return (true, isUpperLast ? "ẞ" : "ß")
        default:
            return (false, nil)
        }
    }
}

// MARK: - Language Enum

/// Language modes supported by MiKey
enum MiKeyLanguage: Int, CaseIterable {
    case english = 0
    case vietnamese = 1
    case german = 2
    
    var displayName: String {
        switch self {
        case .english: return "English"
        case .vietnamese: return "Tiếng Việt"
        case .german: return "Deutsch"
        }
    }
    
    var shortName: String {
        switch self {
        case .english: return "EN"
        case .vietnamese: return "VI"
        case .german: return "DE"
        }
    }
    
    var flag: String {
        switch self {
        case .english: return "🇬🇧"
        case .vietnamese: return "🇻🇳"
        case .german: return "🇩🇪"
        }
    }
}
