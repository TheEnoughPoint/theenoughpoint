#!/usr/bin/env python3
"""Catch words glued together across an inline tag boundary.

Astro and JSX collapse the newline between an inline tag and the next line, so

    <b>Cash in T-bills</b>
    gives it the actual rate

renders as "Cash in T-billsgives it the actual rate". The source reads correctly,
the build succeeds, and only the rendered text is wrong -- which is why this runs
against the BUILT html rather than the components.

Usage
    npm run build
    python scripts/check_inline_spacing.py                 # all of dist/
    python scripts/check_inline_spacing.py dist/foo/index.html

Exit code is 1 only when a HIGH finding exists, so a build fails on something a
reader would actually see, not on the lower-severity class below.

Severity
    HIGH  both sides render inline, so the words are visibly joined on screen.
    LOW   the second element is block, a flex/grid item, or carries a horizontal
          margin -- the reader sees a normal gap, but the text stream is still
          joined for screen readers and for anyone copying the text out.

Fix by making the space explicit rather than relying on a newline:

    <b>Cash in T-bills</b>{' '}
    gives it the actual rate
"""

from __future__ import annotations

import io
import re
import sys
from collections import defaultdict
from pathlib import Path

# Article text contains arrows, dashes and curly quotes. On a Windows console the
# default codepage cannot encode them and the script dies mid-report, which is a
# poor first experience for anyone running it. Force UTF-8 output.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

INLINE = r"(?:b|strong|em|i|code|span|a)"

# Text running straight out of a closed inline element.
AFTER_CLOSE = re.compile(rf"([A-Za-z0-9%)])</({INLINE})>([a-zA-Z])")
# Text running straight into an opening inline element. The tag name must end at a
# space or '>', otherwise `<br>` parses as `<b` with an attribute `r` and every line
# break inside a table header is reported as a defect.
BEFORE_OPEN = re.compile(rf"([a-z0-9])<({INLINE})(\s[^>]*)?>([A-Za-z])")

BLOCKISH = {"block", "flex", "grid", "list-item", "table", "table-cell"}
BLOCKIFYING_PARENT = {"flex", "grid", "inline-flex", "inline-grid"}


def load_css() -> str:
    """Every stylesheet, including the ones Astro inlines into the page.

    Small component styles are emitted inside a <style> block rather than a .css
    file. Reading only *.css meant those rules were invisible, so a correctly
    block-styled element was reported as inline -- the last of several false
    positives this checker produced before it was trustworthy.
    """
    parts = [p.read_text(encoding="utf-8", errors="replace")
             for p in DIST.rglob("*.css")]
    for page in DIST.rglob("index.html"):
        html = page.read_text(encoding="utf-8", errors="replace")
        parts.extend(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S))
    return "\n".join(parts)


def rules_for(css: str, cls: str):
    return [m.group(1) for m in
            re.finditer(rf"\.{re.escape(cls)}\b[^{{]*\{{([^}}]*)\}}", css)]


def display_of(css: str, cls: str):
    for body in rules_for(css, cls):
        m = re.search(r"display\s*:\s*([a-z-]+)", body)
        if m:
            return m.group(1)
    return None


def has_side_margin(css: str, cls: str) -> bool:
    return any(re.search(r"margin(-left|-right)?\s*:\s*[^;}]*\d", b)
               for b in rules_for(css, cls))


def nearest_blockifying_parent(css: str, html: str, pos: int):
    head = html[max(0, pos - 900):pos]
    for attr in reversed(re.findall(r'class="([^"]*)"', head)):
        for c in attr.split():
            d = display_of(css, c)
            if d in BLOCKIFYING_PARENT:
                return c, d
    return None, None


def descendant_block_rules(css: str):
    """Rules of the form `.some-class em { display:block }`.

    Without this the checker only sees an element's OWN class and calls every
    descendant-styled tag inline. That produced 13 confident false positives -- an
    <b> that a stylesheet had made display:block, reported as visibly glued text --
    and very nearly caused edits to articles that were never broken.
    """
    out = defaultdict(set)
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        body = m.group(2)
        d = re.search(r"display\s*:\s*([a-z-]+)", body)
        if not d or d.group(1) not in BLOCKISH:
            continue
        for sel in m.group(1).split(","):
            sel = sel.strip()
            parts = sel.split()
            if len(parts) < 2:
                continue
            # Astro scopes component styles by appending an attribute selector, so
            # the built CSS reads `.ds-h-pct em[data-astro-cid-abc]`. Strip attribute
            # and pseudo selectors before matching the tag name, or every scoped
            # component rule is silently ignored and its elements look inline.
            tag = re.sub(r"[\[:].*$", "", parts[-1]).strip()
            if not re.fullmatch(INLINE, tag):
                continue
            for anc in parts[:-1]:
                for c in re.findall(r"\.([A-Za-z0-9_-]+)", anc):
                    out[tag].add(c)
    return out


def styled_block_by_ancestor(rules, html: str, pos: int, tag: str):
    """Is this tag made block by a `.ancestor tag` rule that actually applies here?"""
    wanted = rules.get(tag)
    if not wanted:
        return None
    head = html[max(0, pos - 900):pos]
    for attr in reversed(re.findall(r'class="([^"]*)"', head)):
        for c in attr.split():
            if c in wanted:
                return c
    return None


def scan(path: Path, css: str, desc_rules=None):
    desc_rules = desc_rules if desc_rules is not None else descendant_block_rules(css)
    html = path.read_text(encoding="utf-8", errors="replace")
    html = re.sub(r"<(script|style|pre).*?</\1>", " ", html, flags=re.S)
    findings = []

    def context(m):
        raw = html[max(0, m.start() - 45):m.end() + 35]
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw)).strip()

    for m in AFTER_CLOSE.finditer(html):
        tag = m.group(2)
        anc = styled_block_by_ancestor(desc_rules, html, m.start(), tag)
        if anc:
            findings.append(("LOW", f"<{tag}> is display:block via .{anc} {tag}", context(m)))
        else:
            findings.append(("HIGH", f"text runs straight out of </{tag}>", context(m)))

    for m in BEFORE_OPEN.finditer(html):
        tag = m.group(2)
        attrs = m.group(3) or ""
        cm = re.search(r'class="([^"]*)"', attrs)
        cls = cm.group(1).split() if cm else []
        own = next((d for d in (display_of(css, c) for c in cls) if d), None)
        pcls, pdisp = nearest_blockifying_parent(css, html, m.start())
        if own in BLOCKISH:
            findings.append(("LOW", f"<{tag}> is display:{own}", context(m)))
        elif any(has_side_margin(css, c) for c in cls):
            findings.append(("LOW", f"<{tag}> gap is faked by a horizontal margin", context(m)))
        elif pdisp:
            findings.append(("LOW", f"<{tag}> is a child of .{pcls} (display:{pdisp})", context(m)))
        elif (anc := styled_block_by_ancestor(desc_rules, html, m.start(), tag)):
            findings.append(("LOW", f"<{tag}> is display:block via .{anc} {tag}", context(m)))
        else:
            findings.append(("HIGH", f"<{tag}> renders inline", context(m)))
    return findings


def main() -> int:
    if not DIST.exists():
        print("dist/ not found -- run `npm run build` first.")
        return 1
    css = load_css()
    desc_rules = descendant_block_rules(css)
    targets = ([Path(a) for a in sys.argv[1:]] or sorted(DIST.rglob("index.html")))

    buckets = defaultdict(list)
    for p in targets:
        for sev, why, ctx in scan(p, css, desc_rules):
            name = p.parent.name or "home"
            buckets[sev].append((name, why, ctx))

    for sev in ("HIGH", "LOW"):
        items = buckets.get(sev, [])
        if not items:
            continue
        print(f"\n{sev} — {len(items)}")
        grouped = defaultdict(list)
        for name, why, ctx in items:
            grouped[why].append((name, ctx))
        for why, hits in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
            pages = sorted({n for n, _ in hits})
            print(f"  [{len(hits):>2}] {why}")
            print(f"       pages: {', '.join(pages[:5])}{' …' if len(pages) > 5 else ''}")
            print(f"       e.g.   ...{hits[0][1]}...")

    high, low = len(buckets['HIGH']), len(buckets['LOW'])
    print(f"\n--> {high} HIGH, {low} LOW across {len(targets)} page(s)")
    if high:
        print("    HIGH findings are visible to readers. Add an explicit {' '} "
              "between the tag and the text.")
    return 1 if high else 0


if __name__ == "__main__":
    raise SystemExit(main())
