"""Generate SameMoneySize.astro — every qualifying building, with the stock ceiling drawn.

Rows are derived here from live.json rather than a checked-in extract, and the feed is loaded
through feed_guard so a run that did not actually fetch cannot be frozen into a published figure.
"""
import io, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feed_guard import load_live, rows_for_compare

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.environ.get('LIVE_JSON', r'C:/dev/sg-property-decision/data/live.json')
BUDGET_PY, NEW_PSF_PY = 2_400_000, 2900
BASE_PY = round(BUDGET_PY / NEW_PSF_PY)

data, provenance = load_live(LIVE, ['projects', 'districts'])
_sz = {x['project'].title(): x['size_r'] for x in data['projects']['rows']}
rows = []
for r in rows_for_compare(data):
    if r['d'] != 'D20' or r['m'] > 400:
        continue
    sq = round(BUDGET_PY / r['psf'])
    p90 = _sz[r['p']][1]
    rows.append(dict(p=r['p'], psf=r['psf'], n=r['v'], l=('FH' if r['fh'] else r['lyr']),
                     m=r['m'], x=r['x'], sq=sq, p90=p90, above=sq > p90,
                     pct=round((sq / BASE_PY - 1) * 100)))
rows.sort(key=lambda x: x['sq'])
DATA = json.dumps(rows, separators=(',', ':'), ensure_ascii=False)

TPL = '''---
// DATA PROVENANCE: __PROVENANCE__
// Regenerate with scripts/gen_samemoney.py — never edit this file by hand.
// Hold the budget still and let the size move.
//
// The article's problem is that a percentage entry gap ("new build costs 34% more per square
// foot") is a number nobody can feel. This figure restates the identical fact in the unit a buyer
// lives in: one fixed sum, and the floor area it buys in each building.
//
// EVERY QUALIFYING BUILDING IS HERE AND NOTHING IS CAPPED. Two earlier versions got this wrong in
// opposite directions: the first dropped four buildings where the budget bought more space than
// they usually sell, then explained the absence in a note longer than the chart; the second capped
// their bars at the 90th percentile of traded sizes and called it "their biggest", which claimed
// more than the data supports and answered a question nobody asked.
//
// The cap conflated two different things — what the money buys at a building's rate, and whether a
// home that size is available. The bar answers the first, which is the comparison the figure
// exists to make. The second is a caveat, and it is now stated as one: rows where the implied size
// sits above the 90th percentile of what trades there carry a "!" and the footer gives both
// reasons to read them as optimistic, the second of which the cap never captured — a building's
// median rate is set by the sizes it sells, and larger homes almost always trade at a lower rate
// per square foot than smaller ones in the same block, so the implied size is doubly generous.
//
// ROWS is emitted mechanically from data/live.json in the sg-property-decision repo (URA
// PMI_Resi_Transaction resale medians, twelve months to August 2026; nearest MRT from LTA exits).
// Floor areas, percentages, the baseline and the spread are recomputed from BUDGET and ROWS below,
// so no figure in the prose can drift from a bar.
//
// COLOUR CARRIES NO VERDICT (VOICE.md C10). Every bar measures the same quantity — square feet —
// so this is a ONE-SERIES chart and takes one hue for every bar, which is the documented treatment:
// slot 1, #2a78d6, validated at 4.4:1 on white. It replaces a near-black slate that turned nine
// stacked rows into a wall and left the two states almost indistinguishable.
//
// The states are pattern, never a second hue:
//   solid bar      floor area the budget buys there
//   upright mark   the p90 of sizes that actually trade there, named as such in the legend:
//                  "biggest size that usually trades" reads as a maximum, which p90 is not. Replaced a hatched bar, which was
//                  the loudest mark in the chart while carrying a footnote, lowered the apparent
//                  ink of the longest bars so the encoding fought itself, and could not show HOW
//                  far past the ceiling a bar ran, because a texture has no position.
//   (was)          white-striped: the same, where the size sits above what usually trades — not
//                  worse, so it is the SAME blue interrupted rather than a different colour
//   dashed outline the building that does not exist yet
//
// White stripes, not dark ones: on a near-black bar the old hatch was invisible at a glance, which
// defeated the point of marking it at all. The baseline row was worse — a cream hatch on white,
// the most important reference on the chart and the least visible thing on it. It now carries a
// pale tint of the same blue inside a dashed border of the full strength.
//
// More space is not "better" here; it is the trade, and the lease and the walk in the same row are
// what it is traded against — Braddell View offers the most floor area and has 54 years left
// against the baseline's fresh 99.
//
// Two filters, both mechanical and both stated on the figure: within 400 m of an MRT entrance, and
// at least 10 resales in the twelve months so a median is not one odd unit. Nothing else is
// excluded — the third filter that used to drop rows is now drawn instead.
const ASOF = 'August 2026';
const BUDGET = 2_400_000;
const NEW_PSF = 2900; // the middle of the illustrative band the article derives; NOT a quote

interface Row { p: string; psf: number; n: number; l: number | string; m: number; x: string;
  sq: number; p90: number; above: boolean; pct: number }

const ROWS: Row[] = __DATA__;

const BASE = Math.round(BUDGET / NEW_PSF);
const MAX = Math.max(BASE, ...ROWS.map((r) => Math.max(r.sq, r.p90)));
const w = (v: number) => (v / MAX) * 100;
const ABOVE = ROWS.filter((r) => r.above);
const MIN_PCT = Math.min(...ROWS.map((r) => r.pct));
const MAX_PCT = Math.max(...ROWS.map((r) => r.pct));
// The threshold is a knife edge for some of these. Naming the narrowest crossing keeps the count
// from implying four equally stretched cases.
const NARROW = ABOVE.filter((r) => (r.sq - r.p90) / r.p90 < 0.03);
const WIDEST = ABOVE.reduce((a, b) => (b.sq - b.p90 > a.sq - a.p90 ? b : a));
const n = (v: number) => v.toLocaleString('en-SG');
const money = (v: number) => `S$${(v / 1_000_000).toFixed(1)}m`;
---

<figure class="sm">
  <figcaption class="sm-cap">
    <h4>What {money(BUDGET)} buys, building by building</h4>
    <p>The same sum spent at each building&rsquo;s own median resale price per square foot, District 20,
    twelve months to {ASOF}. The top row is that sum at S${n(NEW_PSF)} per square foot &mdash; an
    illustrative new-build price, not a quote from anyone.</p>
  </figcaption>

  <div class="sm-legend">
    <span class="sm-lg"><i class="sm-key sm-key-old"></i>floor area {money(BUDGET)} buys there</span>
    <span class="sm-lg"><i class="sm-key sm-key-p90"></i>nine in ten sales are smaller (90th percentile)</span>
    <span class="sm-lg"><i class="sm-key sm-key-new"></i>not built yet</span>
  </div>

  <div class="sm-head">
    <span>Building</span>
    <span class="sm-h-bar">Floor area {money(BUDGET)} buys</span>
    <span class="sm-h-val">sq ft</span>
    <span class="sm-h-pct">vs new</span>
  </div>

  <ol class="sm-rows">
    <li class="sm-row sm-row-base">
      <span class="sm-name"><b>Thomson Reserve</b>
        <span class="sm-nm">not built &middot; at S${n(NEW_PSF)} psf, our illustration</span>
        <span class="sm-nm-s">our illustrative price</span></span>
      <span class="sm-track">
        <span class="sm-bar sm-bar-new" style={`width:${w(BASE)}%`}
          role="img"
          aria-label={`Thomson Reserve, not built yet, at an illustrative S$${n(NEW_PSF)} per square foot. ${n(BASE)} square feet for ${money(BUDGET)}.`}></span>
      </span>
      <span class="sm-val">{n(BASE)}</span>
      <span class="sm-pct sm-pct-base">&mdash;</span>
    </li>

    {ROWS.map((r) => (
      <li class="sm-row">
        <span class="sm-name"><b>{r.p}</b>
          <span class="sm-nm">{r.l} yrs lease &middot; {r.m}m to {r.x} &middot; {r.n} resales</span>
          <span class="sm-nm-s">{r.l} yrs &middot; {r.m}m</span></span>
        <span class="sm-track">
          <span class="sm-ghost" style={`width:${w(BASE)}%`} aria-hidden="true"></span>
          {/* The reference marker that replaced the hatch. A hatch has no position, so it could
              say "this is above what trades" but never how far above, and it degraded the one
              thing the bar is for — length. This sits at the p90 of traded sizes, so a bar that
              runs past it is visibly past it, and a bar short of it shows the headroom instead. */}
          <span class="sm-p90" style={`left:${w(r.p90)}%`} aria-hidden="true"></span>
          <span class="sm-bar sm-bar-old" style={`width:${w(r.sq)}%`}
            role="img"
            aria-label={`${r.p}. Median S$${n(r.psf)} per square foot over ${r.n} resales, ${r.l} years of lease remaining, ${r.m} metres to ${r.x} station. ${money(BUDGET)} buys ${n(r.sq)} square feet there, ${r.pct} per cent against the new-build baseline.${r.above ? ` That is above the size that usually trades there — nine in ten sales are under ${n(r.p90)} square feet — so treat it as optimistic.` : ` Nine in ten sales there are under ${n(r.p90)} square feet, so the budget stays inside the usual range.`}`}></span>
        </span>
        {/* The bar stops at what the building actually offers. An earlier version drew a ghosted
            stretch to the notional figure, which read as more bar rather than as absent space. */}
        <span class="sm-val">{n(r.sq)}{r.above && <i class="sm-cap-note">usually to {n(r.p90)}</i>}</span>
        <span class="sm-pct">{r.pct >= 0 ? '+' : '−'}{Math.abs(r.pct)}%</span>
      </li>
    ))}
  </ol>

  {/* An earlier version said all of this in one sentence carrying three separate ideas, and a
      reader stopped at it. One idea per sentence, with a worked example for the awkward case. */}
  <p class="sm-foot">Each bar is how much space {money(BUDGET)} buys at that building&rsquo;s own
  median price per square foot. Nothing is capped: if the money reaches a bigger home there, the bar
  shows it.</p>

  <p class="sm-foot sm-foot-2">The upright mark on each bar is the 90th percentile of sizes that
  actually trade in that building &mdash; nine in ten of its resales were smaller than that. It is not
  the largest unit there; it is where the top tenth begins. On {ABOVE.length} of them the bar
  runs <b>past</b> that mark, and how far past is the whole point &mdash; at <b>{WIDEST.p}</b> the
  budget implies {n(WIDEST.sq)} sq ft against a usual ceiling of {n(WIDEST.p90)}, while{' '}
  {NARROW.length > 0 ? <>at <b>{NARROW[0].p}</b> it clears the mark by {n(NARROW[0].sq - NARROW[0].p90)} sq
  ft, which is no gap at all</> : <>the rest clear it narrowly</>}. Read the wide ones as optimistic
  for two reasons. You may not find a home that size. And a building&rsquo;s
  median price per square foot is set by the sizes it actually sells, so applying a small-unit
  building&rsquo;s rate to a large notional home overstates the space: bigger homes almost always
  trade at a lower rate per square foot than smaller ones in the same block.</p>

  <p class="sm-foot sm-foot-2">Against <b>{n(BASE)} sq ft</b> in a building that does not exist yet,
  the range runs from {MIN_PCT < 0 ? `${Math.abs(MIN_PCT)}% less space` : `${MIN_PCT}% more`} to{' '}
  {MAX_PCT >= 100 ? 'more than double' : `${MAX_PCT}% more`}. The extra space is not money saved:
  part of what you pay for a new build is the building being new &mdash; a fresh 99-year lease, and
  nothing to repair for years. The lease column is where the biggest jumps show their price: the row
  with the most space has <b>{ROWS.find((r) => r.pct === MAX_PCT).l} years</b> left, against a fresh 99.</p>

  <p class="sm-src">Computed by us from URA private resale transactions, District 20, twelve months to{' '}
  {ASOF}; walking distances are straight-line to the nearest station entrance, so a real walk is
  typically 20&ndash;40% further. Two filters, applied mechanically: within 400 m of an MRT entrance,
  and at least 10 resales in the period so no median rests on one unusual unit &mdash; which is why
  some nearby blocks are absent: Sky Habitat, for one, recorded nine. Where a bar is capped, the
  ceiling is the <b>90th percentile of sizes that traded</b>, not the largest unit the building
  contains; the feed publishes what sold, not what exists. <b>A median mixes
  floor, stack, condition and renovation</b>, so no row is a price for any particular unit, and no
  row is a view on any building.</p>
</figure>

<style is:global>
.sm{
  --sm-ink:var(--color-dark); --sm-body:var(--color-body); --sm-muted:var(--color-muted);
  --sm-rule:var(--color-border);
  --sm-fill:#2a78d6;          /* one hue for every bar: one series, one colour */
  --sm-fill-pale:#DCEAFB;     /* the not-yet-built baseline, same family at a fraction of the weight */
  --sm-ghost:#C9D3DE;         /* the baseline repeated behind each bar, not a second measure */
  --sm-mono:var(--font-mono),'SF Mono',Menlo,Consolas,monospace;
  margin:26px 0;padding:20px 22px 16px;background:#fff;
  border:1px solid var(--sm-rule);border-radius:12px
}
/* No dark-scheme override: the card is pinned white in both schemes, so the ink follows the card
   rather than the page. */
.post-content .sm-cap{margin:0 0 14px;padding:0;text-align:left}
.post-content .sm-cap h4{margin:0 0 3px;font-size:15.5px;font-weight:700;color:var(--sm-ink);
  font-family:var(--font-body);letter-spacing:0}
.post-content .sm-cap p{margin:0;font-size:12.5px;color:var(--sm-muted);line-height:1.5}

.sm-legend{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;margin-bottom:12px;font-size:11.5px}
.sm-lg{display:flex;align-items:center;gap:6px;color:var(--sm-body)}
.sm-key{width:18px;height:11px;border-radius:2px;display:inline-block;flex:0 0 auto}
/* Pattern, not hue, separates the three states — see the note at the top of this file. */
.sm-key-new{border:1.5px dashed var(--sm-fill);background:var(--sm-fill-pale);box-sizing:border-box}
.sm-key-old{background:var(--sm-fill)}

/* An explicit header row: the bars had no column labels at all, so a reader met three numbers
   with no idea which was which until they reached the footnote. */
.sm-head{display:grid;grid-template-columns:minmax(96px,190px) 1fr 62px 44px;gap:10px;
  align-items:end;padding-bottom:6px;border-bottom:1px solid var(--sm-rule);margin-bottom:7px;
  /* 11px unconditionally, not inside the phone query. This was 10.5px and raised to 11 only
     below 640px, so it rendered 10.5 at 768, 1280 and - the case that matters - iPhone
     landscape at 844. Exactly the bug C:/dev/MOBILE_CHECK.md was written about. */
  font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
  color:var(--sm-muted)}
.sm-h-val,.sm-h-pct{text-align:right}

.post-content ol.sm-rows{list-style:none;margin:0;padding:0;display:grid;gap:7px}
.post-content ol.sm-rows li{margin:0;padding:0}
/* The theme paints a numbered badge on every .post-content ol li, absolutely positioned at the
   left edge, which lands on top of this component's own row content. */
.post-content ol.sm-rows li::before{content:none;display:none}
.sm-row{display:grid;grid-template-columns:minmax(96px,190px) 1fr 62px 44px;gap:10px;align-items:center}
.sm-row-base{padding-bottom:8px;border-bottom:1px solid var(--sm-rule);margin-bottom:3px}
.sm-name{font-size:12px;color:var(--sm-body);line-height:1.3}
.sm-name b{display:block;color:var(--sm-ink);font-weight:700}
.sm-nm{display:block;color:var(--sm-muted);font-size:11px}
.sm-nm-s{display:none;color:var(--sm-muted);font-size:11px}
/* Grid, not flex: a percentage bar width must resolve against a definite track. */
.sm-track{position:relative;height:17px;min-width:0}
.sm-bar{position:absolute;left:0;top:0;display:block;height:17px;border-radius:3px;min-width:2px}
.sm-bar-old{background:var(--sm-fill)}
/* The stretch past the largest unit the building has ever sold. Same ink, hatched, so it reads as
   "this part is not available" rather than as a different kind of thing. */
.sm-bar-new{background:var(--sm-fill-pale);border:1.5px dashed var(--sm-fill);box-sizing:border-box}
/* The baseline repeated behind every bar, so the overhang past it is visible on each row. */
.sm-ghost{position:absolute;left:0;top:0;height:17px;border-right:1.5px dashed var(--sm-muted);
  background:transparent}
.sm-val{font-family:var(--sm-mono);font-variant-numeric:tabular-nums;font-size:11.5px;
  font-weight:600;color:var(--sm-ink);text-align:right}
.sm-cap-note{display:block;font-style:normal;font-size:11px;font-weight:400;color:var(--sm-muted)}
.sm-cap-note b{font-weight:700;color:var(--sm-body)}
.sm-p90{position:absolute;top:-4px;height:25px;width:0;z-index:2;
  border-left:2px solid var(--sm-ink)}
.sm-key-p90{width:2px;height:15px;background:var(--sm-ink);border-radius:0;margin-right:7px}
.sm-pct{font-family:var(--sm-mono);font-variant-numeric:tabular-nums;font-size:11.5px;
  color:var(--sm-body);text-align:right;font-weight:600}
.sm-pct-base{color:var(--sm-muted);font-weight:400}

.post-content p.sm-foot{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--sm-rule);
  font-size:12.5px;line-height:1.6;color:var(--sm-body)}
.post-content p.sm-foot-2{margin-top:9px;padding-top:0;border-top:0}
.post-content p.sm-src{margin:10px 0 0;padding-top:10px;border-top:1px solid var(--sm-rule);
  font-size:11.5px;line-height:1.55;color:var(--sm-muted)}

@media (max-width:640px){
  .sm{padding:16px 14px 13px}
  .sm-head,.sm-row{grid-template-columns:minmax(78px,104px) 1fr 52px 40px;gap:7px}
  .sm-name{font-size:11.5px}
  .sm-nm{display:none}       /* the long meta line is desktop-only */
  .sm-nm-s{display:block}    /* a short one replaces it so lease and walk survive */
  .sm-head{letter-spacing:.04em}
  .sm-h-bar{display:none}
}
</style>
'''

out = TPL.replace('__DATA__', DATA).replace('__PROVENANCE__', provenance)
path = r'C:\\TheEnoughPoint-wt-newlaunch\\src\\components\\SameMoneySize.astro'
from jsx_space_lint import assert_clean
assert_clean(out, 'SameMoneySize.astro')   # a newline before an expression eats the space; five have shipped
io.open(path, 'w', encoding='utf-8').write(out)
print('written', len(out), 'bytes ·', len(rows), 'buildings ·',
      sum(1 for r in rows if r['above']), 'above the size that usually trades there')
