# mikey.mikephung.com

The MiKey website (plan: `PLAN.md`). Vietnamese at `/`, German at `/de/`, English at `/en/`; pages: home, download,
guide, changelog, privacy, acknowledgements, 404. Plain HTML and CSS, one optional script (`os.js`), no trackers,
no external fonts or CDNs.

```sh
python3 site-mikey/build.py    # regenerate every page, sitemap.xml, robots.txt, CNAME, _redirects
python3 site-mikey/check.py    # HTML parses, local links exist, lang/title/h1/alt, every page in all languages
swift site-mikey/tools/make_og.swift site-mikey/assets/og.png site-mikey/assets/icon-512.png   # share image
```

- Copy lives in `build.py` (one dictionary per language). Don't edit the generated `index.html` files.
- `VERSION` in `build.py` sets every download link. File sizes and SHA-256 come from `dist/<VERSION>/`
  (made by `Tools/release/release_mikey.sh`): rebuild the site after the final release build.
  Windows files appear automatically once `MiKey-<VERSION>-x64-Setup.exe` is in `dist/<VERSION>/`; until then
  the pages say "coming soon".
- "Plain Telex" examples are real engine output (`VIKEY_AUTO_OFF=1 Tools/autoswitch/test/harness lines`).
- `appcast.xml` is the update feed (written by `Tools/release/mikey_appcast.py`); the Windows app reads it.
- `_headers`: security headers and caching on Cloudflare. `_redirects`: short links `/mac`, `/windows`, `/github`.

## Release checklist (site part)

1. `Tools/release/release_mikey.sh <version>` (makes `dist/<version>/`).
2. In `build.py`: `VERSION`, `RELEASE_DATE`, a new entry at the top of `RELEASES` (vi/de/en).
3. `python3 site-mikey/build.py && python3 site-mikey/check.py`, commit, push.
4. After the GitHub release exists: open `/mac` on the live site and check that the download starts.

## Deploy on Cloudflare Pages (once)

1. Cloudflare dashboard › Workers & Pages › Create › Pages › **Connect to Git** › `mikephung/MiKey`.
2. Production branch `main`, **Root directory** `site-mikey`, **Build command** empty, **Build output directory** `/`.
3. After the first deploy: the project › Custom domains › **Set up a custom domain** › `mikey.mikephung.com`.
   With mikephung.com's DNS on Cloudflare, Cloudflare adds the `CNAME mikey → <project>.pages.dev` record itself.
   The root `mikephung.com` stays on Google Sites; only the `mikey` subdomain points to Pages.
4. Check: `https://mikey.mikephung.com/`, `/de/`, `/en/`, `/download/`, a missing path shows the 404 page,
   and the response headers include the Content-Security-Policy from `_headers`.

Every push to `main` then redeploys. (`CNAME` is only used if the site is ever moved to GitHub Pages.)
