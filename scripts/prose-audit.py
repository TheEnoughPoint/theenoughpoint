#!/usr/bin/env python3
"""
prose-audit.py -- the density gate for article prose.

Why this exists: the gold-routes piece (ways-to-own-gold-singapore, published
2026-08-07) passed the build, check_page.py and the render audit, and still
came back from its first outside readers as "too technical, too dense". None
of the existing checks measure the thing they were reacting to, which turned
out to be sentence and paragraph load, not the number count: the piece carried
FEWER numbers per thousand words (33) than the rising-rates piece (44) that
the same readers took happily. The difference sat in architecture -- median
sentence 20 words against 16, a quarter of sentences over 30 words against a
sixth, average paragraph 83 words against 64, and zero plain-English
translation lines against four.

Calibration doctrine: thresholds are set from the worked pair, not from a
readability formula. rates-rising-market-about-to-crash.mdx must PASS --
it is the engagement standard's worked example and holds full rigour at
these levels.
ways-to-own-gold-singapore.mdx (pre-retrofit) must FAIL -- it is the escape
that created this gate. If you loosen or tighten a threshold, re-run with
--all and say in the PR which articles changed side and why that is right.

Scope: new or materially rewritten articles, run from preflight Part 3 (first,
since it needs no build). The back catalogue is not expected to pass and the
gate is not run against it wholesale, except informationally via --all.

Measurement notes, learned calibrating:
- Markdown list items and table rows must not be fused into "sentences" --
  the first sweep reported 147-word sentences that were bullet lists. Each
  list item is its own unit; table and heading lines are excluded.
- Semicolon chains are deliberately ONE sentence. An 83-word semicolon chain
  is the offence, not a splitting artefact.
- <details> folds are excluded on purpose: folds are opt-in depth, and the
  gate measures the main reading path. Moving method-talk into folds is the
  approved fix, so the gate must not chase it there.

Usage:
    python scripts/prose-audit.py src/content/blog/<slug>.mdx [more.mdx ...]
    python scripts/prose-audit.py --all          # informational sweep, exit 0

Exit 1 if any named file FAILs. Warnings never block; they need a judgement.
"""

import glob
import os
import re
import statistics
import sys

# ---- thresholds (see calibration doctrine above) --------------------------
FAIL_MEDIAN_SENTENCE = 18   # rising-rates 16 | gold pre-retrofit 20
FAIL_PCT_OVER_30W = 20.0    # rising-rates 17% | gold 27%
FAIL_MAX_SENTENCE = 65      # rising-rates 56 | gold 83
FAIL_AVG_PARA = 75          # rising-rates 64 | gold 83
WARN_PLAIN_EN_PER_1000W = 1  # expect >= floor(words/1000) plain-English lines
WARN_TAKEAWAY_WORDS = 35    # rising-rates max 32 | gold carries 37, 47, 48

MIN_BODY_WORDS = 700  # below this the piece is a stub; metrics are noise

ABBREV = re.compile(
    r"\b(vs|e\.g|i\.e|etc|cf|Mr|Mrs|Ms|Dr|No|St"
    r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.$"
)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
PLAIN_EN = re.compile(r"\bIn plain (?:English|terms)\b")

WORD = re.compile(r"[\w'’$%]+")


def words_in(text):
    return len(WORD.findall(text))


def parse_frontmatter_takeaways(raw):
    m = re.match(r"^---\n(.*?)\n---", raw, re.S)
    if not m:
        return []
    takeaways, current, in_block = [], None, False
    for line in m.group(1).splitlines():
        if re.match(r"^takeaways:\s*$", line):
            in_block = True
            continue
        if in_block:
            if re.match(r"^\s*-\s+", line):
                if current is not None:
                    takeaways.append(current)
                current = re.sub(r"^\s*-\s+", "", line)
            elif re.match(r"^\s+\S", line) and current is not None:
                current += " " + line.strip()
            else:
                if current is not None:
                    takeaways.append(current)
                current = None
                in_block = False
    if current is not None:
        takeaways.append(current)
    return [re.sub(r"<[^>]+>", "", t).strip().strip('"') for t in takeaways]


def body_units(raw):
    """Return (paragraph_units, plain_en_count). A unit is a prose paragraph
    or a single list item; tables, headings, folds and components are gone."""
    t = re.sub(r"^---\n.*?\n---", "", raw, count=1, flags=re.S)
    t = re.sub(r"^import .*$", "", t, flags=re.M)
    t = re.sub(r"<details.*?</details>", "", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    plain_en = len(PLAIN_EN.findall(t))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("**", "").replace("*", "")

    units = []
    for block in re.split(r"\n\s*\n", t):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        if any(ln.lstrip().startswith(("|", "#")) for ln in lines):
            continue
        if any(LIST_ITEM.match(ln) for ln in lines):
            item = None
            for ln in lines:
                if LIST_ITEM.match(ln):
                    if item:
                        units.append(item)
                    item = LIST_ITEM.sub("", ln).strip()
                elif item is not None:
                    item += " " + ln.strip()
            if item:
                units.append(item)
        else:
            units.append(" ".join(ln.strip() for ln in lines))
    units = [u for u in units if words_in(u) >= 8]
    return units, plain_en


def sentences_of(unit):
    parts = re.split(r"(?<=[.!?])[\"')”]?\s+(?=[A-Z\"“(])", unit)
    sents = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if sents and ABBREV.search(sents[-1]):
            sents[-1] += " " + p
        else:
            sents.append(p)
    return sents


def audit(path):
    raw = open(path, encoding="utf-8").read()
    units, plain_en = body_units(raw)
    takeaways = parse_frontmatter_takeaways(raw)

    sents = [s for u in units for s in sentences_of(u)]
    slens = [words_in(s) for s in sents]
    plens = [words_in(u) for u in units]
    wc = sum(plens)

    failures, warnings = [], []
    if wc < MIN_BODY_WORDS:
        return {
            "path": path, "words": wc, "failures": [], "warnings": [
                f"only {wc} body words -- below the {MIN_BODY_WORDS}-word floor, metrics not meaningful"],
            "measured": {}, "skipped": True,
        }

    med = statistics.median(slens)
    pct30 = 100.0 * sum(1 for x in slens if x > 30) / len(slens)
    mx = max(slens)
    avgp = statistics.mean(plens)
    worst_sentence = max(sents, key=words_in)
    worst_para = max(units, key=words_in)

    if med > FAIL_MEDIAN_SENTENCE:
        failures.append(
            f"median sentence {med:.0f}w (limit {FAIL_MEDIAN_SENTENCE}) -- the piece reads long everywhere, not in spots")
    if pct30 > FAIL_PCT_OVER_30W:
        failures.append(
            f"{pct30:.0f}% of sentences over 30 words (limit {FAIL_PCT_OVER_30W:.0f}%)")
    if mx > FAIL_MAX_SENTENCE:
        failures.append(
            f"longest sentence {mx}w (limit {FAIL_MAX_SENTENCE}): \"{worst_sentence[:110]}...\"")
    if avgp > FAIL_AVG_PARA:
        failures.append(
            f"average paragraph {avgp:.0f}w (limit {FAIL_AVG_PARA}); longest {words_in(worst_para)}w: \"{worst_para[:90]}...\"")

    expected_pe = max(0, int(wc // 1000)) * WARN_PLAIN_EN_PER_1000W
    if plain_en < expected_pe:
        warnings.append(
            f"{plain_en} plain-English line(s) for {wc} body words (expect ~{expected_pe}). "
            "One human translation per mechanism -- VOICE.md C7.")
    for t in takeaways:
        n = len(t.split())
        if n > WARN_TAKEAWAY_WORDS:
            warnings.append(
                f"takeaway runs {n}w (aim under {WARN_TAKEAWAY_WORDS}; one number per line): \"{t[:80]}...\"")

    return {
        "path": path, "words": wc, "failures": failures, "warnings": warnings,
        "measured": {
            "body_words": wc, "sentences": len(sents),
            "median_sentence_w": round(med, 1),
            "pct_sentences_over_30w": round(pct30, 1),
            "max_sentence_w": mx,
            "avg_paragraph_w": round(avgp, 1),
            "max_paragraph_w": words_in(worst_para),
            "plain_english_lines": plain_en,
        },
        "skipped": False,
    }


def report(r):
    name = os.path.basename(r["path"])
    verdict = "SKIP" if r.get("skipped") else ("FAIL" if r["failures"] else "PASS")
    print(f"\n{verdict}  {name}")
    if r["measured"]:
        m = r["measured"]
        print(f"      {m['body_words']}w body | median sentence {m['median_sentence_w']}w | "
              f"{m['pct_sentences_over_30w']}% over 30w | max {m['max_sentence_w']}w | "
              f"avg para {m['avg_paragraph_w']}w | plain-English x{m['plain_english_lines']}")
    for f in r["failures"]:
        print(f"      FAIL: {f}")
    for w in r["warnings"]:
        print(f"      warn: {w}")
    return verdict


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    if not argv:
        print(__doc__)
        return 2
    if argv == ["--all"]:
        paths = sorted(glob.glob("src/content/blog/*.mdx"))
        print("Informational sweep -- the back catalogue is not expected to pass; exit 0.")
        for p in paths:
            report(audit(p))
        return 0
    bad = False
    for p in argv:
        r = audit(p)
        if report(r) == "FAIL":
            bad = True
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
