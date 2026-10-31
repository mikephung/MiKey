// Draws the 1200×630 share image (Open Graph / X card): icon, name, pitch and the before/after examples.
// usage: swift site-mikey/tools/make_og.swift site-mikey/assets/og.png site-mikey/assets/icon-512.png
import AppKit

let out = CommandLine.arguments[1], iconPath = CommandLine.arguments[2]
let W = 1200, H = 630
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: W, pixelsHigh: H, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                           isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor.white.setFill(); NSRect(x: 0, y: 0, width: W, height: H).fill()
NSColor(red: 0.96, green: 0.96, blue: 0.98, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 660, y: 70, width: 480, height: 490), xRadius: 28, yRadius: 28).fill()
NSImage(contentsOfFile: iconPath)!.draw(in: NSRect(x: 60, y: 430, width: 130, height: 130))
func text(_ s: String, _ size: CGFloat, _ weight: NSFont.Weight, _ color: NSColor, _ x: CGFloat, _ y: CGFloat, strike: Bool = false) {
    var a: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: size, weight: weight), .foregroundColor: color]
    if strike { a[.strikethroughStyle] = NSUnderlineStyle.thick.rawValue; a[.strikethroughColor] = color }
    NSAttributedString(string: s, attributes: a).draw(at: NSPoint(x: x, y: y))
}
let ink = NSColor(red: 0.08, green: 0.08, blue: 0.17, alpha: 1), ink2 = NSColor(red: 0.29, green: 0.29, blue: 0.41, alpha: 1)
let accent = NSColor(red: 0.31, green: 0.27, blue: 0.90, alpha: 1)
let bad = NSColor(red: 0.71, green: 0.14, blue: 0.09, alpha: 1), good = NSColor(red: 0.03, green: 0.46, blue: 0.28, alpha: 1)
let mark = NSMutableAttributedString(string: "Mi", attributes: [.font: NSFont.systemFont(ofSize: 64, weight: .bold), .foregroundColor: ink])
mark.append(NSAttributedString(string: "Key", attributes: [.font: NSFont.systemFont(ofSize: 64, weight: .bold), .foregroundColor: accent]))
mark.draw(at: NSPoint(x: 215, y: 455))   // one word: the wordmark has no space
text("Gõ tiếng Việt, tiếng Đức, tiếng Anh.", 40, .bold, ink, 60, 330)
text("Không cần đổi bàn phím.", 40, .bold, ink, 60, 278)
text("Telex cho người Việt ở Thụy Sĩ, Đức, Áo", 28, .regular, ink2, 60, 200)
text("macOS · Windows · Miễn phí · Mã nguồn mở", 24, .medium, accent, 60, 120)
text("mikey.mikephung.com", 24, .semibold, ink2, 60, 78)
let rows = [("tẽt", "text"), ("ửi", "wir"), ("ơber", "über"), ("õ", "osx")]
for (i, r) in rows.enumerated() {
    let y = CGFloat(470 - i * 105)
    text(r.0, 48, .semibold, bad, 710, y, strike: true)
    text("→", 40, .regular, ink2, 860, y + 4)
    text(r.1, 48, .bold, good, 930, y)
}
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
print("wrote \(out)")
