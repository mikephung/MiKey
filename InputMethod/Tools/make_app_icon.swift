// Draws the MiKey app icon: "Mi" in white on the indigo rounded square (design/BRAND.md accent #4F46E5).
// usage: swift make_app_icon.swift out.png [size]
import AppKit

let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "MiKey-1024.png"
let px = CommandLine.arguments.count > 2 ? Int(CommandLine.arguments[2])! : 1024
let s = CGFloat(px)
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: px, pixelsHigh: px, bitsPerSample: 8, samplesPerPixel: 4,
                           hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
// macOS icon grid: the shape is 824/1024 of the canvas, corner radius ~185/1024
let inset = s * 100 / 1024
let box = NSRect(x: inset, y: inset, width: s - 2 * inset, height: s - 2 * inset)
let path = NSBezierPath(roundedRect: box, xRadius: s * 185 / 1024, yRadius: s * 185 / 1024)
NSGraphicsContext.current?.saveGraphicsState()
let shadow = NSShadow()
shadow.shadowColor = NSColor.black.withAlphaComponent(0.25)
shadow.shadowBlurRadius = s * 12 / 1024
shadow.shadowOffset = NSSize(width: 0, height: -s * 6 / 1024)
shadow.set()
NSColor(red: 0.31, green: 0.27, blue: 0.90, alpha: 1).setFill()
path.fill()
NSGraphicsContext.current?.restoreGraphicsState()
let gradient = NSGradient(starting: NSColor(red: 0.33, green: 0.31, blue: 0.85, alpha: 1),
                          ending: NSColor(red: 0.22, green: 0.26, blue: 0.73, alpha: 1))!
gradient.draw(in: path, angle: -90)
let font = NSFont.systemFont(ofSize: s * 0.40, weight: .semibold)
let text = NSAttributedString(string: "Mi", attributes: [.font: font, .foregroundColor: NSColor.white, .kern: -s * 0.005])
let size = text.size()
text.draw(at: NSPoint(x: box.midX - size.width / 2, y: box.midY - size.height / 2 - s * 0.01))
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
print("wrote \(out)")
