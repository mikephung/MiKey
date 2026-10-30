#!/usr/bin/env python3
"""Signs the release files with MiKey's ed25519 key (Sparkle's EdDSA format: base64 of the 64-byte signature over the
whole file) and writes the appcast item for this version to <dist>/appcast-item.xml, plus the full feed
site-mikey/appcast.xml (newest first). The Windows app reads <enclosure sparkle:os="windows" mikey:arch=...>.

usage: mikey_appcast.py <version> <dist dir>
Key: ~/.mikey/release/ed25519_private.pem (MIKEY_ED25519_KEY overrides)."""
import base64, datetime, glob, os, re, sys
from cryptography.hazmat.primitives import serialization

ver, dist = sys.argv[1], sys.argv[2]
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
key_path = os.environ.get("MIKEY_ED25519_KEY", os.path.expanduser("~/.mikey/release/ed25519_private.pem"))
key = serialization.load_pem_private_key(open(key_path, "rb").read(), password=None)
BASE = f"https://github.com/mikephung/MiKey/releases/download/v{ver}"

def enclosure(path, os_name, arch=None):
    data = open(path, "rb").read()
    sig = base64.b64encode(key.sign(data)).decode()
    extra = f' mikey:arch="{arch}"' if arch else ""
    return (f'<enclosure url="{BASE}/{os.path.basename(path)}" length="{len(data)}" type="application/octet-stream" '
            f'sparkle:os="{os_name}"{extra} sparkle:edSignature="{sig}"/>')

encl = [enclosure(p, "macos") for p in sorted(glob.glob(os.path.join(dist, "MiKey-*-macOS.pkg")))]
# Windows installers (downloaded from the GitHub release into dist after CI): signed here too
for p in sorted(glob.glob(os.path.join(dist, "MiKey-*-*-Setup.exe"))):
    arch = re.search(r"-(x64|arm64)-Setup\.exe$", p).group(1)
    encl.append(enclosure(p, "windows", arch))

notes_path = os.path.join(dist, "notes.md")
notes = open(notes_path, encoding="utf-8").read() if os.path.exists(notes_path) else f"MiKey {ver}"
date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
item = (f"    <item>\n      <title>MiKey {ver}</title>\n      <pubDate>{date}</pubDate>\n"
        f"      <sparkle:version>{ver}</sparkle:version>\n      <sparkle:shortVersionString>{ver}</sparkle:shortVersionString>\n"
        f"      <description><![CDATA[{notes}]]></description>\n" + "".join(f"      {e}\n" for e in encl) + "    </item>\n")
open(os.path.join(dist, "appcast-item.xml"), "w", encoding="utf-8").write(item)

feed_path = os.path.join(ROOT, "site-mikey", "appcast.xml")
head = ('<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle" '
        'xmlns:mikey="https://mikey.mikephung.com/xmlns">\n  <channel>\n    <title>MiKey</title>\n    <link>https://mikey.mikephung.com</link>\n')
items = []
if os.path.exists(feed_path):
    old = open(feed_path, encoding="utf-8").read()
    items = [m for m in re.findall(r"    <item>.*?</item>\n", old, re.S) if f"<sparkle:version>{ver}</sparkle:version>" not in m]
os.makedirs(os.path.dirname(feed_path), exist_ok=True)
open(feed_path, "w", encoding="utf-8").write(head + item + "".join(items) + "  </channel>\n</rss>\n")
print(f"signed {len(encl)} file(s); appcast item: {dist}/appcast-item.xml; feed: {feed_path}")
