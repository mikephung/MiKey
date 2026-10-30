//
//  main.mm
//  MiKey input method: a real macOS input source (System Settings > Keyboard > Input Sources > + > Vietnamese > MiKey).
//  Same engine as the menu bar app, but through InputMethodKit: no Accessibility permission, no event tap.
//
#import <Cocoa/Cocoa.h>
#import <InputMethodKit/InputMethodKit.h>

IMKServer* gMiKeyServer = nil;

int main(int argc, const char* argv[]) {
    @autoreleasepool {
        NSString* connection = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"InputMethodConnectionName"];
        gMiKeyServer = [[IMKServer alloc] initWithName:connection bundleIdentifier:[[NSBundle mainBundle] bundleIdentifier]];
        [NSApplication sharedApplication];
        [NSApp run];
    }
    return 0;
}
