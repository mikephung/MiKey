#!/bin/zsh
# Checks the live site: every page answers, the short links point to the current release files, the 404 page,
# the security headers, and that the live pages are the ones built from this repo.
# usage: zsh site-mikey/check_live.sh [https://mikey.mikephung.com]
SITE=${1:-https://mikey.mikephung.com}
cd "$(dirname "$0")"
VER=$(grep -m1 '^VERSION = ' build.py | cut -d'"' -f2)
fail=0
ok()  { echo "ok   $1"; }
bad() { echo "FAIL $1"; fail=1; }

for p in / /de/ /en/ /download/ /guide/ /changelog/ /privacy/ /acknowledgements/ \
         /de/download/ /en/download/ /de/guide/ /en/guide/ /sitemap.xml /robots.txt /appcast.xml /assets/og.png; do
  c=$(curl -s -o /dev/null -w '%{http_code}' "$SITE$p")
  [ "$c" = 200 ] && ok "$p ($c)" || bad "$p ($c)"
done

# the live pages are the built ones (same bytes as site-mikey/)
for p in index.html de/index.html download/index.html; do
  url="$SITE/${p%index.html}"
  if cmp -s <(curl -s "$url") "$p"; then ok "live $url == repo $p"; else bad "live $url differs from repo $p (not deployed yet?)"; fi
done

# short links -> the current release files, which must download
for s in mac windows; do
  loc=$(curl -s -o /dev/null -w '%{redirect_url}' "$SITE/$s")
  case "$loc" in *"/v$VER/"*) ok "/$s -> $loc" ;; *) bad "/$s -> '$loc' (want v$VER)" ;; esac
  c=$(curl -sL -o /dev/null -w '%{http_code}' -r 0-0 "$loc")
  [ "$c" = 200 ] || [ "$c" = 206 ] && ok "  downloads ($c)" || bad "  download answers $c"
done

# a missing page: our 404 page with status 404
c=$(curl -s -o /tmp/mikey-404.html -w '%{http_code}' "$SITE/no-such-page-$$")
grep -q "mikey.mikephung.com/de/" /tmp/mikey-404.html && [ "$c" = 404 ] && ok "404 page ($c)" || bad "404 page (status $c)"

# security headers from _headers
h=$(curl -sI "$SITE/")
for k in content-security-policy x-content-type-options x-frame-options referrer-policy; do
  echo "$h" | grep -qi "^$k:" && ok "header $k" || bad "header $k missing"
done
echo "$h" | grep -qi "^strict-transport-security:" && ok "header strict-transport-security" || echo "note no HSTS header (Cloudflare: SSL/TLS > Edge Certificates > HSTS)"

# HTTP -> HTTPS
loc=$(curl -s -o /dev/null -w '%{redirect_url}' "http://${SITE#https://}/")
case "$loc" in https://*) ok "http -> https" ;; *) bad "http does not redirect to https ('$loc')" ;; esac

# the version on the site is the latest GitHub release
latest=$(curl -s https://api.github.com/repos/mikephung/MiKey/releases/latest | python3 -c "import json,sys; print(json.load(sys.stdin).get('tag_name',''))")
[ "$latest" = "v$VER" ] && ok "site version v$VER == latest release" || bad "site says v$VER, latest release is $latest"

[ $fail = 0 ] && echo "live site: all checks pass" || echo "live site: some checks FAILED"
exit $fail
