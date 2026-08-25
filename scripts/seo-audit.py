"""seo-audit.py — the head of every built page, checked against itself and the sitemap.

Run from the repo root after a build:

    python scripts/seo-audit.py

Exit code 0 means clean; 1 means something below needs a human; 2 means no dist/.
It also runs in CI (.github/workflows/deploy.yml) between build and deploy, so a
red run keeps the previous version of the site live rather than shipping the defect.

WHY THIS EXISTS
Google decides which duplicate URL represents a page from a bundle of signals —
redirects, sitemap membership and rel=canonical among them. Those signals only
help if they agree: a canonical on the apex with a sitemap entry on www, or a
trailing-slash form the built page does not use, is the site arguing with
itself. No check enforced that agreement, and nothing at all checked meta
descriptions, alt text or the structured data (MainLayout falls back to the
theme's demo title and description when a page forgets to pass its own — a
defect only a uniqueness check catches).

WHAT IT CHECKS — failures
1. Title: present, not the theme default, unique across the site.
2. Meta description: present, not the theme default, unique across the site.
3. Canonical: exactly one; absolute https on the apex host; no query or
   fragment; equal to the URL the page is actually built at; og:url agrees.
4. Sitemap: exists; every indexable page's canonical is in it, in the same
   form; every sitemap URL corresponds to a built page. A near-miss that
   differs only by host or trailing slash is named as a form mismatch.
5. Images: every <img> carries an alt attribute, and no alt is a filename.
6. Structured data: every ld+json block parses; article pages carry a valid
   BlogPosting (headline, ISO dates in order, author, publisher with logo,
   image, mainEntityOfPage matching the canonical) and a BreadcrumbList whose
   positions are contiguous and whose internal URLs resolve to built pages;
   the homepage carries WebSite and Organization (name, url, logo).

WHAT IT PRINTS AS ADVISORY — never fails
7. Titles past 60 characters (search results truncate near there).
8. Article descriptions outside 70–320 characters. Articles only, and a wide
   band: the first run flagged 91 of 107 pages with a textbook 70–160 band,
   because this site's excerpts are editorial standfirsts by choice and its
   archive pages are thin by design. A check that flags a healthy site is
   miscalibrated, not strict.
9. Images with alt="" (legitimate for decorative images — the header logo
   carries alt="" correctly, because the wordmark text beside it names the
   link). Aggregated by image, since one decorative logo on every page is one
   fact, not two hundred.
10. Pairs of article titles whose meaningful words largely overlap — possible
    keyword cannibalisation. Two pieces competing for one query split its
    ranking; only a human knows whether the pieces target different intents,
    so the list is printed for judgement, not failed.

CALIBRATION DOCTRINE
Verify a new check against the site before trusting it — the render audit
shipped three false-positive classes on its first run, and a checker that
cries wolf gets ignored. On the day this file was written the whole catalogue
passed at 0 failures; treat a failure as signal.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit

DIST = Path(__file__).resolve().parent.parent / "dist"
SITE = "https://theenoughpoint.com"
CANONICAL_HOST = "theenoughpoint.com"  # apex, matching link-sweep.py

# The layout's fallbacks. A page rendering either forgot to pass its own.
THEME_TITLE = "Portal - Astro News Magazine Theme"
THEME_DESC_PREFIX = "Portal is a Astro news magazine theme"

TITLE_MAX = 60          # search snippets truncate near 60 characters
DESC_RANGE = (70, 320)  # articles only; wide by calibration (see docstring)

# Alt text that is a filename or a non-description names nothing for a
# screen-reader user or an image index. Case-insensitive.
BAD_ALT = re.compile(
    r"\.(jpe?g|png|webp|svg|gif|avif)$|^(img|dsc)[_\-]?\d|^(image|photo|picture|cover|graphic|icon|untitled)$",
    re.I)

# Words carrying no query intent, stripped before comparing titles. The site
# terms (singapore, sg) are here because sharing them is the catalogue's
# premise, not an overlap.
STOP = set("""a an and are at by for from how in is it its of on or s t the to
versus vs what when which who why with you your we our their before after
singapore sg""".split())

title_re = re.compile(r"<title>(.*?)</title>", re.S)
desc_re = re.compile(r'<meta name="description" content="([^"]*)"')
canon_re = re.compile(r'<link rel="canonical" href="([^"]*)"')
ogurl_re = re.compile(r'<meta property="og:url" content="([^"]*)"')
ogtype_re = re.compile(r'<meta property="og:type" content="([^"]*)"')
robots_re = re.compile(r'<meta name="robots" content="([^"]*)"')
img_re = re.compile(r"<img\b[^>]*>", re.S)
alt_re = re.compile(r'\balt="([^"]*)"')
ld_re = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
h1_re = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)


def unescape(s):
    return (s.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
            .replace("&lt;", "<").replace("&gt;", ">"))


def page_url(page):
    """The URL a dist file is actually served at, in canonical form."""
    rel = page.relative_to(DIST).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[: -len("index.html")]
    return SITE + "/" + rel  # top-level *.html such as 404.html


def parse_iso(s):
    """ISO-8601 via the datetime library — never parsed by hand."""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def ld_nodes(block):
    """Every schema node in a parsed ld+json payload: bare dict, array, or @graph."""
    items = block if isinstance(block, list) else [block]
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append(it)
            graph = it.get("@graph")
            if isinstance(graph, list):
                out.extend(n for n in graph if isinstance(n, dict))
    return out


def resolves(url):
    """Does an internal URL correspond to a built page or file?"""
    path = urlsplit(url).path.lstrip("/")
    cand = DIST / path if path else DIST
    return cand.exists() or (cand / "index.html").exists()


def title_tokens(t):
    return set(re.findall(r"[a-z0-9]+", t.lower())) - STOP


def audit():
    if not DIST.exists():
        print("dist/ not found — run `npm run build` first.")
        return 2
    pages = sorted(DIST.glob("**/index.html")) + [
        p for p in DIST.glob("*.html") if p.name != "index.html"]

    failures = {
        "titles missing or still the theme default": [],
        "duplicate titles": [],
        "descriptions missing or still the theme default": [],
        "duplicate descriptions": [],
        "canonical defects (count, host, scheme, query, self-reference)": [],
        "og:url disagreeing with canonical": [],
        "sitemap defects (missing pages, orphan entries, form mismatches)": [],
        "images without an alt attribute": [],
        "alt text that is a filename or placeholder": [],
        "structured data defects": [],
    }
    advisories = {
        "titles past %d characters" % TITLE_MAX: [],
        "article descriptions outside %d-%d characters" % DESC_RANGE: [],
        "images with empty alt (fine if decorative)": [],
        "possible keyword overlap between articles (judgement needed)": [],
    }

    seen_titles, seen_descs = {}, {}
    article_titles = {}
    empty_alt = {}  # src -> page count, aggregated for the advisory
    sitemap_urls = load_sitemap(failures)

    for page in pages:
        rel = str(page.relative_to(DIST))
        html = page.read_text(encoding="utf-8", errors="replace")
        url = page_url(page)
        is_404 = page.name == "404.html"
        is_home = url == SITE + "/"
        ogt = ogtype_re.search(html)
        is_article = bool(ogt and ogt.group(1) == "article")

        # ---- 1–2. title and description, presence then uniqueness ---------
        m = title_re.search(html)
        title = unescape(m.group(1).strip()) if m else ""
        if not title or title == THEME_TITLE:
            failures["titles missing or still the theme default"].append((rel, title or "(none)"))
        elif not is_404:
            if title in seen_titles:
                failures["duplicate titles"].append((rel, "same as " + seen_titles[title] + ": " + title[:70]))
            seen_titles.setdefault(title, rel)
            if len(title) > TITLE_MAX:
                advisories["titles past %d characters" % TITLE_MAX].append(
                    (rel, "%d chars: %s" % (len(title), title[:70])))

        m = desc_re.search(html)
        desc = unescape(m.group(1).strip()) if m else ""
        if not desc or desc.startswith(THEME_DESC_PREFIX):
            failures["descriptions missing or still the theme default"].append((rel, desc[:60] or "(none)"))
        elif not is_404:
            if desc in seen_descs:
                failures["duplicate descriptions"].append((rel, "same as " + seen_descs[desc] + ": " + desc[:60]))
            seen_descs.setdefault(desc, rel)
            lo, hi = DESC_RANGE
            if is_article and not lo <= len(desc) <= hi:
                advisories["article descriptions outside %d-%d characters" % DESC_RANGE].append(
                    (rel, "%d chars" % len(desc)))

        # ---- 3. canonical -------------------------------------------------
        canons = canon_re.findall(html)
        canon = canons[0] if canons else ""
        if len(canons) != 1:
            failures["canonical defects (count, host, scheme, query, self-reference)"].append(
                (rel, "%d canonical tags" % len(canons)))
        else:
            parts = urlsplit(canon)
            if parts.scheme != "https" or parts.netloc != CANONICAL_HOST:
                failures["canonical defects (count, host, scheme, query, self-reference)"].append(
                    (rel, "wrong scheme or host: " + canon[:80]))
            elif parts.query or parts.fragment:
                failures["canonical defects (count, host, scheme, query, self-reference)"].append(
                    (rel, "carries query or fragment: " + canon[:80]))
            elif canon != url and not is_404:
                failures["canonical defects (count, host, scheme, query, self-reference)"].append(
                    (rel, "canonical %s but page is built at %s" % (canon[:60], url[:60])))
            m = ogurl_re.search(html)
            if m and unescape(m.group(1)) != canon:
                failures["og:url disagreeing with canonical"].append((rel, unescape(m.group(1))[:80]))

        # ---- 4. sitemap membership ---------------------------------------
        robots = robots_re.search(html)
        noindex = bool(robots and "noindex" in robots.group(1))
        if sitemap_urls is not None and not is_404 and not noindex:
            if url not in sitemap_urls:
                near = [s for s in sitemap_urls
                        if s.rstrip("/") == url.rstrip("/")
                        or s.replace("//www.", "//") == url]
                why = ("form mismatch — sitemap has " + near[0][:60]) if near else "absent from sitemap"
                failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append((rel, why))

        # ---- 5. images ----------------------------------------------------
        for tag in img_re.findall(html):
            am = alt_re.search(tag)
            src = re.search(r'\bsrc="([^"]*)"', tag)
            label = (src.group(1)[-60:] if src else tag[:60])
            if not am:
                failures["images without an alt attribute"].append((rel, label))
            elif not am.group(1).strip():
                empty_alt[label] = empty_alt.get(label, 0) + 1
            elif BAD_ALT.search(unescape(am.group(1)).strip()):
                failures["alt text that is a filename or placeholder"].append(
                    (rel, unescape(am.group(1))[:60]))

        # ---- 6. structured data ------------------------------------------
        nodes = []
        for raw in ld_re.findall(html):
            try:
                nodes.extend(ld_nodes(json.loads(unescape_ld(raw))))
            except json.JSONDecodeError as e:
                failures["structured data defects"].append((rel, "ld+json does not parse: " + str(e)[:60]))
        types = {n.get("@type") for n in nodes}

        if is_article:
            check_article_schema(rel, canon, nodes, types, failures)
            if title:
                article_titles[rel] = title
        if is_home:
            if "WebSite" not in types:
                failures["structured data defects"].append((rel, "homepage missing WebSite schema"))
            org = next((n for n in nodes if n.get("@type") == "Organization"), None)
            if not org:
                failures["structured data defects"].append((rel, "homepage missing Organization schema"))
            elif not (org.get("name") and org.get("url") and org.get("logo")):
                failures["structured data defects"].append((rel, "Organization missing name, url or logo"))

    # ---- 4b. every sitemap entry must be a built page ---------------------
    if sitemap_urls is not None:
        for s in sorted(sitemap_urls):
            if not s.startswith(SITE + "/") and s != SITE + "/":
                failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append(
                    ("(sitemap)", "off-host entry: " + s[:80]))
            elif not resolves(s):
                failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append(
                    ("(sitemap)", "entry with no built page: " + s[:80]))

    # ---- 9. empty-alt aggregation ----------------------------------------
    for src, n in sorted(empty_alt.items(), key=lambda kv: -kv[1]):
        advisories["images with empty alt (fine if decorative)"].append(
            (src, "on %d page(s)" % n))

    # ---- 10. cannibalisation advisory ------------------------------------
    for (ra, ta), (rb, tb) in combinations(sorted(article_titles.items()), 2):
        a, b = title_tokens(ta), title_tokens(tb)
        if not a or not b:
            continue
        shared = a & b
        if len(shared) >= 3 and len(shared) / len(a | b) >= 0.5:
            advisories["possible keyword overlap between articles (judgement needed)"].append(
                (ra + " vs " + rb, "share: " + ", ".join(sorted(shared))))

    # ---- report -----------------------------------------------------------
    failed = False
    for name, items in failures.items():
        print("== %s: %d" % (name, len(items)))
        for it in items[:15]:
            print("   ", it)
        failed = failed or bool(items)
    print("-- advisories (never fail the run) --")
    for name, items in advisories.items():
        print("== %s: %d" % (name, len(items)))
        for it in items[:15]:
            print("   ", it)

    print("\nCLEAN." if not failed else "\nISSUES FOUND — see above.")
    return 1 if failed else 0


def unescape_ld(raw):
    """Astro's set:html leaves JSON intact; only stray &amp; needs undoing."""
    return raw.replace("&amp;", "&")


def check_article_schema(rel, canon, nodes, types, failures):
    fail = failures["structured data defects"]
    post = next((n for n in nodes if n.get("@type") in ("BlogPosting", "Article", "NewsArticle")), None)
    if not post:
        fail.append((rel, "article page missing BlogPosting schema"))
    else:
        for field in ("headline", "image"):
            if not post.get(field):
                fail.append((rel, "BlogPosting missing " + field))
        pub = parse_iso(post.get("datePublished", ""))
        if not pub:
            fail.append((rel, "datePublished not ISO-8601: " + str(post.get("datePublished"))[:40]))
        mod = parse_iso(post.get("dateModified", "")) if post.get("dateModified") else None
        if pub and mod and mod < pub:
            fail.append((rel, "dateModified earlier than datePublished"))
        if not (post.get("author") or {}).get("name"):
            fail.append((rel, "BlogPosting missing author.name"))
        publisher = post.get("publisher") or {}
        if not (publisher.get("name") and (publisher.get("logo") or {}).get("url")):
            fail.append((rel, "publisher missing name or logo"))
        meop = post.get("mainEntityOfPage") or {}
        if canon and meop.get("@id") != canon:
            fail.append((rel, "mainEntityOfPage is not the canonical URL"))

    crumbs = next((n for n in nodes if n.get("@type") == "BreadcrumbList"), None)
    if not crumbs:
        fail.append((rel, "article page missing BreadcrumbList schema"))
    else:
        items = crumbs.get("itemListElement") or []
        positions = [c.get("position") for c in items]
        if positions != list(range(1, len(items) + 1)):
            fail.append((rel, "breadcrumb positions not contiguous from 1: " + str(positions)))
        for c in items:
            item = c.get("item")
            if isinstance(item, str) and item.startswith(SITE) and not resolves(item):
                fail.append((rel, "breadcrumb points at an unbuilt page: " + item[:70]))


def load_sitemap(failures):
    """Every <loc> across the sitemap index and its children, or None if absent."""
    index = DIST / "sitemap-index.xml"
    plain = DIST / "sitemap.xml"
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sources = []
    if index.exists():
        try:
            root = ET.parse(index).getroot()
        except ET.ParseError as e:
            failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append(
                ("(sitemap)", "sitemap-index.xml does not parse: " + str(e)[:60]))
            return set()
        for loc in root.findall(".//sm:loc", ns):
            child = DIST / urlsplit(loc.text.strip()).path.lstrip("/")
            if child.exists():
                sources.append(child)
            else:
                failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append(
                    ("(sitemap)", "index lists a child that was not built: " + loc.text.strip()[:70]))
    elif plain.exists():
        sources.append(plain)
    else:
        failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append(
            ("(sitemap)", "no sitemap-index.xml or sitemap.xml in dist/"))
        return None

    urls = set()
    for src in sources:
        try:
            root = ET.parse(src).getroot()
        except ET.ParseError as e:
            failures["sitemap defects (missing pages, orphan entries, form mismatches)"].append(
                ("(sitemap)", src.name + " does not parse: " + str(e)[:60]))
            continue
        urls.update(loc.text.strip() for loc in root.findall(".//sm:loc", ns) if loc.text)
    return urls


if __name__ == "__main__":
    sys.exit(audit())
