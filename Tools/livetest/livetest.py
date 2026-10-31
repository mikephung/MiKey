#!/usr/bin/env python3
"""Live typing test for the MiKey input method on this Mac.

Types every case through the real MiKey input source (real key presses, the keyboard layout in use) into an
app, reads the field back with ⌘A ⌘C and compares. Cases: Tools/livetest/cases.tsv + Tools/autoswitch/test/de_cases.tsv.
It takes over the keyboard while it runs: don't type meanwhile.

usage: python3 Tools/livetest/livetest.py [--app chrome|safari|textedit] [filter]   (default: chrome)
Needs: MiKey installed (Tools/build_inputmethod.sh install), Accessibility permission for the app that runs
this (Terminal, iTerm, Kiro). TextEdit's own auto-capitalization and auto-correction are turned off for the
run and put back afterwards. Exit code = number of failures."""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
TYPER = "/tmp/mikey-typer"
MIKEY = "com.mikey.inputmethod.MiKey"
PAGE = "/tmp/mikey-livetest.html"
APPS = {"textedit": "TextEdit", "chrome": "Google Chrome", "safari": "Safari"}
TEXTEDIT_KEYS = ["NSAutomaticCapitalizationEnabled", "NSAutomaticSpellingCorrectionEnabled", "NSAutomaticTextReplacementEnabled",
                 "NSAutomaticQuoteSubstitutionEnabled", "NSAutomaticDashSubstitutionEnabled", "NSAutomaticPeriodSubstitutionEnabled"]

def run(*a, **k): return subprocess.run(list(a), capture_output=True, text=True, **k)
def osa(script): return run("osascript", "-e", script).stdout.rstrip("\n")
def typer(*a): return subprocess.run([TYPER, *a])

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

def set_language(lang, layout):
    # MiKey reads its settings when it becomes the input source again: no ⌥Z (a manual switch pauses auto switch for 5 s)
    run("defaults", "write", MIKEY, "Language", "-int", lang)
    typer("select", layout); time.sleep(0.15)
    typer("select", MIKEY); time.sleep(0.5)   # MiKey must be active again before the first key

def textedit_prefs(off):
    saved = {}
    for k in TEXTEDIT_KEYS:
        r = run("defaults", "read", "com.apple.TextEdit", k)
        saved[k] = r.stdout.strip() if r.returncode == 0 else None
        run("defaults", "write", "com.apple.TextEdit", k, "-bool", "false")
    return saved

def restore_textedit(saved):
    for k, v in saved.items():
        if v is None: run("defaults", "delete", "com.apple.TextEdit", k)
        else: run("defaults", "write", "com.apple.TextEdit", k, "-bool", "true" if v == "1" else "false")

def open_target(app):
    name = APPS[app]
    if app == "textedit":
        # never quit TextEdit: unsaved documents would ask to be saved and the keys would land in that dialog.
        # The turned-off auto-correction applies if TextEdit wasn't running yet.
        osa('tell application "TextEdit" to activate')
        osa('tell application "TextEdit" to make new document'); time.sleep(1)
    else:
        open(PAGE, "w").write('<!doctype html><meta charset="utf-8"><title>MiKey live test</title>'
                              '<textarea autofocus spellcheck="false" autocapitalize="off" autocorrect="off" '
                              'style="width:90vw;height:80vh;font-size:20px"></textarea>')
        run("open", "-a", name, PAGE); time.sleep(2.5)
    osa(f'tell application "{name}" to activate'); time.sleep(0.5)

def front_app():
    return osa('tell application "System Events" to get name of first process whose frontmost is true')

def ensure_front(name):
    """Never type into another app: stop the run when the target app isn't in front."""
    for _ in range(3):
        if front_app() == name: return
        osa(f'tell application "{name}" to activate'); time.sleep(0.5)
    sys.exit(f"stopped: {front_app()!r} is in front instead of {name!r} (nothing more is typed)")

def read_field():
    run("pbcopy", input="\u2063")                 # a marker: tells "copied nothing" from "copied empty"
    typer("type", "{cmda}{cmdc}"); time.sleep(0.35)
    return run("pbpaste").stdout

def main():
    args = sys.argv[1:]
    app = "chrome"   # a plain textarea: no auto-capitalization, no auto-correction
    if args[:1] == ["--app"]: app, args = args[1], args[2:]
    filt = args[0] if args else None
    build_typer()
    saved_clip = run("pbpaste").stdout
    saved = textedit_prefs(True) if app == "textedit" else {}
    try:
        fails = 0
        if typer("select", MIKEY).returncode != 0:
            sys.exit("MiKey input source not found: run Tools/build_inputmethod.sh install")
        time.sleep(0.4)
        cur = run(TYPER, "current").stdout.strip()
        layout = cur.split(" / ")[-1]
        print("input source:", cur, "| app:", APPS[app])
        open_target(app)
        fails = total = 0
        for start, keys, expected, why in load_cases():
            if filt and filt not in keys: continue
            total += 1
            ensure_front(APPS[app])
            set_language(start, layout)
            ensure_front(APPS[app])
            typer("type", "{cmda}{del}"); time.sleep(0.15)
            ensure_front(APPS[app])
            r = typer("type", keys)
            if r.returncode == 3: sys.exit("give the Accessibility permission to the app running this test, then run it again")
            time.sleep(0.35)
            ensure_front(APPS[app])
            got = read_field()
            want = expected.replace("|", "\n")
            ok = got.rstrip("\n") == want.rstrip("\n")
            if not ok: fails += 1
            print(("ok   " if ok else "FAIL ") + f"{keys!r} -> {got!r}" + ("" if ok else f"   want {want!r}  ({why})"))
        ensure_front(APPS[app])
        typer("type", "{cmda}{del}")
        print(f"live ({APPS[app]}): {total - fails}/{total} pass")
    finally:
        if saved: restore_textedit(saved)
        run("pbcopy", input=saved_clip)
    sys.exit(fails)

if __name__ == "__main__": main()
