# mikey.mikephung.com — plan

## Who it is for and what it must do

**Visitors.** Vietnamese people in Switzerland, Germany and Austria (students, workers, families) who type
Vietnamese, German and English every day, mostly on a Mac or a Windows laptop with a QWERTZ keyboard.
They arrive from a Facebook group post, X, Reddit or a search ("gõ tiếng việt bàn phím thụy sĩ", "telex umlaut").
Second audience: German/Swiss partners, colleagues and IT departments who need to trust what is installed.

**Goals, in order.**
1. In 5 seconds: "this fixes *my* problem" (tẽt, ửi, ơber) and where to download it.
2. Install without help: unsigned-package warnings explained before they scare people.
3. Trust: free, open source, nothing leaves the computer, who made it, credits.
4. Keep users: a guide for the edge cases, a changelog, a way to report wrong words.

**Not goals.** No tracking, accounts, newsletter, cookie banner, or JavaScript the page needs to work.

## Pages (each in Vietnamese `/`, German `/de/`, English `/en/`)

| Page | Path | Content |
|---|---|---|
| Home | `/` | hero + download (OS detected), before/after demo, the problem, features, how it works, 3-step install, privacy, FAQ, final CTA |
| Download | `/download/` | every file of the current version with size and SHA-256, requirements, install steps per OS with the warning screens explained, update, uninstall |
| Guide | `/guide/` | Telex table, tone placement, switching (⌥Z/Alt+Z, menu), how auto-detection works, German detection, Backspace undo, tips (names, acronyms, codes, URLs), known trade-offs (ist/ít, gif/gì, hdd/hđ, rar/rả) |
| Changelog | `/changelog/` | release notes, newest first (from `releases` in build.py) |
| Privacy | `/privacy/` | what the app does and does not do, the website (static, Cloudflare logs), contact |
| Credits | `/credits/` | Vikey, OpenKey, data sources and licenses, GPL source offer |
| 404 | `/404.html` | short, links home in all three languages |

## Every page

- Header: logo, nav (Download · Guide · FAQ · Changelog), language switch that keeps the current page.
- Footer: credits line, license, source, report a problem, privacy, author.
- `<html lang>`, title, description, canonical, hreflang (vi/de/en + x-default), Open Graph + Twitter card
  with a 1200×630 image, favicon, theme colour.
- Home and Download: JSON-LD `SoftwareApplication` (name, OS, price 0, version, download URL).
- Accessibility: skip link, landmarks, one h1, real tables with headers and captions, visible focus,
  contrast AA in light and dark mode, no information in colour only (struck-through + labels), works without JS.

## Download links

One `VERSION` in build.py. Buttons link to the exact GitHub release assets
(`/releases/download/v<VERSION>/MiKey-<VERSION>-macOS.pkg`, `…-x64-Setup.exe`, `…-arm64-Setup.exe`, portable zips)
and "all versions" to `/releases`. Sizes and SHA-256 are read from `dist/<VERSION>/` when it exists.
A 20-line script (`os.js`, optional) puts the visitor's OS first; without it both buttons show.

## Tech

- `build.py`: one layout, one dictionary of copy per language, pages as functions. Output is committed
  so Cloudflare Pages needs no build step.
- `check.py`: HTML parses, every local link/asset exists, every page has lang/title/one h1/alt/hreflang,
  no page missing in a language.
- `_headers` (Cloudflare): CSP `default-src 'self'`, no referrer leak, nosniff, frame-deny, long cache for assets.
- `_redirects`: `/download/latest/mac` etc. to the current files (stable links for posts).
- `assets/og.png` 1200×630 drawn by `tools/make_og.swift`.
- Hosting: Cloudflare Pages, root `site-mikey`, custom domain `mikey.mikephung.com` (CNAME on Cloudflare DNS);
  the root domain stays on Google Sites.

## Copy rules

- Vietnamese: natural, full diacritics, "bạn". German: Swiss-friendly (ss, no ß in our own copy), "du".
  English: plain. Short sentences.
- Every example of a mistake is real engine output (`VIKEY_AUTO_OFF=1 Tools/autoswitch/test/harness`).
- Honest: unsigned packages, Linux not yet, known trade-offs, based on Vikey/OpenKey.

## Later

Screenshots of the input menu and settings; a short screen recording; testimonials once there are users;
Linux page; Product Hunt.
