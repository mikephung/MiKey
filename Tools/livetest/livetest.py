#!/usr/bin/env python3
"""Live typing test for the MiKey input method on this Mac.

Types every case into a TextEdit document through the real MiKey input source (real key presses, the
keyboard layout in use), reads the document back and compares. Cases: Tools/livetest/cases.tsv plus
Tools/autoswitch/test/de_cases.tsv. It takes over the keyboard while it runs: don't type meanwhile.

usage: python3 Tools/livetest/livetest.py [filter]
Needs: MiKey installed (Tools/build_inputmethod.sh install), Accessibility permission for the app that
runs this (Terminal, iTerm, Kiro). Exit code = number of failures."""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
TYPER = "/tmp/mikey-typer"
MIKEY = "com.mikey.inputmethod.MiKey"

def osa(script):
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.rstrip("\n")

def build_typer():
    src = os.path.join(HERE, "typer.swift")
    if not os.path.exists(TYPER) or os.path.getmtime(TYPER) < os.path.getmtime(src):
        subprocess.run(["swiftc", "-O", "-o", TYPER, src], check=True)

def load_cases():
    cases = []
    for path in (os.path.join(HERE, "cases.tsv"), os.path.join(ROOT, "Tools", "autoswitch", "test", "de_cases.tsv")):
        for line in open(path, encoding="utf-8"):
            if not line.strip() or line.startswith("#"): continue
            f = line.rstrip("\n").split("\t")
            cases.append((f[0], f[1], f[2], f[4] if len(f) > 4 else os.path.basename(path)))
    return cases

def set_language(lang):
    # the input menu items are the reliable way, but they need UI scripting; ⌥Z toggles and the
    # language is read back from MiKey's defaults
    cur = subprocess.run(["defaults", "read", MIKEY, "Language"], capture_output=True, text=True).stdout.strip() or "1"
    if cur != lang:
        subprocess.run([TYPER, "type", "{optz}"]); time.sleep(0.3)

def main():
    build_typer()
    filt = sys.argv[1] if len(sys.argv) > 1 else None
    osa('tell application "TextEdit" to activate')
    osa('tell application "TextEdit" to if (count of documents) = 0 then make new document')
    time.sleep(1)
    if subprocess.run([TYPER, "select", MIKEY]).returncode != 0:
        sys.exit("MiKey input source not found: run Tools/build_inputmethod.sh install")
    time.sleep(0.5)
    print("input source:", subprocess.run([TYPER, "current"], capture_output=True, text=True).stdout.strip())
    fails = total = 0
    for start, keys, expected, why in load_cases():
        if filt and filt not in keys: continue
        total += 1
        osa('tell application "TextEdit" to set text of front document to ""')
        osa('tell application "TextEdit" to activate')
        time.sleep(0.25)
        set_language(start)
        # a click-free fresh start: Return then Backspace ends any word MiKey still holds
        r = subprocess.run([TYPER, "type", keys])
        if r.returncode == 3: sys.exit("give the Accessibility permission to the app running this test, then run it again")
        time.sleep(0.4)
        got = osa('tell application "TextEdit" to get text of front document')
        want = expected.replace("|", "\n")
        # TextEdit ends the text with the last key; compare without a trailing newline difference
        ok = got.rstrip("\n") == want.rstrip("\n")
        if not ok: fails += 1
        print(("ok   " if ok else "FAIL ") + f"{keys!r} -> {got!r}" + ("" if ok else f"   want {want!r}  ({why})"))
    print(f"live: {total - fails}/{total} pass")
    sys.exit(fails)

if __name__ == "__main__": main()
