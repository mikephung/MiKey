# mikey.mikephung.com

The MiKey landing page: Vietnamese (`/`), German (`/de/`), English (`/en/`). Plain HTML and CSS, no JavaScript,
no trackers, no external fonts or CDNs.

```sh
python3 site-mikey/build.py    # regenerate the three pages, sitemap.xml, robots.txt, CNAME from build.py
python3 site-mikey/check.py    # HTML parses, local links exist, lang/title/h1/alt on every page
```

Edit the copy in `build.py` (one dictionary per language), not the generated `index.html` files.
The "plain Telex" examples are real engine output (`VIKEY_AUTO_OFF=1 Tools/autoswitch/test/harness lines`).
`appcast.xml` is the update feed, written by `Tools/release/mikey_appcast.py`; the Windows app reads it.

## Deploy on Cloudflare Pages

1. Cloudflare dashboard › Workers & Pages › Create › Pages › **Connect to Git** › `mikephung/MiKey`.
2. Production branch `main`, **Root directory** `site-mikey`, **Build command** empty, **Build output directory** `/`.
3. After the first deploy: the project › Custom domains › **Set up a custom domain** › `mikey.mikephung.com`.
   With mikephung.com's DNS on Cloudflare, Cloudflare adds the `CNAME mikey → <project>.pages.dev` record itself.
   The root `mikephung.com` stays on Google Sites; only the `mikey` subdomain points to Pages.

Every push to `main` then redeploys the site. (`CNAME` is only used if the site is ever moved to GitHub Pages.)
