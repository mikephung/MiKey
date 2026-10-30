#!/usr/bin/env python3
"""Builds mikey.mikephung.com (see PLAN.md): home, download, guide, changelog, privacy, acknowledgements and 404,
in Vietnamese (/), German (/de/) and English (/en/), from one layout. The output is committed, so Cloudflare
Pages needs no build step.  usage: python3 site-mikey/build.py"""
import hashlib, html, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SITE = "https://mikey.mikephung.com"
REPO = "https://github.com/mikephung/MiKey"
VERSION = "1.0.1"
RELEASE_DATE = "2026-10-30"
REL = f"{REPO}/releases/download/v{VERSION}"
e = html.escape
LANGS = ("vi", "de", "en")
PREFIX = {"vi": "", "de": "de/", "en": "en/"}
NAME = {"vi": "Tiếng Việt", "de": "Deutsch", "en": "English"}

# ---- release files: size and SHA-256 from dist/<VERSION>/ when it is there ------------------------------------
FILES = [  # key, file name, platform, note key
    ("mac_dmg", f"MiKey-{VERSION}-macOS.dmg", "mac", "f_mac_dmg"),
    ("mac_pkg", f"MiKey-{VERSION}-macOS.pkg", "mac", "f_mac_pkg"),
    ("mac_zip", f"MiKey-{VERSION}-macOS.zip", "mac", "f_mac_zip"),
    ("win_x64", f"MiKey-{VERSION}-x64-Setup.exe", "win", "f_win_x64"),
    ("win_arm", f"MiKey-{VERSION}-arm64-Setup.exe", "win", "f_win_arm"),
    ("win_x64_zip", f"MiKey-{VERSION}-x64-portable.zip", "win", "f_win_zip"),
    ("win_arm_zip", f"MiKey-{VERSION}-arm64-portable.zip", "win", "f_win_zip_arm"),
]
DIST = os.path.join(ROOT, "dist", VERSION)
def file_info(name):
    p = os.path.join(DIST, name)
    if not os.path.exists(p): return None
    data = open(p, "rb").read()
    return {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
INFO = {k: file_info(n) for k, n, _, _ in FILES}
# Windows installers come from GitHub Actions; until they are in dist/ the page says they are on the way
WIN_READY = INFO["win_x64"] is not None
def mb(n): return f"{n / 1048576:.1f} MB"

# ---- real engine output (VIKEY_AUTO_OFF=1 Tools/autoswitch/test/harness); über/Café: Swiss keyboard before MiKey ---
DEMO = [("text", "tẽt", "text"), ("wir", "ửi", "wir"), ("der", "dẻ", "der"), ("über", "ơber", "über"), ("osx", "õ", "osx")]
FIXES = [("text", "tẽt", "text"), ("server", "sẻver", "server"), ("wir", "ửi", "wir"), ("der", "dẻ", "der"), ("nur", "nủ", "nur"),
         ("dass", "das", "dass"), ("wissen", "ưisen", "wissen"), ("über", "ơber", "über"), ("Café", "Càé", "Café"), ("osx", "õ", "osx")]
TELEX_MARKS = [("aa", "â"), ("aw", "ă"), ("ee", "ê"), ("oo", "ô"), ("ow", "ơ"), ("uw", "ư"), ("w", "ư"), ("dd", "đ")]
TELEX_TONES = [("s", "á", "sắc"), ("f", "à", "huyền"), ("r", "ả", "hỏi"), ("x", "ã", "ngã"), ("j", "ạ", "nặng"), ("z", "a", "×")]
TELEX_EXAMPLES = [("tooi ddi hocj", "tôi đi học"), ("truwowngf / truowfng", "trường"), ("Vieetj Nam", "Việt Nam"),
                  ("khoer khoong", "khoẻ không"), ("caamf", "cầm"), ("nguyeenx", "nguyễn")]

RELEASES = [  # newest first
    ("1.0.1", "2026-10-30", {
        "vi": ["Sửa lỗi cài đặt trên máy mới.",
               "macOS: sau khi cài, MiKey tự xuất hiện trong menu bàn phím (trước đây trên máy mới chỉ hiện như một ứng dụng, phải đăng xuất mới thấy).",
               "Bộ cài luôn cài vào /Library/Input Methods và dọn bản MiKey cũ trong thư mục người dùng.",
               "Logo và liên kết trong ứng dụng thanh menu: MiKey thay cho Vikey."],
        "de": ["Behebt die Installation auf einem neuen Mac.",
               "macOS: Nach der Installation erscheint MiKey sofort im Eingabemenü (auf einem neuen Mac war es zuvor nur als App sichtbar, erst nach dem Abmelden als Eingabequelle).",
               "Das Installationsprogramm installiert immer nach /Library/Input Methods und räumt eine ältere MiKey-Kopie im Benutzerordner weg.",
               "Logo und Links in der Menüleisten-App: MiKey statt Vikey."],
        "en": ["Fixes installing on a new Mac.",
               "macOS: after installing, MiKey shows up in the input menu right away (on a new Mac it used to appear only as an app, and as an input source only after logging out).",
               "The installer always installs into /Library/Input Methods and removes an older MiKey copy in the user folder.",
               "Logo and links in the menu bar app: MiKey instead of Vikey."]}),
    (VERSION, RELEASE_DATE, {
        "vi": ["Bản đầu tiên của MiKey.",
               "macOS: MiKey là một input source thật trong menu bàn phím (InputMethodKit), không cần quyền Accessibility.",
               "Phím ä ö ü ß é và các dead key (´ ^ ¨) trên bàn phím Đức/Thụy Sĩ gõ thẳng, không còn bị Telex biến thành ơ, ư.",
               "Nhận biết khoảng 30.000 từ tiếng Đức (wir, der, dass…) cùng với tiếng Anh.",
               "Từ công nghệ như osx, macos, exe không còn bị bỏ dấu.",
               "Sửa lỗi từ mới bị dính vào từ trước sau khi xoá hay click (đawng, tootho).",
               "Windows: cùng các sửa lỗi bàn phím Đức/Thụy Sĩ, bộ cài MiKey riêng, tự cập nhật có chữ ký."],
        "de": ["Erste Version von MiKey.",
               "macOS: MiKey ist eine echte Eingabequelle im Eingabemenü (InputMethodKit), ohne Bedienungshilfen-Berechtigung.",
               "ä ö ü ß é und die Tottasten (´ ^ ¨) auf deutschen und Schweizer Tastaturen werden nicht mehr von Telex zu ơ oder ư gemacht.",
               "Erkennt rund 30'000 deutsche Wörter (wir, der, dass…), zusätzlich zu Englisch.",
               "Tech-Wörter wie osx, macos, exe bekommen keine Akzente mehr.",
               "Behoben: Nach Löschen oder Klicken klebte das neue Wort am vorherigen (đawng, tootho).",
               "Windows: dieselben Korrekturen für deutsche/Schweizer Tastaturen, eigenes Installationsprogramm, signierte Updates."],
        "en": ["First MiKey release.",
               "macOS: MiKey is a real input source in the input menu (InputMethodKit), no Accessibility permission needed.",
               "ä ö ü ß é and the dead keys (´ ^ ¨) on German and Swiss keyboards are no longer turned into ơ or ư by Telex.",
               "Recognises about 30,000 German words (wir, der, dass…) as well as English.",
               "Tech words such as osx, macos, exe no longer get tone marks.",
               "Fixed: after deleting or clicking, the next word was glued to the previous one (đawng, tootho).",
               "Windows: the same German/Swiss keyboard fixes, its own installer, signed updates."]}),
]

CREDITS_CODE = [("Vikey", "Tony Dinh", "GPL-3.0", "https://github.com/trungdq88/Vikey"),
                ("OpenKey", "Tuyen Mai", "GPL-3.0", "https://github.com/tuyenvm/OpenKey"),
                ("TweetNaCl (Windows updates)", "Daniel J. Bernstein et al.", "public domain", "https://tweetnacl.cr.yp.to"),
                ("Inno Setup (Windows installer)", "Jordan Russell, Martijn Laan", "Inno Setup License", "https://jrsoftware.org/isinfo.php")]
CREDITS_WORDS = [("FrequencyWords (OpenSubtitles 2018): English, Vietnamese, German", "Hermit Dave", "CC BY-SA 4.0", "https://github.com/hermitdave/FrequencyWords"),
                 ("FineWeb-2 and FineWeb", "Hugging Face", "ODC-By 1.0", "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2"),
                 ("HPLT v2", "High Performance Language Technologies", "CC0", "https://hplt-project.org"),
                 ("MADLAD-400", "Google", "ODC-By 1.0", "https://huggingface.co/datasets/allenai/MADLAD-400"),
                 ("Reddit comments", "tensorshield/reddit_dataset_157", "MIT", "https://huggingface.co/datasets/tensorshield/reddit_dataset_157"),
                 ("Vietnamese forums and reader comments", "VnExpress, Tuổi Trẻ, Tinhte, Otofun, Dạy Nhau Học", None, None),
                 ("Emoji names and keywords (CLDR)", "Unicode, Inc.", "Unicode License v3", "https://cldr.unicode.org"),
                 ("Emojibase", "Miles Johnson", "MIT", "https://emojibase.dev")]
CREDITS_TEST = [("ViLexNorm", "Nguyen et al., EACL 2024", "CC BY-NC-SA 4.0", "https://github.com/ngxtnhi/ViLexNorm"),
                ("UIT-ViCTSD", "UIT NLP Group", "research use", "https://huggingface.co/datasets/tarudesu/ViCTSD"),
                ("VietMix", "EACL 2026", "research use", "https://huggingface.co/datasets/razent/vietmix"),
                ("GitHub Typo Corpus", "Hagiwara & Mita, LREC 2020", "research use", "https://github.com/mhagiwara/github-typo-corpus"),
                ("Birkbeck spelling error corpus", "Roger Mitton", "free to use", "https://www.dcs.bbk.ac.uk/~roger/corpora.html"),
                ("Lists of common misspellings", "Wikipedia", "CC BY-SA 4.0", "https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings")]

# ---- copy -------------------------------------------------------------------------------------------------------
S = {
"vi": dict(
  skip="Bỏ qua, đến nội dung", nav=[("download/", "Tải về"), ("guide/", "Hướng dẫn"), ("#faq", "Câu hỏi"), ("changelog/", "Thay đổi")],
  dl_mac="Tải cho macOS", dl_win="Tải cho Windows", dl_win_soon="Windows: sắp có", dl_all="Tất cả bản tải", version=f"Phiên bản {VERSION}",
  meta="macOS 13 trở lên · Windows 10/11 · Miễn phí · Mã nguồn mở",
  foot_credits='MiKey dựa trên <a href="https://github.com/trungdq88/Vikey">Vikey</a> của Tony Dinh và <a href="https://github.com/tuyenvm/OpenKey">OpenKey</a> của Tuyen Mai.',
  foot_links=[("acknowledgements/", "Ghi công"), ("privacy/", "Quyền riêng tư"), (REPO, "Mã nguồn"), (REPO + "/issues", "Báo lỗi")],
  foot_license="Giấy phép GPL-3.0. Làm bởi <a href=\"https://mikephung.com\">Mike Phung</a>.",
  # home
  home_title="MiKey: bộ gõ tiếng Việt cho người Việt ở Thụy Sĩ, Đức và Áo",
  home_desc="Bộ gõ Telex cho macOS và Windows, tự nhận ra tiếng Anh và tiếng Đức: text không thành tẽt, wir không thành ửi, ü không thành ơ. Miễn phí, mã nguồn mở, không gửi dữ liệu.",
  h1="Gõ tiếng Việt, tiếng Đức và tiếng Anh. Không cần đổi bàn phím.",
  lead="MiKey là bộ gõ Telex cho người Việt sống ở Thụy Sĩ, Đức, Áo. Nó tự nhận ra khi bạn gõ tiếng Anh hay tiếng Đức, và các phím ä ö ü cứ thế mà dùng.",
  d_keys="Phím gõ", d_bad="Telex thường", d_good="MiKey", demo_cap="Cùng một chuỗi phím: Telex thường và MiKey",
  prob_h="Quen không?", prob_p="Bạn nhắn tin cho bạn bè bằng tiếng Việt, rồi gửi email cho đồng nghiệp bằng tiếng Đức, rồi gõ một lệnh trong Terminal. Telex không biết bạn đang viết gì: chữ s f r x j w lúc nào cũng có thể là dấu. Vậy là \"text\" thành \"tẽt\", \"wir\" thành \"ửi\". Trên bàn phím Thụy Sĩ còn tệ hơn: phím ü nằm đúng chỗ phím [ mà Telex dùng để gõ ơ.",
  t_keys="Bạn gõ", t_bad="Telex thường ra", t_good="MiKey ra", fix_cap="Một số lỗi Telex thường gặp và kết quả với MiKey",
  feat_h="MiKey làm gì khác",
  feats=[("Phím ä ö ü cứ thế dùng", "Gặp ä ö ü ß é hay một dead key, MiKey để nguyên cả từ: über, Grüße, Café, Zürich."),
         ("Hiểu tiếng Đức", "Khoảng 30.000 từ tiếng Đức: wir, der, nur, dass, wissen giữ nguyên. Tắt được nếu không cần."),
         ("Hiểu tiếng Anh", "Khoảng 40.000 từ tiếng Anh và từ công nghệ: text, server, deploy, osx, macos giữ nguyên."),
         ("Tiếng Việt vẫn là tiếng Việt", "Từ tiếng Việt thường gặp không bao giờ bị đổi: gì, ít, có, tô. Câu tiếng Việt gõ bình thường."),
         ("Một phím để chuyển", "⌥Z trên Mac, Alt+Z trên Windows: Việt ↔ Anh/Đức, có nhãn VI/EN hiện ở con trỏ."),
         ("Đoán sai thì Backspace", "Bấm Backspace ngay sau một từ MiKey vừa sửa là lấy lại đúng phím bạn gõ.")],
  how_h="Cách MiKey quyết định",
  how=[("Bạn gõ một từ", "Telex chạy như bình thường trong lúc bạn gõ."),
       ("Bạn kết thúc từ", "Khi bạn bấm cách, dấu câu hay Enter, MiKey xem từ vừa gõ: là âm tiết tiếng Việt, hay là một từ tiếng Anh, tiếng Đức có thật?"),
       ("MiKey giữ đúng chữ", "Nếu là tiếng Anh hay tiếng Đức, từ trở lại đúng các phím bạn gõ và MiKey chuyển sang chế độ Anh/Đức. Gặp một từ rõ ràng là tiếng Việt, nó tự chuyển về.")],
  inst_h="Cài trong 3 bước",
  inst=["Tải MiKey cho máy của bạn.", "Mở bộ cài. Lần đầu, macOS hoặc Windows sẽ hỏi lại vì bản cài chưa được ký: xem hướng dẫn chi tiết.", "Chọn MiKey trong menu bàn phím (Mac) hoặc thấy nó ở khay hệ thống (Windows). Gõ thôi."],
  inst_more="Hướng dẫn cài chi tiết",
  priv_h="Những gì bạn gõ ở lại trên máy bạn",
  priv_p="MiKey không gửi gì lên mạng, không có tài khoản, không quảng cáo, không đo đếm. Trên Mac nó là một input source như bàn phím ABC, nên không cần quyền Accessibility. Mã nguồn mở, ai cũng kiểm tra được.",
  priv_more="Chính sách quyền riêng tư",
  faq_h="Câu hỏi thường gặp",
  faq=[("MiKey có miễn phí không?", "Có. MiKey miễn phí, mã nguồn mở theo giấy phép GPL-3.0."),
       ("Có cần quyền Accessibility trên Mac không?", "Không. MiKey là một input source của macOS, giống \"ABC\" hay \"Schweiz, deutsch\"."),
       ("Vì sao macOS/Windows cảnh báo khi cài?", "Vì bản cài chưa được ký bằng chứng chỉ của Apple hay Microsoft (tốn phí hằng năm). Mã nguồn công khai trên GitHub, và trang Tải về có mã SHA-256 để bạn kiểm tra file."),
       ("Tôi dùng bàn phím Thụy Sĩ hoặc Đức (QWERTZ) được không?", "Được, MiKey được làm cho chính các bàn phím đó. Nó đọc chữ in trên phím của layout bạn đang dùng, nên z/y và ä ö ü đều đúng."),
       ("Một từ bị đoán sai thì làm sao?", "Bấm Backspace ngay sau đó để lấy lại đúng chữ đã gõ. Nếu một từ tiếng Việt hay bị đổi sang tiếng Đức, tắt \"Nhận biết tiếng Đức\" trong menu bàn phím và báo cho mình trên GitHub."),
       ("Có bản cho Linux, iPhone, Android không?", "Chưa. Linux (IBus) đang được làm. Vikey, bản gốc của MiKey, đã có cho iPhone và Android."),
       ("MiKey khác Vikey thế nào?", "MiKey là bản fork của Vikey (Tony Dinh), thêm những gì người Việt ở vùng nói tiếng Đức cần: phím umlaut, từ tiếng Đức, từ công nghệ, và một input source thật trên Mac.")],
  final_h="Thử MiKey ngay", final_p="Miễn phí, cài trong một phút, gỡ cũng nhanh như vậy.",
  # download
  dl_title="Tải MiKey cho macOS và Windows", dl_desc=f"Tải MiKey {VERSION} cho macOS (Apple Silicon và Intel) và Windows (x64, ARM64), kèm hướng dẫn cài, cập nhật và gỡ.",
  dl_h1="Tải MiKey", dl_lead=f"Phiên bản {VERSION}, phát hành {RELEASE_DATE}. Miễn phí, không cần tài khoản.",
  f_head=("File", "Dành cho", "Dung lượng", "SHA-256"), f_cap="Các file của phiên bản này",
  f_mac_dmg="macOS 13+, Apple Silicon (M1–M4) và Intel. Nên dùng.", f_mac_pkg="Chỉ bộ cài, giống trong file .dmg.", f_mac_zip="macOS, bản .app để tự chép vào Input Methods.",
  f_win_x64="Windows 10/11, hầu hết máy tính. Nên dùng.", f_win_arm="Windows 11 trên ARM (Snapdragon, Surface Pro X).",
  f_win_zip="Windows x64, không cần cài.", f_win_zip_arm="Windows ARM64, không cần cài.",
  win_soon="Bộ cài Windows đang được hoàn thiện và sẽ có trên trang phát hành trong vài ngày tới.",
  req_h="Yêu cầu", req=["macOS 13 Ventura trở lên, Mac Apple Silicon hoặc Intel.", "Windows 10 hoặc 11, x64 hoặc ARM64.", "Bất kỳ layout bàn phím nào: Schweiz, deutsch · Deutsch · ABC/US · Österreich."],
  mac_h="Cài trên macOS",
  mac=["Tải <b>" + f"MiKey-{VERSION}-macOS.dmg" + "</b>, mở nó, rồi bấm đúp <b>Cài đặt MiKey.pkg</b>. Cùng một file cho Mac Apple Silicon (M1–M4) và Mac Intel.",
       "macOS báo <i>không thể mở vì Apple không thể kiểm tra phần mềm độc hại</i>: bấm <b>Xong</b>. Đây là vì bản cài chưa được ký bằng chứng chỉ Apple.",
       "Mở <b>System Settings › Privacy &amp; Security</b>, kéo xuống, bấm <b>Open Anyway</b> cạnh dòng MiKey, rồi nhập mật khẩu máy.",
       "Bộ cài chép MiKey vào <code>/Library/Input Methods</code>. Bấm Continue, Install.",
       "Mở <b>System Settings › Keyboard › Input Sources › Edit…</b>, bấm <b>+</b>, chọn <b>Vietnamese</b> › <b>MiKey</b> › Add. Nếu chưa thấy MiKey, đăng xuất rồi đăng nhập lại.",
       "Chọn <b>MiKey</b> trong menu bàn phím ở thanh menu (cạnh đồng hồ). Bàn phím bên dưới vẫn là layout bạn đã chọn, ví dụ Schweiz, deutsch."],
  mac_upd="Cập nhật: tải bản mới và cài đè lên. Gỡ: bỏ MiKey khỏi Input Sources, rồi xoá <code>/Library/Input Methods/MiKey.app</code> (Finder › Go › Go to Folder).",
  win_h="Cài trên Windows",
  win=["Tải <b>" + f"MiKey-{VERSION}-x64-Setup.exe" + "</b> (hoặc bản arm64 cho máy ARM).",
       "Windows SmartScreen báo <i>Windows protected your PC</i>: bấm <b>More info</b> › <b>Run anyway</b>. Lý do giống trên Mac: bản cài chưa được ký.",
       "MiKey được cài cho riêng tài khoản của bạn, không cần quyền quản trị.",
       "MiKey nằm ở khay hệ thống (góc dưới bên phải). <kbd>Alt</kbd>+<kbd>Z</kbd> để chuyển Việt ↔ Anh/Đức."],
  win_upd="Cập nhật: MiKey tự kiểm tra bản mới mỗi ngày và chỉ cài bản có chữ ký của MiKey. Gỡ: Settings › Apps › MiKey › Uninstall.",
  verify_h="Kiểm tra file", verify_p="Mã SHA-256 ở bảng trên phải khớp với file bạn tải về. Trên Mac: <code>shasum -a 256 MiKey-*.pkg</code>. Trên Windows (PowerShell): <code>Get-FileHash MiKey-*.exe</code>.",
  older="Các bản cũ và mã nguồn: trang phát hành trên GitHub.",
  # guide
  g_title="Hướng dẫn sử dụng MiKey", g_desc="Bảng Telex, cách MiKey nhận ra tiếng Anh và tiếng Đức, chuyển ngôn ngữ, sửa sai bằng Backspace, mẹo và giới hạn.",
  g_h1="Hướng dẫn sử dụng", g_lead="Mọi thứ cần biết để gõ nhanh với MiKey, và những trường hợp đặc biệt.",
  g_toc="Mục lục",
  g_telex_h="Bảng Telex", g_marks="Dấu mũ, móc, trăng và đ", g_tones="Dấu thanh", g_ex="Ví dụ",
  g_telex_p="Gõ dấu sau chữ cái, ở đâu trong từ cũng được: <code>truowfng</code>, <code>truongwf</code> và <code>truwowngf</code> đều ra <b>trường</b>. Bấm phím dấu hai lần để bỏ dấu và giữ chữ cái: <code>vaff</code> ra <b>vaf</b>.",
  g_place_h="Kiểu bỏ dấu", g_place_p="Mặc định MiKey bỏ dấu kiểu mới: <b>hoà, thuý, khoẻ</b>. Muốn kiểu cũ (<b>hòa, thúy, khỏe</b>) thì tắt \"Bỏ dấu kiểu mới\" trong menu bàn phím trên Mac.",
  g_switch_h="Chuyển ngôn ngữ", g_switch=["<kbd>⌥</kbd>+<kbd>Z</kbd> trên Mac, <kbd>Alt</kbd>+<kbd>Z</kbd> trên Windows: Tiếng Việt ↔ English/Deutsch. Trên Mac, một nhãn nhỏ <b>VI</b> hoặc <b>EN</b> hiện ở con trỏ.",
       "Trên Mac cũng chọn được trong menu bàn phím: <b>Tiếng Việt (Telex)</b> hoặc <b>English / Deutsch</b>.",
       "Sau khi bạn tự chuyển, MiKey tạm không tự chuyển trong 5 giây, để không đổi lại ngay điều bạn vừa chọn."],
  g_auto_h="MiKey nhận ra tiếng Anh và tiếng Đức thế nào",
  g_auto=["MiKey chỉ quyết định khi một từ kết thúc: bấm cách, dấu câu (, . ; : ? ! ) \") hoặc Enter.",
          "Ở chế độ tiếng Việt: nếu các phím bạn gõ là một từ tiếng Anh hay tiếng Đức có thật, và cách đọc tiếng Việt hiếm hoặc không có, từ trở lại đúng các phím và MiKey chuyển sang Anh/Đức. <code>text</code> → <b>text</b>, <code>wir</code> → <b>wir</b>.",
          "Ở chế độ Anh/Đức: nếu bạn gõ một từ rõ ràng là tiếng Việt, MiKey đổi nó và chuyển về tiếng Việt. <code>treen</code> → <b>trên</b>, <code>ddi hocj</code> → <b>đi học</b>.",
          "Khi một từ có hai cách đọc (car / cả, too / tô), MiKey xem từ đứng trước nó và dùng cách đọc phổ biến hơn trong văn bản thật.",
          "Từ tiếng Việt thường gặp không bao giờ bị đổi sang tiếng Anh hay tiếng Đức."],
  g_umlaut_h="Phím ä ö ü và dead key", g_umlaut_p="Khi bạn gõ ä ö ü ß é è à ç hoặc một dead key (´ ` ^ ¨), MiKey trả từ đang gõ về đúng các phím rồi tắt Telex đến hết từ đó. Vì vậy <b>über</b>, <b>fährt</b>, <b>Grüße</b>, <b>Café</b>, <b>Zürich</b> luôn đúng, kể cả giữa một câu tiếng Việt: <i>đi học ở Zürich</i>.",
  g_de_h="Nhận biết tiếng Đức", g_de_p="Bật sẵn. MiKey biết khoảng 30.000 từ tiếng Đức, kể cả cách viết không umlaut (fuer, schoen) và kiểu Thụy Sĩ với ss (Strasse). Trên Mac, tắt trong menu bàn phím: <b>Nhận biết tiếng Đức</b>.",
  g_undo_h="Sửa sai bằng Backspace", g_undo_p="Ngay sau khi MiKey tự đổi một từ, bấm <kbd>Backspace</kbd> một lần: từ trở lại đúng như bạn gõ và ngôn ngữ trở lại như trước. Gõ tiếp vào từ đó thì MiKey xem lại cả từ.",
  g_tips_h="Mẹo",
  g_tips=["<b>Viết tắt, tên viết hoa</b>: từ có từ hai chữ hoa trở lên được giữ nguyên (NAS, HDD, USA, GoPro). Gõ cả câu bằng Caps Lock vẫn ra tiếng Việt: <code>TOOI DDI HOCJ</code> → <b>TÔI ĐI HỌC</b>.",
          "<b>Code, file, đường dẫn</b>: từ đứng sau . _ - / được giữ nguyên: <code>file.txt</code>, <code>my_var</code>, <code>git push</code>.",
          "<b>Số</b>: <code>5trawm</code> → <b>5trăm</b>, <code>100k</code> và <code>md5sum</code> giữ nguyên.",
          "<b>Từ có hai cách đọc</b>: gõ chữ hoa để giữ nguyên (GIF, HDD), hoặc tự chuyển bằng ⌥Z/Alt+Z trước khi gõ."],
  g_limits_h="Những trường hợp cố ý giữ tiếng Việt",
  g_limits_p="Một vài từ vừa là tiếng Việt thường gặp vừa là tiếng Anh/Đức. MiKey ưu tiên tiếng Việt, vì đổi nhầm một từ tiếng Việt phiền hơn:",
  g_limits=[("gif", "gì"), ("hdd", "hđ (hợp đồng)"), ("rar", "rả (rôm rả)"), ("ist (đầu câu)", "ít")],
  g_limits_after="Sau một từ tiếng Đức, <code>ist</code> vẫn là <b>ist</b>: <i>das ist gut</i>. Thấy từ nào sai thường xuyên? Báo trên GitHub.",
  # changelog
  c_title="Các thay đổi của MiKey", c_desc="Những gì mới trong từng phiên bản MiKey.", c_h1="Các thay đổi", c_lead="Phiên bản mới nhất ở trên cùng.",
  # privacy
  p_title="Quyền riêng tư", p_desc="MiKey không thu thập dữ liệu. Những gì bộ gõ và trang web làm, nói rõ.", p_h1="Quyền riêng tư", p_lead=f"Cập nhật {RELEASE_DATE}. Ngắn gọn: MiKey không thu thập gì cả.",
  p_sections=[("Bộ gõ", ["Mọi xử lý diễn ra trên máy bạn. MiKey không gửi những gì bạn gõ đi đâu cả.",
                          "Trên Mac, input method MiKey không kết nối mạng.",
                          "Trên Windows, MiKey kiểm tra bản cập nhật mỗi ngày một lần bằng cách tải <code>mikey.mikephung.com/appcast.xml</code>. Yêu cầu này giống mọi lần mở trang web (địa chỉ IP, loại trình duyệt) và không chứa gì về bạn hay những gì bạn gõ. Tắt được trong cài đặt.",
                          "Trên Windows có một \"nhật ký gõ\" để gỡ lỗi. Nó tắt sẵn, chỉ lưu trên máy bạn, và không bao giờ ghi trong ô mật khẩu."]),
              ("Trang web này", ["Trang web là các file HTML tĩnh: không cookie, không đo đếm, không quảng cáo, không phông chữ hay script từ bên ngoài.",
                                 "Trang được phục vụ qua Cloudflare. Như mọi máy chủ web, Cloudflare xử lý địa chỉ IP của bạn để gửi trang và chống tấn công.",
                                 "Nút tải dẫn tới GitHub. GitHub có chính sách quyền riêng tư riêng."]),
              ("Liên hệ", ["Câu hỏi về quyền riêng tư: mở một issue trên GitHub hoặc liên hệ qua mikephung.com."])],
  # acknowledgements
  a_title="Ghi công", a_desc="Mã nguồn và dữ liệu MiKey được xây dựng từ đó, cùng giấy phép.", a_h1="Ghi công",
  a_lead="MiKey đứng trên vai những dự án này. Cảm ơn các tác giả.",
  a_code="Mã nguồn", a_words="Dữ liệu đếm từ (chỉ số đếm được đưa vào app, không có văn bản)", a_test="Dữ liệu chỉ dùng để đo độ chính xác (không có trong app)",
  a_head=("Tên", "Tác giả", "Giấy phép"), a_stats="thống kê từ",
  a_gpl=f"MiKey được phát hành theo giấy phép GNU GPL-3.0. Mã nguồn đầy đủ của mọi phiên bản ở <a href=\"{REPO}\">{REPO.replace('https://', '')}</a>.",
  # 404
  nf_h1="Không tìm thấy trang", nf_p="Trang này không có. Về trang chủ:",
),
"de": dict(
  skip="Zum Inhalt springen", nav=[("download/", "Download"), ("guide/", "Anleitung"), ("#faq", "FAQ"), ("changelog/", "Änderungen")],
  dl_mac="Für macOS laden", dl_win="Für Windows laden", dl_win_soon="Windows: bald", dl_all="Alle Downloads", version=f"Version {VERSION}",
  meta="macOS 13 oder neuer · Windows 10/11 · Gratis · Open Source",
  foot_credits='MiKey basiert auf <a href="https://github.com/trungdq88/Vikey">Vikey</a> von Tony Dinh und <a href="https://github.com/tuyenvm/OpenKey">OpenKey</a> von Tuyen Mai.',
  foot_links=[("acknowledgements/", "Danksagung"), ("privacy/", "Datenschutz"), (REPO, "Quellcode"), (REPO + "/issues", "Fehler melden")],
  foot_license="Lizenz GPL-3.0. Gemacht von <a href=\"https://mikephung.com\">Mike Phung</a>.",
  home_title="MiKey: vietnamesisch tippen in der Schweiz, in Deutschland und Österreich",
  home_desc="Telex-Eingabe für macOS und Windows, die Englisch und Deutsch selbst erkennt: aus text wird nicht tẽt, aus wir nicht ửi, aus ü nicht ơ. Gratis, Open Source, ohne Datensammlung.",
  h1="Vietnamesisch, Deutsch und Englisch tippen. Ohne die Tastatur zu wechseln.",
  lead="MiKey ist eine vietnamesische Telex-Eingabe für alle, die in der Schweiz, in Deutschland oder Österreich leben. Sie erkennt englische und deutsche Wörter selbst, und die Tasten ä ö ü funktionieren einfach.",
  d_keys="Tasten", d_bad="Normales Telex", d_good="MiKey", demo_cap="Dieselben Tasten: normales Telex und MiKey",
  prob_h="Kennst du das?", prob_p="Du schreibst Freunden auf Vietnamesisch, dann eine E-Mail auf Deutsch, dann einen Befehl im Terminal. Telex weiss nicht, was du gerade schreibst: s f r x j w können immer Akzente sein. So wird aus \"text\" \"tẽt\" und aus \"wir\" \"ửi\". Auf der Schweizer Tastatur ist es noch schlimmer: ü liegt genau dort, wo Telex mit [ ein ơ macht.",
  t_keys="Getippt", t_bad="Normales Telex", t_good="MiKey", fix_cap="Typische Telex-Fehler und was MiKey daraus macht",
  feat_h="Was MiKey anders macht",
  feats=[("ä ö ü einfach tippen", "Bei ä ö ü ß é oder einer Tottaste lässt MiKey das ganze Wort in Ruhe: über, Grüsse, Café, Zürich."),
         ("Versteht Deutsch", "Rund 30'000 deutsche Wörter: wir, der, nur, dass, wissen bleiben stehen. Abschaltbar."),
         ("Versteht Englisch", "Rund 40'000 englische Wörter und Tech-Begriffe: text, server, deploy, osx, macos bleiben stehen."),
         ("Vietnamesisch bleibt Vietnamesisch", "Häufige vietnamesische Wörter werden nie umgestellt: gì, ít, có, tô."),
         ("Eine Taste zum Umschalten", "⌥Z auf dem Mac, Alt+Z unter Windows: Vietnamesisch ↔ Englisch/Deutsch, mit VI/EN-Hinweis beim Cursor."),
         ("Falsch erkannt? Rücktaste", "Direkt nach einer Korrektur holt die Rücktaste genau das Getippte zurück.")],
  how_h="Wie MiKey entscheidet",
  how=[("Du tippst ein Wort", "Telex arbeitet ganz normal, während du tippst."),
       ("Du beendest das Wort", "Bei Leerzeichen, Satzzeichen oder Enter prüft MiKey das Wort: vietnamesische Silbe oder ein echtes englisches oder deutsches Wort?"),
       ("MiKey behält das Richtige", "Bei Englisch oder Deutsch kommen genau deine Tasten zurück und MiKey wechselt auf Englisch/Deutsch. Kommt ein klar vietnamesisches Wort, wechselt es von selbst zurück.")],
  inst_h="In 3 Schritten installiert",
  inst=["MiKey für dein System laden.", "Das Installationsprogramm öffnen. Beim ersten Mal fragt macOS oder Windows nach, weil es nicht signiert ist: siehe Anleitung.", "MiKey im Eingabemenü wählen (Mac) oder im Infobereich finden (Windows). Fertig."],
  inst_more="Ausführliche Installationsanleitung",
  priv_h="Was du tippst, bleibt auf deinem Gerät",
  priv_p="MiKey schickt nichts ins Internet, hat kein Konto, keine Werbung, keine Statistik. Auf dem Mac ist es eine Eingabequelle wie ABC und braucht keine Bedienungshilfen-Berechtigung. Der Code ist offen und prüfbar.",
  priv_more="Datenschutzerklärung",
  faq_h="Häufige Fragen",
  faq=[("Ist MiKey gratis?", "Ja. MiKey ist gratis und Open Source unter der GPL-3.0."),
       ("Braucht MiKey auf dem Mac die Bedienungshilfen-Berechtigung?", "Nein. MiKey ist eine macOS-Eingabequelle, wie \"ABC\" oder \"Schweiz, deutsch\"."),
       ("Warum warnt macOS/Windows bei der Installation?", "Weil das Installationsprogramm (noch) nicht mit einem kostenpflichtigen Apple- oder Microsoft-Zertifikat signiert ist. Der Quellcode ist auf GitHub, und auf der Download-Seite stehen SHA-256-Prüfsummen."),
       ("Geht das mit einer Schweizer oder deutschen Tastatur (QWERTZ)?", "Ja, genau dafür ist MiKey gemacht. Es liest die Zeichen deines Layouts, also stimmen z/y und ä ö ü."),
       ("Was, wenn ein Wort falsch erkannt wird?", "Direkt danach die Rücktaste: das Getippte kommt zurück. Wird ein vietnamesisches Wort oft als Deutsch erkannt, \"Nhận biết tiếng Đức\" im Eingabemenü abschalten und es auf GitHub melden."),
       ("Gibt es MiKey für Linux, iPhone, Android?", "Noch nicht. Linux (IBus) ist in Arbeit. Vikey, das Original, gibt es für iPhone und Android."),
       ("Was ist der Unterschied zu Vikey?", "MiKey ist ein Fork von Vikey (Tony Dinh) mit dem, was Vietnamesinnen und Vietnamesen im deutschsprachigen Raum brauchen: Umlaut-Tasten, deutsche Wörter, Tech-Wörter und eine echte Mac-Eingabequelle.")],
  final_h="MiKey ausprobieren", final_p="Gratis, in einer Minute installiert und genauso schnell wieder entfernt.",
  dl_title="MiKey für macOS und Windows laden", dl_desc=f"MiKey {VERSION} für macOS (Apple Silicon und Intel) und Windows (x64, ARM64), mit Anleitung zu Installation, Update und Deinstallation.",
  dl_h1="MiKey laden", dl_lead=f"Version {VERSION}, erschienen am {RELEASE_DATE}. Gratis, ohne Konto.",
  f_head=("Datei", "Für", "Grösse", "SHA-256"), f_cap="Die Dateien dieser Version",
  f_mac_dmg="macOS 13+, Apple Silicon (M1–M4) und Intel. Empfohlen.", f_mac_pkg="Nur das Installationsprogramm, wie im .dmg.", f_mac_zip="macOS, die .app zum selbst Kopieren in Input Methods.",
  f_win_x64="Windows 10/11, die meisten PCs. Empfohlen.", f_win_arm="Windows 11 auf ARM (Snapdragon, Surface Pro X).",
  f_win_zip="Windows x64, ohne Installation.", f_win_zip_arm="Windows ARM64, ohne Installation.",
  win_soon="Das Windows-Installationsprogramm wird gerade fertiggestellt und erscheint in den nächsten Tagen auf der Release-Seite.",
  req_h="Voraussetzungen", req=["macOS 13 Ventura oder neuer, Mac mit Apple Silicon oder Intel.", "Windows 10 oder 11, x64 oder ARM64.", "Jedes Tastaturlayout: Schweiz, deutsch · Deutsch · ABC/US · Österreich."],
  mac_h="Installation auf dem Mac",
  mac=["<b>" + f"MiKey-{VERSION}-macOS.dmg" + "</b> laden, öffnen und <b>Cài đặt MiKey.pkg</b> doppelklicken. Dieselbe Datei für Macs mit Apple Silicon (M1–M4) und Intel.",
       "macOS meldet, dass Apple die Software nicht auf Malware prüfen konnte: <b>Fertig</b> klicken. Das liegt daran, dass das Paket nicht mit einem Apple-Zertifikat signiert ist.",
       "<b>Systemeinstellungen › Datenschutz &amp; Sicherheit</b> öffnen, nach unten scrollen, bei MiKey <b>Trotzdem öffnen</b> klicken und das Passwort eingeben.",
       "Das Installationsprogramm kopiert MiKey nach <code>/Library/Input Methods</code>. Fortfahren, Installieren.",
       "<b>Systemeinstellungen › Tastatur › Eingabequellen › Bearbeiten…</b>, <b>+</b>, <b>Vietnamesisch</b> › <b>MiKey</b> › Hinzufügen. Fehlt MiKey, ab- und wieder anmelden.",
       "<b>MiKey</b> im Eingabemenü in der Menüleiste wählen. Darunter bleibt dein Layout aktiv, zum Beispiel Schweiz, deutsch."],
  mac_upd="Update: neue Version laden und darüber installieren. Entfernen: MiKey aus den Eingabequellen nehmen und <code>/Library/Input Methods/MiKey.app</code> löschen (Finder › Gehe zu › Gehe zum Ordner).",
  win_h="Installation unter Windows",
  win=["<b>" + f"MiKey-{VERSION}-x64-Setup.exe" + "</b> laden (oder arm64 für ARM-Geräte).",
       "Windows SmartScreen meldet <i>Der Computer wurde durch Windows geschützt</i>: <b>Weitere Informationen</b> › <b>Trotzdem ausführen</b>. Grund wie auf dem Mac: nicht signiert.",
       "MiKey wird nur für dein Benutzerkonto installiert, ohne Administratorrechte.",
       "MiKey sitzt im Infobereich (unten rechts). <kbd>Alt</kbd>+<kbd>Z</kbd> schaltet Vietnamesisch ↔ Englisch/Deutsch."],
  win_upd="Update: MiKey sucht einmal täglich nach neuen Versionen und installiert nur von MiKey signierte. Entfernen: Einstellungen › Apps › MiKey › Deinstallieren.",
  verify_h="Datei prüfen", verify_p="Die SHA-256-Prüfsumme oben muss zu deiner Datei passen. Mac: <code>shasum -a 256 MiKey-*.pkg</code>. Windows (PowerShell): <code>Get-FileHash MiKey-*.exe</code>.",
  older="Ältere Versionen und Quellcode: Release-Seite auf GitHub.",
  g_title="MiKey-Anleitung", g_desc="Telex-Tabelle, wie MiKey Englisch und Deutsch erkennt, Umschalten, Korrektur mit der Rücktaste, Tipps und Grenzen.",
  g_h1="Anleitung", g_lead="Alles, um mit MiKey schnell zu tippen, und die Sonderfälle.",
  g_toc="Inhalt",
  g_telex_h="Telex-Tabelle", g_marks="Zirkumflex, Hörnchen, Breve und đ", g_tones="Töne", g_ex="Beispiele",
  g_telex_p="Das Zeichen nach dem Buchstaben tippen, egal wo im Wort: <code>truowfng</code>, <code>truongwf</code> und <code>truwowngf</code> ergeben alle <b>trường</b>. Zweimal die Tontaste entfernt den Ton und behält den Buchstaben: <code>vaff</code> ergibt <b>vaf</b>.",
  g_place_h="Tonsetzung", g_place_p="Standard ist die neue Schreibweise: <b>hoà, thuý, khoẻ</b>. Für die alte (<b>hòa, thúy, khỏe</b>) auf dem Mac im Eingabemenü \"Bỏ dấu kiểu mới\" ausschalten.",
  g_switch_h="Sprache wechseln", g_switch=["<kbd>⌥</kbd>+<kbd>Z</kbd> auf dem Mac, <kbd>Alt</kbd>+<kbd>Z</kbd> unter Windows: Vietnamesisch ↔ Englisch/Deutsch. Auf dem Mac erscheint kurz <b>VI</b> oder <b>EN</b> beim Cursor.",
       "Auf dem Mac auch im Eingabemenü: <b>Tiếng Việt (Telex)</b> oder <b>English / Deutsch</b>.",
       "Nach einem Wechsel von Hand stellt MiKey 5 Sekunden lang nicht selbst um, damit deine Wahl gilt."],
  g_auto_h="Wie MiKey Englisch und Deutsch erkennt",
  g_auto=["MiKey entscheidet nur am Wortende: Leerzeichen, Satzzeichen (, . ; : ? ! ) \") oder Enter.",
          "Im vietnamesischen Modus: Sind deine Tasten ein echtes englisches oder deutsches Wort und die vietnamesische Lesart selten oder unmöglich, kommen die Tasten zurück und MiKey wechselt auf Englisch/Deutsch. <code>text</code> → <b>text</b>, <code>wir</code> → <b>wir</b>.",
          "Im englisch/deutschen Modus: Tippst du ein klar vietnamesisches Wort, setzt MiKey die Akzente und wechselt zurück. <code>treen</code> → <b>trên</b>, <code>ddi hocj</code> → <b>đi học</b>.",
          "Hat ein Wort zwei Lesarten (car / cả, too / tô), schaut MiKey auf das Wort davor und nimmt die Lesart, die in echten Texten häufiger ist.",
          "Häufige vietnamesische Wörter werden nie zu Englisch oder Deutsch."],
  g_umlaut_h="ä ö ü und Tottasten", g_umlaut_p="Bei ä ö ü ß é è à ç oder einer Tottaste (´ ` ^ ¨) holt MiKey die bisher getippten Tasten zurück und schaltet Telex bis zum Wortende ab. So stimmen <b>über</b>, <b>fährt</b>, <b>Grüsse</b>, <b>Café</b>, <b>Zürich</b> immer, auch mitten in einem vietnamesischen Satz: <i>đi học ở Zürich</i>.",
  g_de_h="Deutsch-Erkennung", g_de_p="Eingeschaltet. MiKey kennt rund 30'000 deutsche Wörter, auch ohne Umlaute geschrieben (fuer, schoen) und mit Schweizer ss (Strasse). Auf dem Mac im Eingabemenü abschaltbar: <b>Nhận biết tiếng Đức</b>.",
  g_undo_h="Korrigieren mit der Rücktaste", g_undo_p="Direkt nachdem MiKey ein Wort umgestellt hat, einmal <kbd>Rücktaste</kbd>: das Wort steht wieder so da, wie du es getippt hast, und die Sprache ist wie vorher. Tippst du am Wort weiter, prüft MiKey das ganze Wort neu.",
  g_tips_h="Tipps",
  g_tips=["<b>Abkürzungen und Namen in Grossbuchstaben</b>: Wörter mit zwei oder mehr Grossbuchstaben bleiben (NAS, HDD, USA, GoPro). Ganze Sätze mit Feststelltaste werden trotzdem vietnamesisch: <code>TOOI DDI HOCJ</code> → <b>TÔI ĐI HỌC</b>.",
          "<b>Code, Dateien, Pfade</b>: Wörter nach . _ - / bleiben: <code>file.txt</code>, <code>my_var</code>, <code>git push</code>.",
          "<b>Zahlen</b>: <code>5trawm</code> → <b>5trăm</b>, <code>100k</code> und <code>md5sum</code> bleiben.",
          "<b>Wörter mit zwei Lesarten</b>: in Grossbuchstaben tippen (GIF, HDD) oder vorher mit ⌥Z/Alt+Z wechseln."],
  g_limits_h="Bewusst vietnamesisch",
  g_limits_p="Einige Wörter sind zugleich häufiges Vietnamesisch und Englisch/Deutsch. MiKey bevorzugt Vietnamesisch, weil ein falsch umgestelltes vietnamesisches Wort mehr stört:",
  g_limits=[("gif", "gì"), ("hdd", "hđ (hợp đồng, Vertrag)"), ("rar", "rả (rôm rả)"), ("ist (am Satzanfang)", "ít")],
  g_limits_after="Nach einem deutschen Wort bleibt <code>ist</code> aber <b>ist</b>: <i>das ist gut</i>. Ein Wort ist oft falsch? Auf GitHub melden.",
  c_title="Änderungen in MiKey", c_desc="Was in jeder MiKey-Version neu ist.", c_h1="Änderungen", c_lead="Die neueste Version steht oben.",
  p_title="Datenschutz", p_desc="MiKey sammelt keine Daten. Was die Eingabe und die Website tun, klar beschrieben.", p_h1="Datenschutz", p_lead=f"Stand {RELEASE_DATE}. Kurz: MiKey sammelt nichts.",
  p_sections=[("Die Eingabe", ["Alles passiert auf deinem Gerät. MiKey schickt nicht, was du tippst.",
                               "Auf dem Mac stellt die MiKey-Eingabequelle keine Netzwerkverbindung her.",
                               "Unter Windows prüft MiKey einmal täglich auf Updates, indem es <code>mikey.mikephung.com/appcast.xml</code> lädt. Diese Anfrage ist wie jeder Website-Aufruf (IP-Adresse, Browser-Typ) und enthält nichts über dich oder dein Getipptes. In den Einstellungen abschaltbar.",
                               "Unter Windows gibt es ein \"Tipp-Protokoll\" zur Fehlersuche. Es ist ausgeschaltet, bleibt auf deinem Gerät und zeichnet nie in Passwortfeldern auf."]),
              ("Diese Website", ["Die Website besteht aus statischen HTML-Dateien: keine Cookies, keine Statistik, keine Werbung, keine externen Schriften oder Skripte.",
                                 "Ausgeliefert wird sie über Cloudflare. Wie jeder Webserver verarbeitet Cloudflare deine IP-Adresse, um die Seite zu senden und Angriffe abzuwehren.",
                                 "Die Download-Knöpfe führen zu GitHub, mit eigener Datenschutzerklärung."]),
              ("Kontakt", ["Fragen zum Datenschutz: ein Issue auf GitHub eröffnen oder über mikephung.com."])],
  a_title="Danksagung", a_desc="Code und Daten, auf denen MiKey aufbaut, mit Lizenzen.", a_h1="Danksagung",
  a_lead="MiKey steht auf den Schultern dieser Projekte. Danke an alle Autorinnen und Autoren.",
  a_code="Code", a_words="Daten für die Worthäufigkeiten (in der App stehen nur Zahlen, kein Text)", a_test="Daten nur zum Messen der Genauigkeit (nicht in der App)",
  a_head=("Name", "Von", "Lizenz"), a_stats="Wortstatistik",
  a_gpl=f"MiKey steht unter der GNU GPL-3.0. Der vollständige Quellcode jeder Version liegt auf <a href=\"{REPO}\">{REPO.replace('https://', '')}</a>.",
  nf_h1="Seite nicht gefunden", nf_p="Diese Seite gibt es nicht. Zur Startseite:",
),
"en": dict(
  skip="Skip to content", nav=[("download/", "Download"), ("guide/", "Guide"), ("#faq", "FAQ"), ("changelog/", "Changelog")],
  dl_mac="Download for macOS", dl_win="Download for Windows", dl_win_soon="Windows: coming soon", dl_all="All downloads", version=f"Version {VERSION}",
  meta="macOS 13 or later · Windows 10/11 · Free · Open source",
  foot_credits='MiKey is based on <a href="https://github.com/trungdq88/Vikey">Vikey</a> by Tony Dinh and <a href="https://github.com/tuyenvm/OpenKey">OpenKey</a> by Tuyen Mai.',
  foot_links=[("acknowledgements/", "Acknowledgements"), ("privacy/", "Privacy"), (REPO, "Source"), (REPO + "/issues", "Report a problem")],
  foot_license="GPL-3.0 license. Made by <a href=\"https://mikephung.com\">Mike Phung</a>.",
  home_title="MiKey: Vietnamese typing for people in Switzerland, Germany and Austria",
  home_desc="A Telex input method for macOS and Windows that recognises English and German: text never becomes tẽt, wir never ửi, ü never ơ. Free, open source, no data collected.",
  h1="Type Vietnamese, German and English. Without switching keyboards.",
  lead="MiKey is a Vietnamese Telex input method for people living in Switzerland, Germany and Austria. It notices English and German words by itself, and the ä ö ü keys just work.",
  d_keys="Keys", d_bad="Plain Telex", d_good="MiKey", demo_cap="The same keys: plain Telex and MiKey",
  prob_h="Sound familiar?", prob_p="You text friends in Vietnamese, then email a colleague in German, then type a command in the Terminal. Telex doesn't know what you're writing: s f r x j w can always be tone marks. So \"text\" becomes \"tẽt\" and \"wir\" becomes \"ửi\". On a Swiss keyboard it's worse: ü sits exactly where Telex uses [ to type ơ.",
  t_keys="You type", t_bad="Plain Telex", t_good="MiKey", fix_cap="Common Telex mistakes and what MiKey gives",
  feat_h="What MiKey does differently",
  feats=[("ä ö ü just work", "On ä ö ü ß é or a dead key, MiKey leaves the whole word alone: über, Grüße, Café, Zürich."),
         ("Knows German", "About 30,000 German words: wir, der, nur, dass, wissen stay as typed. Can be turned off."),
         ("Knows English", "About 40,000 English words and tech terms: text, server, deploy, osx, macos stay as typed."),
         ("Vietnamese stays Vietnamese", "Common Vietnamese words are never switched: gì, ít, có, tô."),
         ("One key to switch", "⌥Z on the Mac, Alt+Z on Windows: Vietnamese ↔ English/German, with a VI/EN label at the cursor."),
         ("Wrong guess? Backspace", "Right after a correction, Backspace brings back exactly what you typed.")],
  how_h="How MiKey decides",
  how=[("You type a word", "Telex works as usual while you type."),
       ("You finish the word", "On a space, punctuation or Enter, MiKey looks at the word: a Vietnamese syllable, or a real English or German word?"),
       ("MiKey keeps the right one", "For English or German your exact keys come back and MiKey switches to English/German. When a clearly Vietnamese word comes, it switches back by itself.")],
  inst_h="Installed in 3 steps",
  inst=["Download MiKey for your computer.", "Open the installer. The first time, macOS or Windows asks again because it isn't signed: see the detailed steps.", "Pick MiKey in the input menu (Mac) or find it in the system tray (Windows). Start typing."],
  inst_more="Detailed install steps",
  priv_h="What you type stays on your computer",
  priv_p="MiKey sends nothing anywhere: no account, no ads, no analytics. On the Mac it is an input source like ABC, so it needs no Accessibility permission. The code is open for anyone to check.",
  priv_more="Privacy policy",
  faq_h="FAQ",
  faq=[("Is MiKey free?", "Yes. MiKey is free and open source under the GPL-3.0."),
       ("Does it need the Accessibility permission on the Mac?", "No. MiKey is a macOS input source, like \"ABC\" or \"Swiss German\"."),
       ("Why does macOS/Windows warn me when installing?", "Because the installer isn't (yet) signed with a paid Apple or Microsoft certificate. The source is on GitHub, and the download page lists SHA-256 checksums."),
       ("Does it work with a Swiss or German (QWERTZ) keyboard?", "Yes, that's what it's made for. It reads the characters of your layout, so z/y and ä ö ü are right."),
       ("What if a word is guessed wrong?", "Press Backspace right after it to get back what you typed. If a Vietnamese word is often taken for German, turn off \"Nhận biết tiếng Đức\" in the input menu and report it on GitHub."),
       ("Is there a version for Linux, iPhone, Android?", "Not yet. Linux (IBus) is in progress. Vikey, the original, is available for iPhone and Android."),
       ("How is it different from Vikey?", "MiKey is a fork of Vikey (Tony Dinh) with what Vietnamese people in German-speaking countries need: umlaut keys, German words, tech words, and a real Mac input source.")],
  final_h="Try MiKey now", final_p="Free, installed in a minute, removed just as fast.",
  dl_title="Download MiKey for macOS and Windows", dl_desc=f"Download MiKey {VERSION} for macOS (Apple Silicon and Intel) and Windows (x64, ARM64), with install, update and uninstall steps.",
  dl_h1="Download MiKey", dl_lead=f"Version {VERSION}, released {RELEASE_DATE}. Free, no account.",
  f_head=("File", "For", "Size", "SHA-256"), f_cap="The files of this version",
  f_mac_dmg="macOS 13+, Apple Silicon (M1–M4) and Intel. Recommended.", f_mac_pkg="The installer alone, as in the .dmg.", f_mac_zip="macOS, the .app to copy into Input Methods yourself.",
  f_win_x64="Windows 10/11, most PCs. Recommended.", f_win_arm="Windows 11 on ARM (Snapdragon, Surface Pro X).",
  f_win_zip="Windows x64, no install.", f_win_zip_arm="Windows ARM64, no install.",
  win_soon="The Windows installer is being finished and will be on the releases page in the next few days.",
  req_h="Requirements", req=["macOS 13 Ventura or later, Apple Silicon or Intel Mac.", "Windows 10 or 11, x64 or ARM64.", "Any keyboard layout: Swiss German · German · ABC/US · Austrian."],
  mac_h="Install on macOS",
  mac=["Download <b>" + f"MiKey-{VERSION}-macOS.dmg" + "</b>, open it and double-click <b>Cài đặt MiKey.pkg</b>. The same file for Apple Silicon (M1–M4) and Intel Macs.",
       "macOS says Apple could not check it for malicious software: click <b>Done</b>. This is because the package isn't signed with an Apple certificate.",
       "Open <b>System Settings › Privacy &amp; Security</b>, scroll down, click <b>Open Anyway</b> next to MiKey and enter your password.",
       "The installer copies MiKey to <code>/Library/Input Methods</code>. Continue, Install.",
       "Open <b>System Settings › Keyboard › Input Sources › Edit…</b>, click <b>+</b>, choose <b>Vietnamese</b> › <b>MiKey</b> › Add. If MiKey isn't listed, log out and back in.",
       "Pick <b>MiKey</b> in the input menu in the menu bar. Your layout stays active underneath, for example Swiss German."],
  mac_upd="Update: download the new version and install it over the old one. Remove: take MiKey out of Input Sources, then delete <code>/Library/Input Methods/MiKey.app</code> (Finder › Go › Go to Folder).",
  win_h="Install on Windows",
  win=["Download <b>" + f"MiKey-{VERSION}-x64-Setup.exe" + "</b> (or arm64 for ARM devices).",
       "Windows SmartScreen says <i>Windows protected your PC</i>: click <b>More info</b> › <b>Run anyway</b>. Same reason as on the Mac: not signed.",
       "MiKey is installed for your user account only, no administrator rights needed.",
       "MiKey lives in the system tray (bottom right). <kbd>Alt</kbd>+<kbd>Z</kbd> switches Vietnamese ↔ English/German."],
  win_upd="Update: MiKey checks for a new version once a day and only installs ones signed by MiKey. Remove: Settings › Apps › MiKey › Uninstall.",
  verify_h="Verify the file", verify_p="The SHA-256 above must match your download. Mac: <code>shasum -a 256 MiKey-*.pkg</code>. Windows (PowerShell): <code>Get-FileHash MiKey-*.exe</code>.",
  older="Older versions and source code: the releases page on GitHub.",
  g_title="MiKey guide", g_desc="Telex table, how MiKey recognises English and German, switching, undo with Backspace, tips and limits.",
  g_h1="Guide", g_lead="Everything you need to type fast with MiKey, and the special cases.",
  g_toc="Contents",
  g_telex_h="Telex table", g_marks="Circumflex, horn, breve and đ", g_tones="Tones", g_ex="Examples",
  g_telex_p="Type the mark after the letter, anywhere in the word: <code>truowfng</code>, <code>truongwf</code> and <code>truwowngf</code> all give <b>trường</b>. Pressing the tone key twice removes the tone and keeps the letter: <code>vaff</code> gives <b>vaf</b>.",
  g_place_h="Tone placement", g_place_p="By default MiKey uses the modern placement: <b>hoà, thuý, khoẻ</b>. For the classic one (<b>hòa, thúy, khỏe</b>) turn off \"Bỏ dấu kiểu mới\" in the input menu on the Mac.",
  g_switch_h="Switching language", g_switch=["<kbd>⌥</kbd>+<kbd>Z</kbd> on the Mac, <kbd>Alt</kbd>+<kbd>Z</kbd> on Windows: Vietnamese ↔ English/German. On the Mac a small <b>VI</b> or <b>EN</b> shows at the cursor.",
       "On the Mac also from the input menu: <b>Tiếng Việt (Telex)</b> or <b>English / Deutsch</b>.",
       "After you switch by hand, MiKey doesn't switch by itself for 5 seconds, so your choice holds."],
  g_auto_h="How MiKey recognises English and German",
  g_auto=["MiKey only decides when a word ends: a space, punctuation (, . ; : ? ! ) \") or Enter.",
          "In Vietnamese mode: if your keys are a real English or German word and the Vietnamese reading is rare or impossible, the keys come back and MiKey switches to English/German. <code>text</code> → <b>text</b>, <code>wir</code> → <b>wir</b>.",
          "In English/German mode: if you type a clearly Vietnamese word, MiKey adds the marks and switches back. <code>treen</code> → <b>trên</b>, <code>ddi hocj</code> → <b>đi học</b>.",
          "When a word has two readings (car / cả, too / tô), MiKey looks at the word before it and uses the reading that is more common in real text.",
          "Common Vietnamese words are never switched to English or German."],
  g_umlaut_h="ä ö ü and dead keys", g_umlaut_p="On ä ö ü ß é è à ç or a dead key (´ ` ^ ¨), MiKey puts back the keys typed so far and turns Telex off until the word ends. So <b>über</b>, <b>fährt</b>, <b>Grüße</b>, <b>Café</b>, <b>Zürich</b> are always right, even inside a Vietnamese sentence: <i>đi học ở Zürich</i>.",
  g_de_h="German detection", g_de_p="On by default. MiKey knows about 30,000 German words, also written without umlauts (fuer, schoen) and with the Swiss ss (Strasse). On the Mac, turn it off in the input menu: <b>Nhận biết tiếng Đức</b>.",
  g_undo_h="Undo with Backspace", g_undo_p="Right after MiKey changes a word, press <kbd>Backspace</kbd> once: the word is back exactly as you typed it and the language is as before. If you keep typing on that word, MiKey checks the whole word again.",
  g_tips_h="Tips",
  g_tips=["<b>Acronyms and capitalised names</b>: words with two or more capitals stay as typed (NAS, HDD, USA, GoPro). Whole sentences with Caps Lock still become Vietnamese: <code>TOOI DDI HOCJ</code> → <b>TÔI ĐI HỌC</b>.",
          "<b>Code, files, paths</b>: words after . _ - / stay as typed: <code>file.txt</code>, <code>my_var</code>, <code>git push</code>.",
          "<b>Numbers</b>: <code>5trawm</code> → <b>5trăm</b>; <code>100k</code> and <code>md5sum</code> stay.",
          "<b>Words with two readings</b>: type them in capitals (GIF, HDD), or switch with ⌥Z/Alt+Z first."],
  g_limits_h="Kept Vietnamese on purpose",
  g_limits_p="A few words are both common Vietnamese and English/German. MiKey prefers Vietnamese, because a wrongly switched Vietnamese word is more annoying:",
  g_limits=[("gif", "gì"), ("hdd", "hđ (hợp đồng, contract)"), ("rar", "rả (rôm rả)"), ("ist (start of a sentence)", "ít")],
  g_limits_after="After a German word, <code>ist</code> stays <b>ist</b>: <i>das ist gut</i>. A word often comes out wrong? Report it on GitHub.",
  c_title="MiKey changelog", c_desc="What is new in each MiKey version.", c_h1="Changelog", c_lead="Newest version first.",
  p_title="Privacy", p_desc="MiKey collects no data. What the input method and the website do, plainly.", p_h1="Privacy", p_lead=f"Updated {RELEASE_DATE}. In short: MiKey collects nothing.",
  p_sections=[("The input method", ["Everything happens on your computer. MiKey does not send what you type anywhere.",
                                    "On the Mac, the MiKey input method makes no network connections.",
                                    "On Windows, MiKey checks for updates once a day by downloading <code>mikey.mikephung.com/appcast.xml</code>. This request is like any page visit (IP address, browser type) and contains nothing about you or what you type. It can be turned off in the settings.",
                                    "On Windows there is a \"typing log\" for debugging. It is off by default, stays on your computer and never records in password fields."]),
              ("This website", ["The website is static HTML files: no cookies, no analytics, no ads, no external fonts or scripts.",
                                "It is served through Cloudflare. Like any web server, Cloudflare processes your IP address to deliver the page and block attacks.",
                                "The download buttons lead to GitHub, which has its own privacy policy."]),
              ("Contact", ["Privacy questions: open an issue on GitHub or get in touch through mikephung.com."])],
  a_title="Acknowledgements", a_desc="The code and data MiKey is built from, with licenses.", a_h1="Acknowledgements",
  a_lead="MiKey stands on the shoulders of these projects. Thank you to their authors.",
  a_code="Code", a_words="Data the word frequencies are counted from (only counts are in the app, no text)", a_test="Data used only to measure accuracy (not in the app)",
  a_head=("Name", "By", "License"), a_stats="word statistics",
  a_gpl=f"MiKey is released under the GNU GPL-3.0. The full source of every version is at <a href=\"{REPO}\">{REPO.replace('https://', '')}</a>.",
  nf_h1="Page not found", nf_p="This page doesn't exist. Go to the home page:",
),
}

# ---- layout -----------------------------------------------------------------------------------------------------
def url(code, slug=""): return f"{SITE}/{PREFIX[code]}{slug}"

def layout(code, slug, title, desc, body, jsonld=None, noindex=False):
    t = S[code]
    depth = (1 if PREFIX[code] else 0) + slug.count("/")
    up = "../" * depth
    home = up or "./"
    def href(target):
        if target.startswith("http"): return target
        if target.startswith("#"): return (up + PREFIX[code] if depth else "") + target if slug else target
        return up + PREFIX[code] + target if depth else target
    nav = "".join(f'<a href="{href(h)}">{e(l)}</a>' for h, l in t["nav"])
    langs = "".join(f'<a href="{(up + PREFIX[c] + slug) or "./"}" hreflang="{c}" lang="{c}"' + (' aria-current="true"' if c == code else "")
                    + f'>{c.upper()}<span class="sr"> {NAME[c]}</span></a>' for c in LANGS)
    alternates = "".join(f'<link rel="alternate" hreflang="{c}" href="{url(c, slug)}">' for c in LANGS) + \
                 f'<link rel="alternate" hreflang="x-default" href="{url("vi", slug)}">'
    foot = " · ".join(f'<a href="{href(h)}">{e(l)}</a>' for h, l in t["foot_links"])
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n' if jsonld else ""
    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{url(code, slug)}">'}
{'' if noindex else alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="MiKey">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url(code, slug)}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:creator" content="@m1k3_png">
<meta name="theme-color" content="#4F46E5">
<link rel="icon" type="image/png" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/icon-256.png">
<link rel="stylesheet" href="{up}style.css">
{ld}</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>
<div class="wrap">
<header class="top">
  <a class="brand" href="{up + PREFIX[code] if depth else './'}"><img src="{up}assets/icon-256.png" alt="" width="32" height="32"><span>Mi<span class="key">Key</span></span></a>
  <nav class="main" aria-label="Menu">{nav}</nav>
  <nav class="lang" aria-label="Language">{langs}</nav>
</header>
<main id="main">
{body}
</main>
<footer>
  <p>{t['foot_credits']}</p>
  <p>{foot}</p>
  <p>{t['foot_license']}</p>
</footer>
</div>
<script src="{up}os.js" defer></script>
</body>
</html>
"""

def rel_link(code, slug, target):
    """A link from page <slug> of language <code> to another page of the same language."""
    depth = (1 if PREFIX[code] else 0) + slug.count("/")
    return ("../" * depth + PREFIX[code] + target) if depth else target

def asset(name): return f"{REL}/{name}"

def buttons(code, slug, cls=""):
    t = S[code]
    win = asset(f"MiKey-{VERSION}-x64-Setup.exe") if WIN_READY else rel_link(code, slug, "download/#windows")
    return (f'<div class="cta {cls}"><a class="btn" data-os="mac" href="{asset(f"MiKey-{VERSION}-macOS.dmg")}">{e(t["dl_mac"])}</a>'
            f'<a class="btn alt" data-os="win" href="{win}">{e(t["dl_win"] if WIN_READY else t["dl_win_soon"])}</a>'
            f'<a class="more" href="{rel_link(code, slug, "download/")}">{e(t["dl_all"])} ›</a></div>')

def software_ld(code):
    return {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "MiKey", "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "macOS 13+, Windows 10/11", "softwareVersion": VERSION, "inLanguage": ["vi", "de", "en"],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CHF"}, "license": "https://www.gnu.org/licenses/gpl-3.0.html",
            "downloadUrl": f"{REPO}/releases/latest", "url": url(code), "description": S[code]["home_desc"],
            "author": {"@type": "Person", "name": "Mike Phung", "url": "https://mikephung.com"}}

# ---- pages ------------------------------------------------------------------------------------------------------
def table(cap, head, rows, cls=""):
    th = "".join(f'<th scope="col">{e(h)}</th>' for h in head)
    return f'<table class="{cls}"><caption>{e(cap)}</caption><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>'

def home(code):
    t = S[code]
    demo = table(t["demo_cap"], (t["d_keys"], t["d_bad"], t["d_good"]),
                 "".join(f'<tr><td class="keys">{e(k)}</td><td class="out bad"><del>{e(b)}</del></td><td class="out good">{e(g)}</td></tr>' for k, b, g in DEMO), "demo-t")
    fixes = table(t["fix_cap"], (t["t_keys"], t["t_bad"], t["t_good"]),
                  "".join(f'<tr><td class="mono">{e(k)}</td><td class="bad"><del>{e(b)}</del></td><td class="good">{e(g)}</td></tr>' for k, b, g in FIXES), "fix")
    feats = "".join(f'<div class="card"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in t["feats"])
    how = "".join(f'<li class="card"><h3>{e(h)}</h3><p>{e(p)}</p></li>' for h, p in t["how"])
    inst = "".join(f"<li>{e(s)}</li>" for s in t["inst"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in t["faq"])
    body = f"""<div class="hero">
  <div>
    <h1>{e(t['h1'])}</h1>
    <p class="lead">{e(t['lead'])}</p>
    {buttons(code, "")}
    <p class="meta">{e(t['version'])} · {e(t['meta'])}</p>
  </div>
  <div class="demo">{demo}</div>
</div>
<section aria-labelledby="problem"><h2 id="problem">{e(t['prob_h'])}</h2><p class="lead">{e(t['prob_p'])}</p>{fixes}</section>
<section aria-labelledby="features"><h2 id="features">{e(t['feat_h'])}</h2><div class="grid three">{feats}</div></section>
<section aria-labelledby="how"><h2 id="how">{e(t['how_h'])}</h2><ol class="grid three plain">{how}</ol></section>
<section aria-labelledby="install"><h2 id="install">{e(t['inst_h'])}</h2><ol class="steps big">{inst}</ol>
  <p><a href="{rel_link(code, '', 'download/')}">{e(t['inst_more'])} ›</a></p></section>
<section aria-labelledby="privacy" class="band"><h2 id="privacy">{e(t['priv_h'])}</h2><p class="lead">{e(t['priv_p'])}</p>
  <p><a href="{rel_link(code, '', 'privacy/')}">{e(t['priv_more'])} ›</a></p></section>
<section aria-labelledby="faq"><h2 id="faq">{e(t['faq_h'])}</h2>{faq}</section>
<section aria-labelledby="final" class="final"><h2 id="final">{e(t['final_h'])}</h2><p>{e(t['final_p'])}</p>{buttons(code, "", "center")}</section>"""
    return layout(code, "", t["home_title"], t["home_desc"], body, software_ld(code))

def download(code):
    t = S[code]; slug = "download/"
    rows = ""
    for key, name, plat, note in FILES:
        info = INFO[key]
        if plat == "win" and not WIN_READY: continue
        size = mb(info["size"]) if info else "–"
        sha = f'<code class="sha">{info["sha256"]}</code>' if info else "–"
        rows += f'<tr><td><a href="{asset(name)}">{e(name)}</a></td><td>{e(t[note])}</td><td>{size}</td><td>{sha}</td></tr>'
    files = table(t["f_cap"], t["f_head"], rows, "files")
    soon = "" if WIN_READY else f'<p class="note">{e(t["win_soon"])}</p>'
    req = "".join(f"<li>{e(r)}</li>" for r in t["req"])
    mac = "".join(f"<li>{s}</li>" for s in t["mac"])
    win = "".join(f"<li>{s}</li>" for s in t["win"])
    body = f"""<div class="page-head"><h1>{e(t['dl_h1'])}</h1><p class="lead">{e(t['dl_lead'])}</p>{buttons(code, slug)}</div>
<section aria-label="{e(t['f_cap'])}">{files}{soon}<p><a href="{REPO}/releases">{e(t['older'])}</a></p></section>
<section aria-labelledby="req"><h2 id="req">{e(t['req_h'])}</h2><ul>{req}</ul></section>
<section aria-labelledby="mac" id="macos"><h2 id="mac">{e(t['mac_h'])}</h2><ol class="steps">{mac}</ol><p class="note">{t['mac_upd']}</p></section>
<section aria-labelledby="win" id="windows"><h2 id="win">{e(t['win_h'])}</h2>{soon}<ol class="steps">{win}</ol><p class="note">{t['win_upd']}</p></section>
<section aria-labelledby="verify"><h2 id="verify">{e(t['verify_h'])}</h2><p>{t['verify_p']}</p></section>"""
    return layout(code, slug, t["dl_title"], t["dl_desc"], body, software_ld(code))

def guide(code):
    t = S[code]; slug = "guide/"
    sections = [("telex", t["g_telex_h"]), ("placement", t["g_place_h"]), ("switch", t["g_switch_h"]), ("auto", t["g_auto_h"]),
                ("umlaut", t["g_umlaut_h"]), ("german", t["g_de_h"]), ("undo", t["g_undo_h"]), ("tips", t["g_tips_h"]), ("limits", t["g_limits_h"])]
    toc = "".join(f'<li><a href="#{a}">{e(h)}</a></li>' for a, h in sections)
    marks = table(t["g_marks"], (t["d_keys"], t["d_good"]), "".join(f"<tr><td><kbd>{e(k)}</kbd></td><td>{e(v)}</td></tr>" for k, v in TELEX_MARKS))
    tones = table(t["g_tones"], (t["d_keys"], "a +", ""), "".join(f"<tr><td><kbd>{e(k)}</kbd></td><td>{e(v)}</td><td>{e(n)}</td></tr>" for k, v, n in TELEX_TONES))
    ex = table(t["g_ex"], (t["d_keys"], t["d_good"]), "".join(f"<tr><td class=\"mono\">{e(k)}</td><td>{e(v)}</td></tr>" for k, v in TELEX_EXAMPLES))
    li = lambda items: "".join(f"<li>{x}</li>" for x in items)
    limits = table(t["g_limits_h"], (t["d_keys"], t["d_good"]), "".join(f"<tr><td class=\"mono\">{e(k)}</td><td>{e(v)}</td></tr>" for k, v in t["g_limits"]))
    body = f"""<div class="page-head"><h1>{e(t['g_h1'])}</h1><p class="lead">{e(t['g_lead'])}</p></div>
<nav class="toc" aria-labelledby="toc-h"><h2 id="toc-h">{e(t['g_toc'])}</h2><ol>{toc}</ol></nav>
<section id="telex"><h2>{e(t['g_telex_h'])}</h2><p>{t['g_telex_p']}</p><div class="grid three">{marks}{tones}{ex}</div></section>
<section id="placement"><h2>{e(t['g_place_h'])}</h2><p>{t['g_place_p']}</p></section>
<section id="switch"><h2>{e(t['g_switch_h'])}</h2><ul>{li(t['g_switch'])}</ul></section>
<section id="auto"><h2>{e(t['g_auto_h'])}</h2><ol>{li(t['g_auto'])}</ol></section>
<section id="umlaut"><h2>{e(t['g_umlaut_h'])}</h2><p>{t['g_umlaut_p']}</p></section>
<section id="german"><h2>{e(t['g_de_h'])}</h2><p>{t['g_de_p']}</p></section>
<section id="undo"><h2>{e(t['g_undo_h'])}</h2><p>{t['g_undo_p']}</p></section>
<section id="tips"><h2>{e(t['g_tips_h'])}</h2><ul>{li(t['g_tips'])}</ul></section>
<section id="limits"><h2>{e(t['g_limits_h'])}</h2><p>{e(t['g_limits_p'])}</p>{limits}<p>{t['g_limits_after']}</p></section>"""
    return layout(code, slug, t["g_title"], t["g_desc"], body)

def changelog(code):
    t = S[code]; slug = "changelog/"
    items = ""
    for ver, date, notes in RELEASES:
        n = notes[code]
        items += (f'<article class="release" id="v{ver}"><h2>MiKey {ver}</h2><p class="meta"><time datetime="{date}">{date}</time> · '
                  f'<a href="{REPO}/releases/tag/v{ver}">GitHub</a></p><p>{e(n[0])}</p><ul>' + "".join(f"<li>{e(x)}</li>" for x in n[1:]) + "</ul></article>")
    body = f'<div class="page-head"><h1>{e(t["c_h1"])}</h1><p class="lead">{e(t["c_lead"])}</p></div>{items}'
    return layout(code, slug, t["c_title"], t["c_desc"], body)

def privacy(code):
    t = S[code]; slug = "privacy/"
    secs = "".join(f'<section><h2>{e(h)}</h2><ul>' + "".join(f"<li>{x}</li>" for x in items) + "</ul></section>" for h, items in t["p_sections"])
    body = f'<div class="page-head"><h1>{e(t["p_h1"])}</h1><p class="lead">{e(t["p_lead"])}</p></div>{secs}'
    return layout(code, slug, t["p_title"], t["p_desc"], body)

def acknowledgements(code):
    t = S[code]; slug = "acknowledgements/"
    def rows(lst):
        out = ""
        for name, by, lic, link in lst:
            n = f'<a href="{link}">{e(name)}</a>' if link else e(name)
            out += f"<tr><td>{n}</td><td>{e(by)}</td><td>{e(lic or t['a_stats'])}</td></tr>"
        return out
    body = (f'<div class="page-head"><h1>{e(t["a_h1"])}</h1><p class="lead">{e(t["a_lead"])}</p></div>'
            f'<section>{table(t["a_code"], t["a_head"], rows(CREDITS_CODE))}</section>'
            f'<section>{table(t["a_words"], t["a_head"], rows(CREDITS_WORDS))}</section>'
            f'<section>{table(t["a_test"], t["a_head"], rows(CREDITS_TEST))}</section>'
            f'<section><p>{t["a_gpl"]}</p></section>')
    return layout(code, slug, t["a_title"], t["a_desc"], body)

def not_found():
    # one page for every language: Cloudflare Pages serves /404.html for any missing path
    parts = []
    for c in LANGS:
        head = f'<h1>{e(S[c]["nf_h1"])}</h1>' if c == "vi" else f'<p class="h1like">{e(S[c]["nf_h1"])}</p>'
        parts.append(f'<div lang="{c}" class="nf">{head}<p>{e(S[c]["nf_p"])} <a href="/{PREFIX[c]}">mikey.mikephung.com/{PREFIX[c]}</a></p></div>')
    html_ = layout("vi", "", "404 · MiKey", S["vi"]["nf_p"], "".join(parts), noindex=True)
    # absolute asset paths: the 404 page is served at any depth
    return html_.replace('href="style.css"', 'href="/style.css"').replace('src="assets/', 'src="/assets/').replace('href="assets/', 'href="/assets/') \
                .replace('src="os.js"', 'src="/os.js"').replace('href="./"', 'href="/"').replace('href="download/', 'href="/download/') \
                .replace('href="guide/', 'href="/guide/').replace('href="changelog/', 'href="/changelog/').replace('href="#faq"', 'href="/#faq"') \
                .replace('href="acknowledgements/', 'href="/acknowledgements/').replace('href="privacy/', 'href="/privacy/') \
                .replace('href="de/"', 'href="/de/"').replace('href="en/"', 'href="/en/"').replace('href="./" hreflang', 'href="/" hreflang')

PAGES = [("", home), ("download/", download), ("guide/", guide), ("changelog/", changelog), ("privacy/", privacy), ("acknowledgements/", acknowledgements)]

def write(rel, text):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)
    print("wrote", rel)

for code in LANGS:
    for slug, fn in PAGES:
        write(PREFIX[code] + slug + "index.html", fn(code))
write("404.html", not_found())
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
      + "".join(f"  <url><loc>{url(c, s)}</loc>" + "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{url(a, s)}"/>' for a in LANGS) + "</url>\n"
                for s, _ in PAGES for c in LANGS) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
write("CNAME", "mikey.mikephung.com\n")
# stable short links for posts: /mac and /windows always point to the current files
write("_redirects", f"/mac {asset(f'MiKey-{VERSION}-macOS.dmg')} 302\n"
      + (f"/windows {asset(f'MiKey-{VERSION}-x64-Setup.exe')} 302\n" if WIN_READY else "/windows /download/#windows 302\n")
      + f"/github {REPO} 302\n")
print("windows files:", "yes" if WIN_READY else "not yet (the page says so)")
