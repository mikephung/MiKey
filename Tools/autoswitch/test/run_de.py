#!/usr/bin/env python3
"""German/Swiss user cases (de_cases.tsv) against the harness with German-aware auto switch on."""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
H = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'harness')
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'de_cases.tsv'), encoding='utf-8')
        if l.strip() and not l.startswith('#')]
inp = ''.join(f"{r[0]}\t{r[1]}\n" for r in rows)
env = dict(os.environ, VIKEY_GERMAN=os.environ.get('VIKEY_GERMAN', '1'))
out = subprocess.run([H, 'lines'], input=inp, capture_output=True, text=True, env=env).stdout
# "<text>\t<switches>\t<lang>" per case; text may contain newlines from Enter
parts = out.split('\t'); res = []; text = parts[0]
for k in range(1, len(parts)):
    if k % 2 == 0:
        lang, _, rest = parts[k].partition('\n'); res.append((text, lang)); text = rest
fail = 0
for r, (text, lang) in zip(rows, res):
    want = r[2].replace('|', '\n')
    ok = text == want and lang == r[3]
    if not ok: fail += 1
    print(('PASS ' if ok else 'FAIL ') + f"{r[1]!r} -> {text!r} lang={lang}" + ('' if ok else f"   want {want!r} lang={r[3]}  ({r[4]})"))
print(f"german: {len(rows) - fail}/{len(rows)} pass")
sys.exit(1 if fail else 0)
