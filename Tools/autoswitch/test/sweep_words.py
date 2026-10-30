#!/usr/bin/env python3
"""Types hazard words (English, German ASCII) in Vietnamese mode followed by each break key and
reports every word the engine changes. usage: sweep_words.py [harness path]"""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
H = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'harness')
EN = """text next six box fix mix tax index exit exam example express expect explain extra excel xml linux flex apex max relax
just job jobs json major project object subject reject first for if of file from full left life after software
zoom size zero prize lazy azure organize realize
are more your word world start or work window show know new now how low view www draw saw law
add odd address see feed need good book look keep deep week coffee all will call class pass miss boss less press access process success
user users sudo git push pull branch commit merge release deploy server client database query response request
the this that was is as his has does goes yes
interest design tomorrow tweet street sweet meet issue use sure measure
email gmail iphone macbook wifi password username okay thanks please sorry hello
ok vs pdf html css api url ssh download upload ssl contexts texts""".split()
DE = """ist das was wir sie nicht und der die den dem ein eine mit von nach auch aber oder wenn dann noch schon sehr hier dort
heute morgen gestern immer wieder jetzt bitte danke gut ja nein doch kann muss will soll darf mich dich mir dir ihm ihr uns euch
wirklich vielleicht eigentlich natuerlich weiss grosse strasse fuss dass lassen essen wissen
haben sein werden worden wurde wurden gewesen gehen gehe gehst geht kommen komme kommst kommt
machen mache machst macht sagen sage sagst sagt fahren fahre
Montag Dienstag Mittwoch Donnerstag Freitag Samstag Sonntag
Schule Haus Auto Zug Bahn Arbeit Zeit Woche Monat Jahr
nur man mal wo wie wer warum weil wann welche""".split()
BREAKS = [' ', ',', '.', ';', '?', ')', '\n']
def run(words, start='1'):
    bad = []
    for b in BREAKS:
        inp = ''.join(f"{start}\t{w}{b}\n" for w in words)
        # harness output: text \t switches \t lang, text may contain a newline for Enter
        out = subprocess.run([H, 'lines'], input=inp.replace('\n\n', '\n|\n'), capture_output=True, text=True).stdout
        lines = out.split('\n')
        for w, l in zip(words, lines):
            t = l.split('\t')[0]
            if b == '\n': continue
            if t != w + b: bad.append((w + repr(b), t))
    return bad
for name, words in (('EN', EN), ('DE', DE)):
    bad = run(words)
    print(name, len(bad), 'bad of', len(words) * (len(BREAKS) - 1))
    seen = set()
    for w, t in bad:
        if w.split("'")[0] in seen: continue
        seen.add(w.split("'")[0]); print('  ', w, '->', t)
