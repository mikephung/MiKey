// Draws the input menu icon: "Mi" in a rounded box, as a template image (macOS tints it for light/dark).
// usage: swift make_icon.swift out.tiff
import AppKit

func render(_ px: CGFloat) -> NSBitmapImageRep {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(px), pixelsHigh: Int(px), bitsPerSample: 8,
                               samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                               bytesPerRow: 0, bitsPerPixel: 0)!
    rep.size = NSSize(width: 16, height: 16)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    let box = NSRect(x: 0.5, y: 1.5, width: 15, height: 13)
    NSColor.black.setFill()
    NSBezierPath(roundedRect: box, xRadius: 3, yRadius: 3).fill()
    // the letters are cut out of the box
    NSGraphicsContext.current?.compositingOperation = .destinationOut
    let font = NSFont.systemFont(ofSize: 10, weight: .bold)
    let s = NSAttributedString(string: "Mi", attributes: [.font: font, .foregroundColor: NSColor.black])
    let sz = s.size()
    s.draw(at: NSPoint(x: box.midX - sz.width / 2, y: box.midY - sz.height / 2 + 0.5))
    NSGraphicsContext.restoreGraphicsState()
    return rep
}

let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "MiKeyMenu.tiff"
let image = NSImage(size: NSSize(width: 16, height: 16))
image.addRepresentation(render(16))
image.addRepresentation(render(32))
image.isTemplate = true
try! image.tiffRepresentation!.write(to: URL(fileURLWithPath: out))
print("wrote \(out)")
