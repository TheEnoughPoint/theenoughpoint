"""Generate SameMoneySize.astro — all nine qualifying buildings, with the stock ceiling drawn."""
import io, json

rows = json.load(io.open('sm_rows.json', encoding='utf-8'))
DATA = json.dumps(rows, separators=(',', ':'), ensure_ascii=False)

TPL = '''---
// Hold the budget still and let the size move.
//
// The article's problem is that a percentage entry gap ("new build costs 34% more per square
// foot") is a number nobody can feel. This figure restates the identical fact in the unit a buyer
// lives in: one fixed sum, and the floor area it buys in each building.
//
// EVERY QUALIFYING BUILDING IS HERE, AND THE CONSTRAINT IS DRAWN RATHER THAN FOOTNOTED. An earlier
// version dropped four buildings where the budget bought more space than the building has ever
// sold, then explained the exclusion in a note longer than the chart. That was worse on both
// counts: it hid buildings a reader might want, and it spent its longest paragraph on absence.
// Now the bar runs solid to the largest unit that has actually traded there and continues hatched
// to what the money would notionally buy — so "your budget outgrows this building" is a thing you
// SEE, in the same row, instead of a paragraph you have to read and trust.
//
// That also puts Braddell View back on the chart, which matters: it is the row that shows the real
// trade in this neighbourhood most starkly — far more space, at half the remaining lease.
//
// ROWS is emitted mechanically from data/live.json in the sg-property-decision repo (URA
// PMI_Resi_Transaction resale medians, twelve months to August 2026; nearest MRT from LTA exits).
// Floor areas, percentages, the baseline and the spread are recomputed from BUDGET and ROWS below,
// so no figure in the prose can drift from a bar.
//
// COLOUR CARRIES NO VERDICT (VOICE.md C10). Every bar measures the same quantity — square feet —
// so every bar is the same ink. What varies is PATTERN: solid for floor area you could actually
// buy, hatched for the stretch past the largest unit ever sold, dashed outline for the building
// that does not exist yet. More space is not "better" here; it is the trade, and the lease and the
// walk in the same row are what it is traded against.
//
// Two filters, both mechanical and both stated on the figure: within 400 m of an MRT entrance, and
// at least 10 resales in the twelve months so a median is not one odd unit. Nothing else is
// excluded — the third filter that used to drop rows is now drawn instead.
const ASOF = 'August 2026';
const BUDGET = 2_400_000;
const NEW_PSF = 2900; // the middle of the illustrative band the article derives; NOT a quote

interface Row { p: string; psf: number; n: number; l: number | string; m: number; x: string;
  sq: number; cap: number; over: boolean; pct: number }

const ROWS: Row[] = __DATA__;

const BASE = Math.round(BUDGET / NEW_PSF);
const MAX = Math.max(BASE, ...ROWS.map((r) => r.sq));
const w = (v: number) => (v / MAX) * 100;
const OVER = ROWS.filter((r) => r.over);
const FITS = ROWS.filter((r) => !r.over);
const MIN_PCT = Math.min(...FITS.map((r) => r.pct));
const MAX_PCT = Math.max(...FITS.map((r) => r.pct));
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
    <span class="sm-lg"><i class="sm-key sm-key-new"></i>not built yet</span>
    <span class="sm-lg"><i class="sm-key sm-key-old"></i>floor area you could buy</span>
    <span class="sm-lg"><i class="sm-key sm-key-over"></i>more than this building has ever sold</span>
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
          <span class={`sm-bar sm-bar-old${r.over ? ' is-capped' : ''}`}
            style={`width:${w(r.over ? r.cap : r.sq)}%`}
            role="img"
            aria-label={`${r.p}. Median S$${n(r.psf)} per square foot over ${r.n} resales, ${r.l} years of lease remaining, ${r.m} metres to ${r.x} station. ${money(BUDGET)} buys ${n(r.sq)} square feet, ${r.pct} per cent more floor area than the new-build baseline.${r.over ? ` The largest unit ever sold there is ${n(r.cap)} square feet, so the budget stretches past anything this building offers.` : ''}`}></span>
          {r.over && (
            <span class="sm-bar sm-bar-over"
              style={`left:${w(r.cap)}%;width:${w(r.sq - r.cap)}%`} aria-hidden="true"></span>
          )}
        </span>
        <span class="sm-val">{n(r.sq)}{r.over && <i class="sm-cap-note">max {n(r.cap)}</i>}</span>
        <span class="sm-pct">+{r.pct}%</span>
      </li>
    ))}
  </ol>

  <p class="sm-foot">The same {money(BUDGET)} is <b>{n(BASE)} square feet</b> in a building that does
  not exist yet. In the {FITS.length} buildings that can actually offer what it buys, it is{' '}
  <b>{n(MIN_PCT)}% to {n(MAX_PCT)}% more floor area</b>, available next month. On the other{' '}
  {OVER.length} the budget runs past the largest unit ever sold there &mdash; the hatched stretch
  &mdash; which is its own answer: you cannot buy space a building does not have. That extra area is
  the entry gap made physical, and it is <b>not</b> money lost: part of it is what a new building, a
  fresh 99-year lease and no near-term repair bill genuinely cost. The lease column is where the
  biggest jumps show their price &mdash; the row offering {n(Math.max(...ROWS.map((r) => r.pct)))}%
  more space has {ROWS.find((r) => r.pct === Math.max(...ROWS.map((x) => x.pct))).l} years left
  against the baseline&rsquo;s fresh 99.</p>

  <p class="sm-src">Computed by us from URA private resale transactions, District 20, twelve months to
  {ASOF}; walking distances are straight-line to the nearest station entrance, so a real walk is
  typically 20&ndash;40% further. Two filters, applied mechanically: within 400 m of an MRT entrance,
  and at least 10 resales in the period so no median rests on one unusual unit. <b>A median mixes
  floor, stack, condition and renovation</b>, so no row is a price for any particular unit, and no
  row is a view on any building.</p>
</figure>

<style is:global>
.sm{
  --sm-ink:var(--color-dark); --sm-body:var(--color-body); --sm-muted:var(--color-muted);
  --sm-rule:var(--color-border);
  --sm-fill:#33414F;          /* one ink for every bar: the quantity is the same on every row */
  --sm-ghost:#E3DDCF;         /* baseline reference behind each bar, not a second measure */
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
.sm-key-new{border:1.5px dashed var(--sm-fill);background:
  repeating-linear-gradient(45deg,transparent,transparent 3px,var(--sm-ghost) 3px,var(--sm-ghost) 6px)}
.sm-key-old{background:var(--sm-fill)}
.sm-key-over{background:repeating-linear-gradient(45deg,var(--sm-fill),var(--sm-fill) 2px,
  transparent 2px,transparent 5px);border:1px solid var(--sm-fill)}

/* An explicit header row: the bars had no column labels at all, so a reader met three numbers
   with no idea which was which until they reached the footnote. */
.sm-head{display:grid;grid-template-columns:minmax(96px,190px) 1fr 62px 44px;gap:10px;
  align-items:end;padding-bottom:6px;border-bottom:1px solid var(--sm-rule);margin-bottom:7px;
  font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
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
.sm-bar-old.is-capped{border-radius:3px 0 0 3px}
/* The stretch past the largest unit the building has ever sold. Same ink, hatched, so it reads as
   "this part is not available" rather than as a different kind of thing. */
.sm-bar-over{background:repeating-linear-gradient(45deg,var(--sm-fill),var(--sm-fill) 2px,
  transparent 2px,transparent 5px);border:1px solid var(--sm-fill);border-left:0;
  border-radius:0 3px 3px 0;opacity:.85}
.sm-bar-new{background:repeating-linear-gradient(45deg,transparent,transparent 3px,var(--sm-ghost) 3px,var(--sm-ghost) 6px);
  border:1.5px dashed var(--sm-fill);box-sizing:border-box}
/* The baseline repeated behind every bar, so the overhang past it is visible on each row. */
.sm-ghost{position:absolute;left:0;top:0;height:17px;border-right:1.5px dashed var(--sm-muted);
  background:transparent}
.sm-val{font-family:var(--sm-mono);font-variant-numeric:tabular-nums;font-size:11.5px;
  font-weight:600;color:var(--sm-ink);text-align:right}
.sm-cap-note{display:block;font-style:normal;font-size:11px;font-weight:400;color:var(--sm-muted)}
.sm-pct{font-family:var(--sm-mono);font-variant-numeric:tabular-nums;font-size:11.5px;
  color:var(--sm-body);text-align:right;font-weight:600}
.sm-pct-base{color:var(--sm-muted);font-weight:400}

.post-content p.sm-foot{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--sm-rule);
  font-size:12.5px;line-height:1.6;color:var(--sm-body)}
.post-content p.sm-src{margin:10px 0 0;padding-top:10px;border-top:1px solid var(--sm-rule);
  font-size:11.5px;line-height:1.55;color:var(--sm-muted)}

@media (max-width:640px){
  .sm{padding:16px 14px 13px}
  .sm-head,.sm-row{grid-template-columns:minmax(78px,104px) 1fr 52px 40px;gap:7px}
  .sm-name{font-size:11.5px}
  .sm-nm{display:none}       /* the long meta line is desktop-only */
  .sm-nm-s{display:block}    /* a short one replaces it so lease and walk survive */
  .sm-head{font-size:11px;letter-spacing:.04em}
  .sm-h-bar{display:none}
}
</style>
'''

out = TPL.replace('__DATA__', DATA)
path = r'C:\\TheEnoughPoint-wt-newlaunch\\src\\components\\SameMoneySize.astro'
io.open(path, 'w', encoding='utf-8').write(out)
print('written', len(out), 'bytes ·', len(rows), 'buildings ·',
      sum(1 for r in rows if r['over']), 'exceed their stock ceiling')
