// Types lines through Engine/Driver exactly like the MiKey input method does (no harness logic).
// stdin: "<start lang 1|0>\t<keys>" per line ('|' = Enter, '<' = Backspace); prints the resulting text.
// usage: drvtype [--german]
#include "Driver.h"
#include <cstdio>
#include <cstring>
#include <string>
int vLanguage = 1, vSwitchKeyStatus = 0, vCheckSpelling = 1, vUseModernOrthography = 1, vRestoreIfWrongSpelling = 1,
    vFixRecommendBrowser = 0, vUseSmartSwitchKey = 0, vOtherLanguage = 0, vAutoSwitchByTyping = 1;
extern map<Uint32, Uint32> _characterMap;

static std::string utf8(const std::u16string& s) {
    std::string o;
    for (char16_t c : s) {
        if (c < 0x80) o += (char)c;
        else if (c < 0x800) { o += (char)(0xC0 | (c >> 6)); o += (char)(0x80 | (c & 0x3F)); }
        else { o += (char)(0xE0 | (c >> 12)); o += (char)(0x80 | ((c >> 6) & 0x3F)); o += (char)(0x80 | (c & 0x3F)); }
    }
    return o;
}

int main(int argc, char** argv) {
    if (argc > 1 && !strcmp(argv[1], "--german")) vGermanAware = 1;
    vKeyInit();
    VikeyDriver d;
    char buf[4096];
    double now = 100;
    while (fgets(buf, sizeof buf, stdin)) {
        buf[strcspn(buf, "\n")] = 0;
        char* tab = strchr(buf, '\t'); if (!tab) continue;
        d.setLanguage(atoi(buf));
        d.resetContext();
        std::u16string screen;
        for (char* p = tab + 1; *p; p++) {
            now += 0.2;
            Uint16 key; bool shift = false;
            if (*p == '|') key = KEY_RETURN;
            else if (*p == '<') key = KEY_DELETE;
            else {
                auto it = _characterMap.find((Uint32)(unsigned char)*p);
                if (it == _characterMap.end()) continue;
                key = (Uint16)(it->second & 0xFFFF); shift = (it->second & CAPS_MASK) != 0;
            }
            VKEdit e = d.press(key, shift, now);
            if (getenv("EDITS")) fprintf(stderr, "  key %c: delete %d, insert \"%s\"%s\n", *p, e.deleteCount, utf8(e.text).c_str(), e.languageChanged ? " (language changed)" : "");
            for (int i = 0; i < e.deleteCount && !screen.empty(); i++) screen.pop_back();
            screen += e.text;
        }
        printf("%s\t%d\n", utf8(screen).c_str(), d.language());
    }
}
