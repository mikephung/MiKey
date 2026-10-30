#!/usr/bin/env python3
"""Builds the MiKey landing page (mikey.mikephung.com) in Vietnamese (/), German (/de/) and English (/en/)
from one template, so the three pages always have the same sections. usage: python3 site-mikey/build.py"""
import html, os
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://mikey.mikephung.com"
REPO = "https://github.com/mikephung/MiKey"
DL = REPO + "/releases/latest"

# Demo rows: keys typed, what plain Telex gives, what MiKey gives (all checked in Tools/autoswitch/test/de_cases.tsv)
DEMO = [("text", "tẽt", "text"), ("wir", "ửi", "wir"), ("der", "dẻ", "der"), ("über", "ơber", "über"), ("osx", "õ", "osx")]
# "Plain Telex" column: Tools/autoswitch/test/harness with VIKEY_AUTO_OFF=1; über/Café as on a Swiss keyboard before MiKey
FIXES = [("text", "tẽt", "text"), ("wir", "ửi", "wir"), ("der", "dẻ", "der"), ("dass", "das", "dass"), ("wissen", "ưisen", "wissen"),
         ("über", "ơber", "über"), ("Café", "Càé", "Café"), ("osx", "õ", "osx"), ("server", "sẻver", "server")]
TELEX = [("aa", "â"), ("aw", "ă"), ("ee", "ê"), ("oo", "ô"), ("ow", "ơ"), ("uw", "ư"), ("dd", "đ"),
         ("s", "´ sắc"), ("f", "` huyền"), ("r", "̉ hỏi"), ("x", "~ ngã"), ("j", ". nặng"), ("z", "×")]

T = {
 "vi": dict(path="", lang="vi", name="Tiếng Việt",
   title="MiKey: bộ gõ tiếng Việt cho người Việt ở Đức và Thụy Sĩ",
   desc="Bộ gõ Telex cho macOS và Windows, tự nhận ra tiếng Anh và tiếng Đức. text không còn thành tẽt, wir không thành ửi, ü không thành ơ. Miễn phí, mã nguồn mở.",
   skip="Bỏ qua, đến nội dung",
   h1="Gõ tiếng Việt, tiếng Đức và tiếng Anh. Không cần đổi bàn phím.",
   lead="MiKey là bộ gõ Telex cho người Việt sống ở Đức, Thụy Sĩ, Áo. Nó tự nhận ra khi bạn gõ tiếng Anh hay tiếng Đức, và các phím ä ö ü cứ thế mà dùng.",
   dl_mac="Tải cho macOS", dl_win="Tải cho Windows", meta="macOS 13 trở lên · Windows 10/11 · Miễn phí · Mã nguồn mở (GPL-3.0)",
   demo_label="Ví dụ: gõ phím, Telex thường và MiKey", d_keys="Phím gõ", d_bad="Telex thường", d_good="MiKey",
   why_h="Hết những lỗi ngớ ngẩn khi gõ", why_p="Telex biến các chữ cái s f r x j w thành dấu. Với tiếng Việt thì tiện, nhưng với chữ nước ngoài thì hỏng. MiKey biết khoảng 70.000 từ tiếng Anh và tiếng Đức, nên các từ đó giữ nguyên.",
   t_keys="Bạn gõ", t_bad="Telex thường ra", t_good="MiKey ra",
   f=[("Phím ä ö ü cứ thế dùng", "Trên bàn phím Đức và Thụy Sĩ, ü nằm đúng chỗ phím [ của Telex nên hay bị biến thành ơ. MiKey để yên ä ö ü ß é: über, Grüße, Café, Zürich."),
      ("Hiểu tiếng Đức", "wir, der, nur, dass, wissen không bị đổi thành ửi, dẻ, nủ, das, ưisen. Có thể tắt trong menu nếu bạn không cần."),
      ("Hiểu tiếng Anh và từ công nghệ", "text, server, the best test, osx, macos, exe giữ nguyên. Các từ tiếng Việt thường gặp như gì, ít vẫn luôn là tiếng Việt."),
      ("Chuyển nhanh bằng ⌥Z / Alt+Z", "Một phím để đổi Việt ↔ Anh/Đức, có nhãn VI/EN hiện ngay ở con trỏ."),
      ("Sửa sai thì bấm Backspace", "Nếu MiKey đoán sai một từ, bấm Backspace ngay sau đó là từ trở lại như bạn gõ."),
      ("Mọi thứ ở trên máy bạn", "Không gửi gì lên mạng. Trên Mac, MiKey là một input source thật, không cần quyền Accessibility.")],
   inst_h="Cài đặt", mac_h="macOS",
   mac=["Tải <b>MiKey-…-macOS.pkg</b> từ trang phát hành và mở nó.",
        "Lần đầu macOS sẽ hỏi vì gói chưa được Apple ký: chuột phải vào file › <b>Open</b>, hoặc vào System Settings › Privacy &amp; Security › <b>Open Anyway</b>.",
        "Vào System Settings › Keyboard › Input Sources › <b>Edit…</b> › <b>+</b> › Vietnamese › <b>MiKey</b>.",
        "Chọn <b>MiKey</b> trong menu bàn phím trên thanh menu. Xong."],
   win_h="Windows",
   win=["Tải <b>MiKey-…-x64-Setup.exe</b> (hoặc arm64) từ trang phát hành.",
        "Windows SmartScreen có thể cảnh báo vì bản cài chưa được ký: bấm <b>More info</b> › <b>Run anyway</b>.",
        "MiKey nằm ở khay hệ thống. <kbd>Alt</kbd>+<kbd>Z</kbd> để chuyển Việt ↔ Anh/Đức."],
   linux="Linux (IBus): sắp có.",
   telex_h="Bảng Telex", telex_p="Gõ dấu sau chữ cái, ở bất kỳ đâu trong từ: truowfng, truongwf và truwowngf đều ra trường.",
   faq_h="Câu hỏi thường gặp",
   faq=[("MiKey có miễn phí không?", "Có. MiKey miễn phí và là mã nguồn mở (GPL-3.0). Mã nguồn ở GitHub."),
        ("MiKey có gửi những gì tôi gõ đi đâu không?", "Không. Mọi xử lý diễn ra trên máy bạn. MiKey không có quảng cáo, không đo đếm, không tài khoản."),
        ("Trên Mac có cần cấp quyền Accessibility không?", "Không. MiKey là một input source của macOS, giống bàn phím ABC hay Schweiz, deutsch."),
        ("Một từ bị đoán sai thì sao?", "Bấm Backspace ngay sau đó để lấy lại đúng chữ bạn gõ. Nếu không cần nhận biết tiếng Đức, tắt mục \"Nhận biết tiếng Đức\" trong menu bàn phím."),
        ("Tôi dùng bàn phím Đức hoặc Thụy Sĩ (QWERTZ) được không?", "Được, MiKey làm cho chính các bàn phím đó. Nó đọc chữ in trên phím của layout bạn đang dùng, nên z/y và ä ö ü đều đúng."),
        ("MiKey khác Vikey và OpenKey thế nào?", "MiKey dựa trên Vikey (Tony Dinh), mà Vikey lại dựa trên OpenKey (Tuyen Mai). MiKey thêm phần dành cho người Việt ở vùng nói tiếng Đức: phím umlaut, từ tiếng Đức, từ công nghệ.")],
   credits="MiKey dựa trên <a href=\"https://github.com/trungdq88/Vikey\">Vikey</a> của Tony Dinh và <a href=\"https://github.com/tuyenvm/OpenKey\">OpenKey</a> của Tuyen Mai. Dữ liệu tần suất từ: FrequencyWords (Hermit Dave, OpenSubtitles 2018, CC BY-SA 4.0).",
   license="Giấy phép GPL-3.0 · <a href=\"" + REPO + "\">Mã nguồn trên GitHub</a> · <a href=\"" + REPO + "/issues\">Báo lỗi</a>",
   by="Làm bởi <a href=\"https://mikephung.com\">Mike Phung</a>."),
 "de": dict(path="de/", lang="de", name="Deutsch",
   title="MiKey: vietnamesische Tastatur für Vietnamesinnen und Vietnamesen in der Schweiz und in Deutschland",
   desc="Telex-Eingabe für macOS und Windows, die Englisch und Deutsch selbst erkennt: aus text wird nicht tẽt, aus wir nicht ửi, aus ü nicht ơ. Gratis und Open Source.",
   skip="Zum Inhalt springen",
   h1="Vietnamesisch, Deutsch und Englisch tippen. Ohne die Tastatur zu wechseln.",
   lead="MiKey ist eine vietnamesische Telex-Eingabe für alle, die in der Schweiz, in Deutschland oder Österreich leben. Sie erkennt englische und deutsche Wörter selbst, und die Tasten ä ö ü funktionieren einfach.",
   dl_mac="Für macOS laden", dl_win="Für Windows laden", meta="macOS 13 oder neuer · Windows 10/11 · Gratis · Open Source (GPL-3.0)",
   demo_label="Beispiel: Tasten, normales Telex und MiKey", d_keys="Tasten", d_bad="Normales Telex", d_good="MiKey",
   why_h="Schluss mit den typischen Telex-Fehlern", why_p="Telex macht aus den Buchstaben s f r x j w Akzente. Für Vietnamesisch praktisch, für fremde Wörter fatal. MiKey kennt rund 70'000 englische und deutsche Wörter und lässt sie, wie sie sind.",
   t_keys="Getippt", t_bad="Normales Telex", t_good="MiKey",
   f=[("ä ö ü einfach tippen", "Auf Schweizer und deutschen Tastaturen liegt ü dort, wo Telex die Taste [ erwartet, und wurde zu ơ. MiKey lässt ä ö ü ß é in Ruhe: über, Grüsse, Café, Zürich."),
      ("Versteht Deutsch", "wir, der, nur, dass, wissen werden nicht zu ửi, dẻ, nủ, das, ưisen. Im Menü abschaltbar."),
      ("Versteht Englisch und Tech-Wörter", "text, server, the best test, osx, macos, exe bleiben stehen. Häufige vietnamesische Wörter wie gì oder ít bleiben vietnamesisch."),
      ("Umschalten mit ⌥Z / Alt+Z", "Eine Taste für Vietnamesisch ↔ Englisch/Deutsch, mit einem kleinen VI/EN-Hinweis beim Cursor."),
      ("Falsch erkannt? Rücktaste", "Hat MiKey ein Wort falsch erkannt, holt die Rücktaste direkt danach das Getippte zurück."),
      ("Alles bleibt auf deinem Gerät", "Nichts wird ins Internet geschickt. Auf dem Mac ist MiKey eine echte Eingabequelle, ohne Bedienungshilfen-Berechtigung.")],
   inst_h="Installation", mac_h="macOS",
   mac=["<b>MiKey-…-macOS.pkg</b> von der Release-Seite laden und öffnen.",
        "Beim ersten Mal fragt macOS nach, weil das Paket nicht von Apple signiert ist: Rechtsklick auf die Datei › <b>Öffnen</b>, oder Systemeinstellungen › Datenschutz &amp; Sicherheit › <b>Trotzdem öffnen</b>.",
        "Systemeinstellungen › Tastatur › Eingabequellen › <b>Bearbeiten…</b> › <b>+</b> › Vietnamesisch › <b>MiKey</b>.",
        "<b>MiKey</b> im Eingabemenü in der Menüleiste wählen. Fertig."],
   win_h="Windows",
   win=["<b>MiKey-…-x64-Setup.exe</b> (oder arm64) von der Release-Seite laden.",
        "Windows SmartScreen warnt eventuell, weil das Installationsprogramm nicht signiert ist: <b>Weitere Informationen</b> › <b>Trotzdem ausführen</b>.",
        "MiKey sitzt im Infobereich. <kbd>Alt</kbd>+<kbd>Z</kbd> schaltet Vietnamesisch ↔ Englisch/Deutsch."],
   linux="Linux (IBus): kommt bald.",
   telex_h="Telex-Tabelle", telex_p="Akzente nach dem Buchstaben, irgendwo im Wort: truowfng, truongwf und truwowngf ergeben alle trường.",
   faq_h="Häufige Fragen",
   faq=[("Ist MiKey gratis?", "Ja. MiKey ist gratis und Open Source (GPL-3.0). Der Quellcode liegt auf GitHub."),
        ("Schickt MiKey, was ich tippe, irgendwohin?", "Nein. Alles passiert auf deinem Gerät. Keine Werbung, keine Statistik, kein Konto."),
        ("Braucht MiKey auf dem Mac die Bedienungshilfen-Berechtigung?", "Nein. MiKey ist eine macOS-Eingabequelle, wie ABC oder Schweiz, deutsch."),
        ("Und wenn ein Wort falsch erkannt wird?", "Direkt danach die Rücktaste drücken: das Getippte kommt zurück. Wer die Deutsch-Erkennung nicht braucht, schaltet sie im Eingabemenü ab."),
        ("Geht das mit einer Schweizer oder deutschen Tastatur (QWERTZ)?", "Ja, genau dafür ist MiKey gemacht. Es liest die Zeichen des aktiven Layouts, also stimmen z/y und ä ö ü."),
        ("Was ist der Unterschied zu Vikey und OpenKey?", "MiKey basiert auf Vikey (Tony Dinh), das auf OpenKey (Tuyen Mai) basiert. MiKey ergänzt, was Vietnamesinnen und Vietnamesen im deutschsprachigen Raum brauchen: Umlaut-Tasten, deutsche Wörter, Tech-Wörter.")],
   credits="MiKey basiert auf <a href=\"https://github.com/trungdq88/Vikey\">Vikey</a> von Tony Dinh und <a href=\"https://github.com/tuyenvm/OpenKey\">OpenKey</a> von Tuyen Mai. Worthäufigkeiten: FrequencyWords (Hermit Dave, OpenSubtitles 2018, CC BY-SA 4.0).",
   license="Lizenz GPL-3.0 · <a href=\"" + REPO + "\">Quellcode auf GitHub</a> · <a href=\"" + REPO + "/issues\">Fehler melden</a>",
   by="Gemacht von <a href=\"https://mikephung.com\">Mike Phung</a>."),
 "en": dict(path="en/", lang="en", name="English",
   title="MiKey: Vietnamese typing for people who also write German and English",
   desc="A Telex input method for macOS and Windows that recognises English and German on its own: text never becomes tẽt, wir never ửi, ü never ơ. Free and open source.",
   skip="Skip to content",
   h1="Type Vietnamese, German and English. Without switching keyboards.",
   lead="MiKey is a Vietnamese Telex input method for people living in Switzerland, Germany and Austria. It notices English and German words by itself, and the ä ö ü keys just work.",
   dl_mac="Download for macOS", dl_win="Download for Windows", meta="macOS 13 or later · Windows 10/11 · Free · Open source (GPL-3.0)",
   demo_label="Example: keys, plain Telex and MiKey", d_keys="Keys", d_bad="Plain Telex", d_good="MiKey",
   why_h="No more silly Telex mistakes", why_p="Telex turns the letters s f r x j w into tone marks. Great for Vietnamese, bad for every other word. MiKey knows about 70,000 English and German words and leaves them alone.",
   t_keys="You type", t_bad="Plain Telex", t_good="MiKey",
   f=[("ä ö ü just work", "On Swiss and German keyboards ü sits where Telex expects the [ key, so it became ơ. MiKey leaves ä ö ü ß é alone: über, Grüße, Café, Zürich."),
      ("Knows German", "wir, der, nur, dass, wissen don't turn into ửi, dẻ, nủ, das, ưisen. Can be turned off in the menu."),
      ("Knows English and tech words", "text, server, the best test, osx, macos, exe stay as typed. Common Vietnamese words like gì and ít always stay Vietnamese."),
      ("Switch with ⌥Z / Alt+Z", "One key for Vietnamese ↔ English/German, with a small VI/EN label at the cursor."),
      ("Wrong guess? Backspace", "If MiKey gets a word wrong, Backspace right after it brings back what you typed."),
      ("Everything stays on your computer", "Nothing is sent anywhere. On the Mac, MiKey is a real input source and needs no Accessibility permission.")],
   inst_h="Install", mac_h="macOS",
   mac=["Download <b>MiKey-…-macOS.pkg</b> from the releases page and open it.",
        "The first time, macOS asks because the package isn't signed by Apple yet: right-click the file › <b>Open</b>, or System Settings › Privacy &amp; Security › <b>Open Anyway</b>.",
        "System Settings › Keyboard › Input Sources › <b>Edit…</b> › <b>+</b> › Vietnamese › <b>MiKey</b>.",
        "Pick <b>MiKey</b> in the input menu in the menu bar. Done."],
   win_h="Windows",
   win=["Download <b>MiKey-…-x64-Setup.exe</b> (or arm64) from the releases page.",
        "Windows SmartScreen may warn because the installer isn't signed yet: <b>More info</b> › <b>Run anyway</b>.",
        "MiKey lives in the system tray. <kbd>Alt</kbd>+<kbd>Z</kbd> switches Vietnamese ↔ English/German."],
   linux="Linux (IBus): coming soon.",
   telex_h="Telex table", telex_p="Type the mark after the letter, anywhere in the word: truowfng, truongwf and truwowngf all give trường.",
   faq_h="FAQ",
   faq=[("Is MiKey free?", "Yes. MiKey is free and open source (GPL-3.0). The code is on GitHub."),
        ("Does MiKey send what I type anywhere?", "No. Everything happens on your computer. No ads, no analytics, no account."),
        ("Does it need the Accessibility permission on the Mac?", "No. MiKey is a macOS input source, like ABC or Swiss German."),
        ("What if a word is guessed wrong?", "Press Backspace right after it to get back exactly what you typed. If you don't need German detection, turn off \"Nhận biết tiếng Đức\" in the input menu."),
        ("Does it work with a Swiss or German (QWERTZ) keyboard?", "Yes, that's what it's made for. It reads the characters of the layout you use, so z/y and ä ö ü are right."),
        ("How is it different from Vikey and OpenKey?", "MiKey is based on Vikey (Tony Dinh), which is based on OpenKey (Tuyen Mai). MiKey adds what Vietnamese people in German-speaking countries need: umlaut keys, German words, tech words.")],
   credits="MiKey is based on <a href=\"https://github.com/trungdq88/Vikey\">Vikey</a> by Tony Dinh and <a href=\"https://github.com/tuyenvm/OpenKey\">OpenKey</a> by Tuyen Mai. Word frequencies: FrequencyWords (Hermit Dave, OpenSubtitles 2018, CC BY-SA 4.0).",
   license="GPL-3.0 license · <a href=\"" + REPO + "\">Source on GitHub</a> · <a href=\"" + REPO + "/issues\">Report a problem</a>",
   by="Made by <a href=\"https://mikephung.com\">Mike Phung</a>."),
}

e = html.escape

def page(code):
    t = T[code]
    up = "../" if t["path"] else ""
    langs = "".join(f'<a href="{up}{T[c]["path"] or "./"}" hreflang="{T[c]["lang"]}" lang="{T[c]["lang"]}"'
                    + (' aria-current="true"' if c == code else "") + f'>{c.upper()}<span class="sr"> {T[c]["name"]}</span></a>'
                    for c in ("vi", "de", "en"))
    alternates = "".join(f'<link rel="alternate" hreflang="{T[c]["lang"]}" href="{SITE}/{T[c]["path"]}">' for c in T) + \
                 f'<link rel="alternate" hreflang="x-default" href="{SITE}/">'
    demo = (f'<table class="demo-t"><caption class="sr">{e(t["demo_label"])}</caption><thead><tr><th scope="col">{e(t["d_keys"])}</th>'
            f'<th scope="col">{e(t["d_bad"])}</th><th scope="col">{e(t["d_good"])}</th></tr></thead><tbody>'
            + "".join(f'<tr><td class="keys">{e(k)}</td><td class="out bad">{e(b)}</td><td class="out good">{e(g)}</td></tr>' for k, b, g in DEMO)
            + "</tbody></table>")
    fixes = "".join(f"<tr><td class=\"mono\">{e(k)}</td><td>{e(b)}</td><td>{e(g)}</td></tr>" for k, b, g in FIXES)
    feats = "".join(f'<div class="card"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in t["f"])
    telex = "".join(f"<tr><td><kbd>{e(k)}</kbd></td><td>{e(v)}</td></tr>" for k, v in TELEX)
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in t["faq"])
    mac = "".join(f"<li>{s}</li>" for s in t["mac"])
    win = "".join(f"<li>{s}</li>" for s in t["win"])
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['desc'])}">
<link rel="canonical" href="{SITE}/{t['path']}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(t['title'])}">
<meta property="og:description" content="{e(t['desc'])}">
<meta property="og:url" content="{SITE}/{t['path']}">
<meta property="og:image" content="{SITE}/assets/icon-512.png">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#4F46E5">
<link rel="icon" type="image/png" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/icon-256.png">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>
<div class="wrap">
<header class="top">
  <a class="brand" href="{up or './'}"><img src="{up}assets/icon-256.png" alt="" width="32" height="32"><span>Mi<span class="key">Key</span></span></a>
  <nav class="lang" aria-label="Language">{langs}</nav>
</header>
<main id="main">
<div class="hero">
  <div>
    <h1>{e(t['h1'])}</h1>
    <p class="lead">{e(t['lead'])}</p>
    <div class="cta"><a class="btn" href="{DL}">{e(t['dl_mac'])}</a><a class="btn alt" href="{DL}">{e(t['dl_win'])}</a></div>
    <p class="meta">{e(t['meta'])}</p>
  </div>
  <div class="demo">{demo}</div>
</div>
<section aria-labelledby="why"><h2 id="why">{e(t['why_h'])}</h2><p class="lead">{e(t['why_p'])}</p>
  <table class="fix"><thead><tr><th scope="col">{e(t['t_keys'])}</th><th scope="col">{e(t['t_bad'])}</th><th scope="col">{e(t['t_good'])}</th></tr></thead><tbody>{fixes}</tbody></table>
</section>
<section aria-label="Features"><div class="grid three">{feats}</div></section>
<section aria-labelledby="install"><h2 id="install">{e(t['inst_h'])}</h2>
  <div class="grid two">
    <div class="card"><h3>{e(t['mac_h'])}</h3><ol class="steps">{mac}</ol></div>
    <div class="card"><h3>{e(t['win_h'])}</h3><ol class="steps">{win}</ol></div>
  </div>
  <p class="note">{e(t['linux'])}</p>
  <div class="cta"><a class="btn" href="{DL}">{e(t['dl_mac'])}</a><a class="btn alt" href="{DL}">{e(t['dl_win'])}</a></div>
</section>
<section aria-labelledby="telex"><h2 id="telex">{e(t['telex_h'])}</h2><p>{e(t['telex_p'])}</p>
  <table><tbody>{telex}</tbody></table>
</section>
<section aria-labelledby="faq"><h2 id="faq">{e(t['faq_h'])}</h2>{faq}</section>
</main>
<footer>
  <p>{t['credits']}</p>
  <p>{t['license']}</p>
  <p>{t['by']}</p>
</footer>
</div>
</body>
</html>
"""

for code, t in T.items():
    path = os.path.join(HERE, t["path"], "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(page(code))
    print("wrote", os.path.relpath(path, HERE))
open(os.path.join(HERE, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE}/{t['path']}</loc></url>\n" for t in T.values()) + "</urlset>\n")
open(os.path.join(HERE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
open(os.path.join(HERE, "CNAME"), "w").write("mikey.mikephung.com\n")
