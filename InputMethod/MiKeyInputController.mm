//
//  MiKeyInputController.mm
//  MiKey input method (InputMethodKit).
//
//  The word being typed is kept as marked text and committed at the end of the word (space, punctuation,
//  Return, a click). The engine (Engine/Driver.cpp, the same one the iOS keyboard runs) decides every edit,
//  including putting English and German words back as typed. Keys are read as the characters the active
//  keyboard layout gives (QWERTZ, Swiss German...), so Telex always sees the letter printed on the key.
//  Letters Telex doesn't know (ä ö ü ß é à è ç) end Telex for the rest of that word: "über", "Café", "Grüße".
//
#import <Cocoa/Cocoa.h>
#import <InputMethodKit/InputMethodKit.h>
#include "Driver.h"
#include "Vietnamese.h"

// Engine settings (Engine.h). vGermanAware lives in Engine.cpp.
int vLanguage = 1, vSwitchKeyStatus = 0, vCheckSpelling = 1, vUseModernOrthography = 1, vRestoreIfWrongSpelling = 1,
    vFixRecommendBrowser = 0, vUseSmartSwitchKey = 0, vOtherLanguage = 0, vAutoSwitchByTyping = 1;

static NSString* const kLanguage = @"Language";            // 1 = Vietnamese, 0 = English/German
static NSString* const kAutoSwitch = @"AutoSwitchByTyping";
static NSString* const kGerman = @"GermanAware";
static NSString* const kModern = @"ModernOrthography";

enum { TagVietnamese = 1, TagEnglish, TagAutoSwitch, TagGerman, TagModern, TagAbout };

static VikeyDriver* gDriver = nullptr;
static vKeyHookState* gHook = nullptr;     // the engine's output for the last call
static NSMutableString* gComposing = nil;   // marked text: the word being typed, not yet in the document
static bool gForeign = false;               // inside a word with ä ö ü ß é...: Telex is off until the word ends
static NSPanel* gHud = nil;

static NSUserDefaults* Defaults() { return [NSUserDefaults standardUserDefaults]; }
static int DefaultInt(NSString* key, int fallback) { id v = [Defaults() objectForKey:key]; return v ? [v intValue] : fallback; }

static void LoadSettings() {
    vLanguage = DefaultInt(kLanguage, 1);
    vGermanAware = DefaultInt(kGerman, 1);
    vUseModernOrthography = DefaultInt(kModern, 1);
    vCheckSpelling = 1;
    vSetCheckSpelling();
    vRestoreIfWrongSpelling = 1;
    if (gDriver) gDriver->autoSwitch = DefaultInt(kAutoSwitch, 1) != 0;
    vAutoSwitchByTyping = DefaultInt(kAutoSwitch, 1);
}

static NSString* StringOf(const std::u16string& s) {
    return [NSString stringWithCharacters:(const unichar*)s.data() length:s.size()];
}

@interface MiKeyInputController : IMKInputController
@end

@implementation MiKeyInputController

- (instancetype)initWithServer:(IMKServer*)server delegate:(id)delegate client:(id)inputClient {
    self = [super initWithServer:server delegate:delegate client:inputClient];
    if (self && !gDriver) {
        gHook = (vKeyHookState*)vKeyInit();
        gDriver = new VikeyDriver();
        gComposing = [NSMutableString string];
        LoadSettings();
    }
    return self;
}

- (NSUInteger)recognizedEvents:(id)sender {
    return NSEventMaskKeyDown | NSEventMaskFlagsChanged;
}

#pragma mark - Marked text

- (void)showComposing:(id)client {
    NSDictionary* attrs = [self markForStyle:kTSMHiliteSelectedRawText atRange:NSMakeRange(0, gComposing.length)];
    NSAttributedString* s = [[NSAttributedString alloc] initWithString:gComposing attributes:attrs ?: @{}];
    [client setMarkedText:s selectionRange:NSMakeRange(gComposing.length, 0) replacementRange:NSMakeRange(NSNotFound, 0)];
}

/** Puts the word being typed into the document. */
- (void)commit:(id)client {
    if (gComposing.length == 0) return;
    NSString* s = [gComposing copy];
    [gComposing setString:@""];
    [client insertText:s replacementRange:NSMakeRange(NSNotFound, 0)];
}

/** Applies an engine edit: delete before the cursor, then insert. Deletes beyond the word being typed
 *  (a fix of the word before it) replace text already in the document. */
- (void)apply:(const VKEdit&)e client:(id)client {
    NSString* text = StringOf(e.text);
    NSUInteger del = (NSUInteger)MAX(0, e.deleteCount);
    if (del <= gComposing.length) {
        [gComposing deleteCharactersInRange:NSMakeRange(gComposing.length - del, del)];
        [gComposing appendString:text];
        [self showComposing:client];
        return;
    }
    NSUInteger excess = del - gComposing.length;
    [gComposing setString:@""];
    [self showComposing:client];
    NSRange sel = [client selectedRange];
    if (sel.location != NSNotFound && sel.location >= excess)
        [client insertText:text replacementRange:NSMakeRange(sel.location - excess, excess)];
    else
        [client insertText:text replacementRange:NSMakeRange(NSNotFound, 0)];
}

/** The cursor may be somewhere else now (click, shortcut, arrows, Return, another field): forget the word being
 *  typed and the engine's word history too. Otherwise a Backspace at the start of the next word brings back the
 *  previous word from the history, and the next keys are glued to it ("looxi" + "ddawng" -> "looxiddawng"). */
- (void)resetTyping {
    gForeign = false;
    if (!gDriver) return;
    vKeyHandleEvent(vKeyEvent::Mouse, vKeyEventState::MouseDown, 0);   //like a click: clears the word history
    gDriver->resetContext();
}

#pragma mark - Keys

static bool IsLetterOrDigit(unichar c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'); }

- (BOOL)handleEvent:(NSEvent*)event client:(id)sender {
    if (!gDriver || event.type != NSEventTypeKeyDown) return NO;
    NSEventModifierFlags flags = event.modifierFlags & NSEventModifierFlagDeviceIndependentFlagsMask;
    NSString* plain = event.charactersIgnoringModifiers.lowercaseString;

    // ⌥Z: Vietnamese <-> English/German (the same hotkey as the menu bar app)
    if ((flags & NSEventModifierFlagOption) && !(flags & (NSEventModifierFlagCommand | NSEventModifierFlagControl)) &&
        [plain isEqualToString:@"z"]) {
        [self commit:sender];
        gDriver->manualSwitch(CFAbsoluteTimeGetCurrent());
        gForeign = false;
        [Defaults() setInteger:vLanguage forKey:kLanguage];
        [self showLanguageHud:sender];
        return YES;
    }
    if (flags & (NSEventModifierFlagCommand | NSEventModifierFlagControl | NSEventModifierFlagOption)) {
        [self commit:sender];
        [self resetTyping];
        return NO;
    }

    unsigned short code = event.keyCode;
    bool shift = flags & NSEventModifierFlagShift;
    switch (code) {
        case 36: case 76: {            // Return, Enter: end the word, then let the app handle the key itself
            if (!gForeign) {
                VKEdit e = gDriver->press(KEY_RETURN, shift, CFAbsoluteTimeGetCurrent());
                if (!e.text.empty() && e.text.back() == u'\n') e.text.pop_back();
                [self apply:e client:sender];
            }
            [self commit:sender];
            [self resetTyping];
            return NO;
        }
        case 48:                       // Tab
            [self commit:sender];
            [self resetTyping];
            return NO;
        case 51: {                     // Backspace
            if (gComposing.length == 0 && gForeign) return NO;
            if (gComposing.length == 0) {
                // deleting a selection: the cursor is not after the previous word, so don't edit it
                NSRange sel = [sender selectedRange];
                if (sel.location != NSNotFound && sel.length > 0) { [self resetTyping]; return NO; }
            }
            VKEdit e = gDriver->press(KEY_DELETE, false, CFAbsoluteTimeGetCurrent());
            if (gComposing.length == 0 && e.deleteCount == 1 && e.text.empty()) return NO;   // the app deletes (and handles a selection)
            [self apply:e client:sender];
            return YES;
        }
        case 53: case 117: case 115: case 119: case 116: case 121: case 123: case 124: case 125: case 126:
            // Esc, forward delete, Home, End, Page Up/Down, arrows: the cursor moves, the word ends
            [self commit:sender];
            [self resetTyping];
            return NO;
    }

    NSString* chars = event.characters;
    if (chars.length == 0) {           // a dead key (´ ` ^ ¨ on German/Swiss layouts): an accented letter comes next
        [self foreignLetter:sender];
        return NO;
    }
    unichar c = [chars characterAtIndex:0];
    auto it = c < 0x80 ? _characterMap.find((Uint32)c) : _characterMap.end();
    if (it == _characterMap.end()) {
        // ä ö ü ß é à è ç...: the rest of this word is not Telex. A symbol (§ ° £ €) just ends the word.
        if ([[NSCharacterSet letterCharacterSet] characterIsMember:c]) [self foreignLetter:sender];
        else { [self commit:sender]; [self resetTyping]; }
        return NO;
    }
    if (gForeign) {
        if (IsLetterOrDigit(c)) return NO;   // still inside "über": typed as is
        gForeign = false;
        gDriver->resetContext();
    }
    Uint16 key = (Uint16)(it->second & 0xFFFF);
    bool caps = (it->second & CAPS_MASK) != 0;
    VKEdit e = gDriver->press(key, caps, CFAbsoluteTimeGetCurrent());
    // punctuation or a space that changed nothing: let the app type it (keeps its own auto-pairing etc.)
    if (!IsLetterOrDigit(c) && gComposing.length == 0 && e.deleteCount == 0 && e.text.size() == 1 && e.text[0] == c) return NO;
    [self apply:e client:sender];
    if (!IsLetterOrDigit(c)) [self commit:sender];
    return YES;
}

/** ä ö ü ß é... or a dead key inside a word: put the keys typed so far back as typed, end Telex for the word. */
- (void)foreignLetter:(id)sender {
    if (!gForeign && vLanguage == 1 && vKeyRestoreRawWord()) {
        VKEdit e;
        e.deleteCount = gHook->backspaceCount;
        for (int i = gHook->newCharCount - 1; i >= 0; i--) {
            Uint32 d = gHook->charData[i];
            e.text.push_back((d & CHAR_CODE_MASK) ? (char16_t)(d & 0xFFFF) : (char16_t)keyCodeToCharacter(d));
        }
        [self apply:e client:sender];
    }
    [self commit:sender];
    gDriver->resetContext();
    gForeign = true;
}

#pragma mark - Session

- (void)commitComposition:(id)sender {
    [self commit:sender];
    [self resetTyping];
}

- (void)activateServer:(id)sender {
    LoadSettings();
    [gComposing setString:@""];
    [self resetTyping];
}

- (void)deactivateServer:(id)sender {
    [self commit:sender];
    [self resetTyping];
}

#pragma mark - Language indicator

/** A small "VI" / "EN" label at the caret for a moment after ⌥Z. */
- (void)showLanguageHud:(id)client {
    NSRect caret = NSZeroRect;
    @try { [client attributesForCharacterIndex:0 lineHeightRectangle:&caret]; } @catch (NSException* e) {}
    if (NSIsEmptyRect(caret)) {
        NSPoint m = [NSEvent mouseLocation];
        caret = NSMakeRect(m.x, m.y, 1, 16);
    }
    if (!gHud) {
        gHud = [[NSPanel alloc] initWithContentRect:NSMakeRect(0, 0, 40, 24)
                                          styleMask:NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel
                                            backing:NSBackingStoreBuffered defer:YES];
        gHud.level = NSStatusWindowLevel;
        gHud.opaque = NO;
        gHud.backgroundColor = NSColor.clearColor;
        gHud.ignoresMouseEvents = YES;
        gHud.hasShadow = YES;
        NSTextField* label = [NSTextField labelWithString:@"VI"];
        label.font = [NSFont systemFontOfSize:13 weight:NSFontWeightBold];
        label.textColor = NSColor.whiteColor;
        label.alignment = NSTextAlignmentCenter;
        label.frame = NSMakeRect(0, 3, 40, 18);
        label.tag = 7;
        NSView* bg = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 40, 24)];
        bg.wantsLayer = YES;
        bg.layer.cornerRadius = 6;
        [bg addSubview:label];
        gHud.contentView = bg;
    }
    NSView* bg = gHud.contentView;
    bg.layer.backgroundColor = (vLanguage ? [NSColor colorWithRed:0.31 green:0.27 blue:0.90 alpha:0.95]
                                          : [NSColor colorWithWhite:0.25 alpha:0.95]).CGColor;
    ((NSTextField*)[bg viewWithTag:7]).stringValue = vLanguage ? @"VI" : @"EN";
    [gHud setFrameOrigin:NSMakePoint(NSMinX(caret), NSMinY(caret) - 28)];
    [gHud orderFrontRegardless];
    static int shown = 0;
    int mine = ++shown;
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.8 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        if (mine == shown) [gHud orderOut:nil];
    });
}

#pragma mark - Menu (the input menu in the menu bar)

- (NSMenu*)menu {
    NSMenu* m = [[NSMenu alloc] initWithTitle:@"MiKey"];
    NSMenuItem* (^add)(NSString*, NSInteger, BOOL) = ^NSMenuItem*(NSString* title, NSInteger tag, BOOL on) {
        NSMenuItem* i = [[NSMenuItem alloc] initWithTitle:title action:@selector(menuAction:) keyEquivalent:@""];
        i.tag = tag;
        i.state = on ? NSControlStateValueOn : NSControlStateValueOff;
        [m addItem:i];
        return i;
    };
    add(@"Tiếng Việt (Telex)", TagVietnamese, vLanguage == 1);
    add(@"English / Deutsch", TagEnglish, vLanguage == 0);
    NSMenuItem* hint = [[NSMenuItem alloc] initWithTitle:@"Chuyển nhanh: ⌥Z" action:nil keyEquivalent:@""];
    hint.enabled = NO;
    [m addItem:hint];
    [m addItem:[NSMenuItem separatorItem]];
    add(@"Tự chuyển ngôn ngữ khi gõ", TagAutoSwitch, DefaultInt(kAutoSwitch, 1) != 0);
    add(@"Nhận biết tiếng Đức (wir, der, dass…)", TagGerman, vGermanAware != 0);
    add(@"Bỏ dấu kiểu mới (hoà, thuý)", TagModern, vUseModernOrthography != 0);
    [m addItem:[NSMenuItem separatorItem]];
    add(@"Giới thiệu MiKey…", TagAbout, NO);
    return m;
}

- (void)menuAction:(id)sender {
    NSMenuItem* item = [sender isKindOfClass:[NSDictionary class]] ? sender[kIMKCommandMenuItemName] : sender;
    id client = self.client;
    switch (item.tag) {
        case TagVietnamese: case TagEnglish: {
            int lang = item.tag == TagVietnamese ? 1 : 0;
            [self commit:client];
            gDriver->setLanguage(lang);
            [Defaults() setInteger:lang forKey:kLanguage];
            break;
        }
        case TagAutoSwitch: [Defaults() setInteger:DefaultInt(kAutoSwitch, 1) ? 0 : 1 forKey:kAutoSwitch]; LoadSettings(); break;
        case TagGerman: [Defaults() setInteger:vGermanAware ? 0 : 1 forKey:kGerman]; LoadSettings(); break;
        case TagModern: [Defaults() setInteger:vUseModernOrthography ? 0 : 1 forKey:kModern]; LoadSettings(); break;
        case TagAbout: {
            [NSApp activateIgnoringOtherApps:YES];
            NSAlert* a = [NSAlert new];
            a.messageText = @"MiKey";
            a.informativeText = @"Bộ gõ tiếng Việt Telex, tự nhận ra tiếng Anh và tiếng Đức.\n⌥Z: chuyển Tiếng Việt ↔ English/Deutsch.\n\nDựa trên Vikey (Tony Dinh) và OpenKey (Tuyen Mai). GPL-3.0.";
            [a runModal];
            break;
        }
    }
    [Defaults() synchronize];
}

@end
