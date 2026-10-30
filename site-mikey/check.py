#!/usr/bin/env python3
"""Checks the built site: HTML parses, every local link/src points to an existing file, every page has a lang,
one h1, a title and alt on images. usage: python3 site-mikey/check.py"""
import os, sys
from html.parser import HTMLParser
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__))

class P(HTMLParser):
    def __init__(self): super().__init__(); self.refs, self.h1, self.lang, self.title, self.noalt = [], 0, None, False, 0
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html": self.lang = a.get("lang")
        if tag == "h1": self.h1 += 1
        if tag == "title": self.title = True
        if tag == "img" and "alt" not in a: self.noalt += 1
        for k in ("href", "src"):
            if k in a and tag != "link" or (tag == "link" and k == "href" and a.get("rel") in ("stylesheet", "icon", "apple-touch-icon")):
                if a.get(k): self.refs.append(a[k])

bad = 0
pages = sorted(os.path.join(d, f) for d, _, fs in os.walk(HERE) for f in fs if f.endswith(".html"))
# every page exists in all three languages
rels = {os.path.relpath(p, HERE) for p in pages}
for r in sorted(rels):
    if r.startswith(("de/", "en/")) or r == "404.html": continue
    for pre in ("de/", "en/"):
        if pre + r not in rels: print(f"FAIL missing translation {pre + r}"); bad += 1
for page in pages:
    p = P(); p.feed(open(page, encoding="utf-8").read())
    rel = os.path.relpath(page, HERE)
    problems = []
    if not p.lang: problems.append("no lang")
    if p.h1 != 1: problems.append(f"{p.h1} h1")
    if not p.title: problems.append("no title")
    if p.noalt: problems.append(f"{p.noalt} img without alt")
    for r in p.refs:
        u = urlparse(r)
        if u.scheme or r.startswith("#") or r.startswith("mailto:"): continue
        base = HERE if u.path.startswith("/") else os.path.dirname(page)   # /style.css: from the site root (404.html)
        target = os.path.normpath(os.path.join(base, u.path.lstrip("/")))
        if os.path.isdir(target): target = os.path.join(target, "index.html")
        if not os.path.exists(target): problems.append(f"missing {r}")
    print(("ok   " if not problems else "FAIL ") + rel + ("" if not problems else ": " + ", ".join(problems)))
    bad += bool(problems)
sys.exit(bad)
