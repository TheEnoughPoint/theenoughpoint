"""Body + script + styles for CondoCompare.astro — variant E, wired for live selection."""

BODY = r'''
<figure class="cmp">
  <figcaption class="cmp-cap">
    <h4>Compare three, on the public record</h4>
    {/* The counts are written by the script from METRICS, not typed here, so adding or
        unmarking a measure cannot leave the caption claiming something untrue. */}
    <p>{n(ROWS.length)} condominiums, {DISTRICTS.length} districts, twelve months
    to {ASOF}. <span id="cmp-count"></span></p>
  </figcaption>

  <div class="cmp-picks">
    {[0, 1, 2].map((i) => (
      <div class="cmp-pick">
        <label for={`cmp-s${i}`}>{SLOTS[i]}</label>
        <select id={`cmp-s${i}`}>
          <option value="">&mdash; none &mdash;</option>
          {BY_D.map((grp) => (
            <optgroup label={`${grp.d} · ${grp.name}`}>
              {grp.items.map((r) => (
                <option value={r.p} selected={r.p === DEFAULTS[i]}>{r.p}</option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>
    ))}
  </div>

  <div class="cmp-lead" id="cmp-lead" aria-live="polite"></div>

  {/* Collapsible, but open on load: a reader who has picked three buildings wants the numbers,
      and the summary above is the headline rather than a replacement for them. */}
  <details class="cmp-fold" open>
    <summary>Every measure, side by side</summary>
    <div class="cmp-out" id="cmp-out"></div>
  </details>

  <p class="cmp-say" id="cmp-say"></p>

  <p class="cmp-src">Computed by us from URA private resale transactions and LTA station-exit
  locations, twelve months to {ASOF}. <b>A project appears only if at least {MIN_SALES} units
  resold in that period</b> &mdash; {n(ROWS.length)} of about {n(TOTAL_PROJECTS)} condominiums clear
  that, so this is the liquid end of the market, not a full list. Every price is a <b>median of what
  traded</b>, mixing floor, stack, facing, condition and renovation, so it is not a valuation of any
  particular unit. Distances are straight-line to the nearest station entrance; a real walk is
  typically 20&ndash;40% further. &ldquo;Against its district&rdquo; compares a project with resale
  of the <b>same size band</b> in the same district. Buildings are labelled by postal district,
  which is exact; we do not show a market-segment tag, because the upstream classification is an
  approximation and disagrees with itself inside some districts. <b>There is no overall score and
  there will not be one</b>: the weights belong to whoever is buying.</p>
</figure>

<script is:inline define:vars={{ ROWS }}>
(function(){
const $ = id => document.getElementById(id);
const sgd = v => 'S$' + Math.round(v).toLocaleString('en-SG');
const num = v => Math.round(v).toLocaleString('en-SG');
const BY = Object.fromEntries(ROWS.map(r => [r.p, r]));
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

function signed(x){
  const r = Math.abs(x).toFixed(0);
  return r === '0' ? '0' : (x >= 0 ? '+' : '−') + r;
}

// `dir` is the honest part: 'more'/'less' name a direction the data genuinely has, 'none' means
// the measure has no better end and the tool must not invent one. `lead`/`trail` are factual
// words — "longest", "furthest" — never "best" or "worst".
const METRICS = [
  // The sub-line is the point of this row. Between these buildings the medians differ by about
  // 13%; inside one of them the 10th-to-90th percentile can run 28%. Showing only the median
  // implies the project decides the price when the floor and the stack decide more of it.
  { label: 'Median resale price', short: 'price per square foot', dir: 'none', lead: '', trail: '', kind: 'ratio',
    fmt: r => sgd(r.psf) + ' psf', brief: r => sgd(r.psf), val: r => r.psf,
    sub: r => 'range ' + num(r.lo) + '–' + num(r.hi) + ' (' + Math.round((r.hi / r.lo - 1) * 100) + '%)',
    note: 'no better end — cheaper suits a buyer, dearer is what the market pays. The range beneath is the 10th to 90th percentile WITHIN that building, which is usually wider than the gap between buildings' },
  { label: 'Price change, 12 months', short: 'which way it is moving', dir: 'none', lead: '', trail: '',
    kind: 'pp',
    fmt: r => r.mo === null ? '—' : signed(r.mo * 100) + '%',
    brief: r => r.mo === null ? 'not available' : signed(r.mo * 100) + '%',
    val: r => r.mo === null ? 0 : r.mo,
    note: 'no better end — a rise is good news for an owner and bad for a buyer. Median against median, so a change in which units sold moves it too' },
  { label: 'Against its district', short: 'standing vs its district', dir: 'none', lead: '', trail: '', kind: 'pp',
    fmt: r => signed((r.psf / r.b - 1) * 100) + '%', brief: r => signed((r.psf / r.b - 1) * 100) + '%',
    val: r => r.psf / r.b - 1,
    note: 'no better end — a position vs same-size resale nearby, not a discount' },
  // NOT marked, and the reason matters. A raw count of resales tracks how many units a building
  // HAS at least as much as how readily they sell — a 1,200-unit project will out-trade a
  // 400-unit one at identical turnover. The feed carries no unit count, so the tool cannot
  // normalise it, and marking a leader on a measure it cannot normalise would be calling building
  // size liquidity. The number is still worth reporting: it is also the sample size behind that
  // building's median on every other row.
  { label: 'Resales in 12 months', short: 'the resale count', dir: 'none', lead: '', trail: '',
    kind: 'ratio', nomark: 'not size-adjusted',
    fmt: r => num(r.v), brief: r => num(r.v) + ' sales', val: r => r.v,
    note: 'not marked — a bigger building trades more at the same turnover, and no unit count is published to divide by. It is also the sample size behind this building’s median' },
  { label: 'Lease remaining', short: 'lease left', dir: 'more', lead: 'longest', trail: 'shortest',
    kind: 'ratio', fh: true,
    fmt: r => r.l === 'FH' ? 'Freehold' : r.l + ' yrs',
    brief: r => r.l === 'FH' ? 'freehold' : r.l + ' yrs',
    val: r => r.l === 'FH' ? 999 : Number(r.l),
    note: 'more years is more, and under 60 the CPF and lending rules tighten' },
  { label: 'To the nearest MRT', short: 'the walk to a station', dir: 'less', lead: 'nearest',
    trail: 'furthest', kind: 'ratio',
    fmt: r => num(r.m) + ' m · ' + r.x, brief: r => num(r.m) + ' m', val: r => r.m,
    note: 'nearer is nearer — whether that beats quiet is yours to weigh' },
  { label: 'Size that actually trades', short: 'the size that trades', dir: 'none', lead: '', trail: '',
    kind: 'ratio',
    fmt: r => num(r.s) + ' sq ft', brief: r => num(r.s) + ' sq ft', val: r => r.s,
    note: 'no better end — the right size is the one you need' },
  { label: 'Typical price paid', short: 'the typical cheque', dir: 'none', lead: '', trail: '',
    kind: 'ratio',
    fmt: r => sgd(r.q), brief: r => sgd(r.q), val: r => r.q,
    note: 'no better end — it tracks the size that trades as much as the price' },
];
const CLOSE = 0.15;   // below 15% apart, the buildings are level on that measure

// `fh` marks the ONE measure using 999 as a freehold sentinel. Without it these helpers treated
// any value over 999 as freehold — every price and every floor area — and scored them zero spread,
// which once reported a 2.2x price gap as "much the same".
function spreadOf(mt, picked){
  const vals = picked.map(mt.val);
  const hi = Math.max.apply(null, vals), lo = Math.min.apply(null, vals);
  if (mt.kind === 'pp') return Math.abs(hi - lo) * 100 / 20;
  if (mt.fh && hi >= 999) return 0;
  return lo > 0 ? (hi / lo) - 1 : 0;
}
function gapPhrase(mt, picked){
  const vals = picked.map(mt.val);
  const hi = Math.max.apply(null, vals), lo = Math.min.apply(null, vals);
  if (mt.kind === 'pp') return Math.round(Math.abs(hi - lo) * 100) + ' points apart';
  if (mt.fh && hi >= 999) return 'one is freehold';
  const ratio = lo > 0 ? hi / lo : 0;
  if (ratio >= 1.8) return 'about ' + (Math.round(ratio * 10) / 10) + '× apart';
  return Math.round((ratio - 1) * 100) + '% apart';
}
function rankOf(mt, picked, r){
  if (mt.dir === 'none' || picked.length < 2 || spreadOf(mt, picked) < CLOSE) return 'flat';
  const vals = picked.map(mt.val);
  const ordered = [...new Set(vals)].sort((a, b) => mt.dir === 'more' ? b - a : a - b);
  if (ordered.length < 2) return 'flat';
  const idx = ordered.indexOf(mt.val(r));
  return idx === 0 ? 'best' : idx === ordered.length - 1 ? 'worst' : 'mid';
}

// ---- the summary: what differs, in sentences, with the figures annotated -------------------
function renderLead(picked){
  if (picked.length < 2){ $('cmp-lead').innerHTML = ''; return; }

  // Freehold against leasehold is a difference in KIND. Its ratio is meaningless, so it is set
  // aside and named rather than allowed to fall into "level", which would say 91 years and
  // freehold are alike.
  const mixedTenure = METRICS.filter(mt => mt.fh).filter(mt => {
    const v = picked.map(mt.val);
    return Math.max.apply(null, v) >= 999 && Math.min.apply(null, v) < 999;
  });
  const ranked = METRICS.filter(mt => !mixedTenure.includes(mt))
    .map(mt => ({ mt, s: spreadOf(mt, picked) })).sort((a, b) => b.s - a.s);
  // Every measure lands in exactly one bucket; an earlier version let a measure that differed but
  // ranked fourth fall into neither and vanish.
  const differing = ranked.filter(x => x.s >= CLOSE);
  const apart = differing.slice(0, 3);
  const alsoApart = differing.slice(3);
  const alike = ranked.filter(x => x.s < CLOSE);

  let h = '';
  if (apart.length){
    h += '<div class="cmp-leadh">Where they differ most</div>';
    apart.forEach(({ mt }) => {
      const vals = picked.map(mt.val);
      const hiV = Math.max.apply(null, vals), loV = Math.min.apply(null, vals);
      const hi = picked[vals.indexOf(hiV)], lo = picked[vals.indexOf(loV)];
      // On a ranked measure the front-runner leads the sentence; on an unranked one the two ends
      // are simply shown, untinted, so the sentence carries no preference.
      const ranked2 = mt.dir !== 'none';
      const front = !ranked2 ? hi : (mt.dir === 'more' ? hi : lo);
      const back = front === hi ? lo : hi;
      h += '<div class="cmp-p"><h5>' + esc(mt.label) + '<em>' + gapPhrase(mt, picked) + '</em></h5><p>'
        + '<b>' + esc(front.p) + '</b> <span class="cmp-chip' + (ranked2 ? ' good' : '') + '">'
        + esc(mt.brief(front)) + '</span>'
        + (ranked2 ? ' <i class="cmp-ti good">▲ ' + mt.lead + '</i>' : '')
        + ' <span class="cmp-vs">against</span> '
        + '<b>' + esc(back.p) + '</b> <span class="cmp-chip' + (ranked2 ? ' bad' : '') + '">'
        + esc(mt.brief(back)) + '</span>'
        + (ranked2 ? ' <i class="cmp-ti bad">▼ ' + mt.trail + '</i>' : '')
        + '</p></div>';
    });
  }
  if (mixedTenure.length){
    const fh = picked.filter(r => r.l === 'FH').map(r => esc(r.p));
    const lh = picked.filter(r => r.l !== 'FH').map(r => esc(r.p) + ' ' + r.l + ' yrs');
    h += '<p class="cmp-alike"><b>Different in kind, not degree</b> — ' + fh.join(' and ')
      + (fh.length > 1 ? ' are freehold' : ' is freehold') + '; ' + lh.join(', ')
      + '. That is not a percentage gap and we do not state one.</p>';
  }
  if (alsoApart.length){
    h += '<p class="cmp-alike"><b>Also apart on</b> '
      + alsoApart.map(x => esc(x.mt.short) + ' (' + gapPhrase(x.mt, picked) + ')').join(' &middot; ')
      + '.</p>';
  }
  if (alike.length){
    h += '<p class="cmp-alike"><b>Level on</b> ' + alike.map(x => esc(x.mt.short)).join(' &middot; ')
      + ' — those will not decide it.</p>';
  }
  if (!apart.length){
    h = '<div class="cmp-leadh">These are close on everything measured here</div>'
      + '<p class="cmp-alike">No measure separates them by more than ' + Math.round(CLOSE * 100)
      + '%. Whatever decides between them is not in the public record — it is the unit, the '
      + 'floor and the outlook.</p>';
  }
  $('cmp-lead').innerHTML = h;
}

// ---- the facts table ------------------------------------------------------------------------
function render(){
  const picked = [0,1,2].map(i => BY[$('cmp-s'+i).value]).filter(Boolean);
  if (!picked.length){
    $('cmp-out').innerHTML = '<p class="cmp-empty">Choose at least one building to compare.</p>';
    $('cmp-lead').innerHTML = ''; $('cmp-say').textContent = '';
    return;
  }
  const cols = picked.length;
  // The header carries the identity for the whole table, so it names the building, then its
  // district and district name beneath — three bare names left a reader mapping them back to the
  // prose with no hint the buildings sit in different districts.
  let h = '<table class="cmp-t"><thead><tr><th class="cmp-corner">Measure</th>';
  picked.forEach(r => {
    h += '<th><b>' + esc(r.p) + '</b><span>' + r.d + '<em> · ' + esc(r.n) + '</em></span></th>';
  });
  h += '</tr></thead><tbody>';

  METRICS.forEach((mt, i) => {
    const level = cols > 1 && spreadOf(mt, picked) < CLOSE;
    const tag = level ? '<i>level</i>'
              : mt.nomark ? '<i>' + mt.nomark + '</i>'
              : mt.dir === 'none' ? '<i>no better end</i>' : '';
    // The explanation used to sit under every label, so eight paragraphs competed with the
    // numbers the reader came for. It is one tap away now; the short tag stays visible because it
    // is the compressed version of the same point.
    const nid = 'cmp-n' + i;
    h += '<tr class="' + (level ? 'lvl' : '') + '"><th>' + esc(mt.label) + tag
       + '<button type="button" class="cmp-q" aria-expanded="false" aria-controls="' + nid
       + '" aria-label="Explain ' + esc(mt.label) + '">?</button>'
       + '<span class="cmp-note" id="' + nid + '" hidden>' + esc(mt.note) + '</span></th>';
    picked.forEach(r => {
      const rank = rankOf(mt, picked, r);
      const mark = rank === 'best' ? ' <i>▲</i>' : rank === 'worst' ? ' <i>▼</i>' : '';
      h += '<td class="is-' + rank + '" aria-label="' + esc(r.p + ', ' + mt.label + ': ' + mt.fmt(r)
        + (mt.sub ? ', ' + mt.sub(r) : '')
        + (rank === 'best' ? ', ' + mt.lead : rank === 'worst' ? ', ' + mt.trail : '')) + '">'
        + esc(mt.fmt(r)) + mark
        + (mt.sub ? '<span class="cmp-sub">' + esc(mt.sub(r)) + '</span>' : '') + '</td>';
    });
    h += '</tr>';
  });
  h += '</tbody></table>';
  $('cmp-out').innerHTML = h;
  renderLead(picked);
  const dirN = METRICS.filter(m => m.dir !== 'none').length;
  $('cmp-count').innerHTML = METRICS.length + ' measures. <b>' + dirN + '</b> of them have a better '
    + 'end and are marked with it; the other ' + (METRICS.length - dirN) + ' do not, and say so.';

  if (cols < 2){
    $('cmp-say').innerHTML = 'Add a second building and every row will show how far apart they are.';
    return;
  }
  // A tally across the directional measures only. It is never summed with the four that have no
  // better end, and it is stated as a tally rather than a score.
  const dirMetrics = METRICS.filter(m => m.dir !== 'none');
  const tally = picked.map(r => dirMetrics.filter(mt => rankOf(mt, picked, r) === 'best').length);
  // Named from dirMetrics, not typed: unmarking the resale count left the old hand-written list
  // claiming liquidity was still directional.
  $('cmp-say').innerHTML = 'On the ' + dirMetrics.length + ' measure'
    + (dirMetrics.length === 1 ? '' : 's') + ' that have a better end ('
    + dirMetrics.map(m => m.short).join(' and ') + '), the count runs '
    + picked.map((r, i) => '<b>' + esc(r.p) + '</b> ' + tally[i]).join(' &middot; ') + '. '
    + 'The rest have no better end, or cannot be compared fairly, so they are reported and not '
    + 'scored &mdash; and the ones that do are not worth the same to everyone, which is why this '
    + 'tool will not add them up for you. What none of it can tell you is which unit, on which '
    + 'floor, facing what, and on these buildings that spread is wider than the gap between them.';
}

function init(){
  [0,1,2].forEach(i => $('cmp-s'+i).addEventListener('change', render));
  // Delegated: the table is rebuilt on every change, so a handler bound to the buttons would be
  // thrown away with them.
  $('cmp-out').addEventListener('click', e => {
    const b = e.target.closest('.cmp-q');
    if (!b) return;
    const note = document.getElementById(b.getAttribute('aria-controls'));
    const open = b.getAttribute('aria-expanded') === 'true';
    b.setAttribute('aria-expanded', String(!open));
    note.hidden = open;
  });
  render();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
})();
</script>

<style is:global>
.cmp{
  /* Status tokens from the fixed scale — reserved meaning, never themed, and used ONLY on the
     three measures that have a better end. good #0ca30c reads 3.27:1 on white and critical
     #d03b3b 4.68:1, so both clear 3:1 as marks; the washes carry dark text at well over 4.5:1.
     Per the status rule they never appear as colour alone: every marked cell also carries an
     arrow, and the summary names the leader and trailer in words. */
  --cmp-good:#0ca30c; --cmp-good-wash:#EBF6EB;
  --cmp-bad:#d03b3b;  --cmp-bad-wash:#FBEDED;
  --cmp-ink:var(--color-dark); --cmp-body:var(--color-body); --cmp-muted:var(--color-muted);
  --cmp-rule:var(--color-border); --cmp-soft:#F0ECE2;
  --cmp-mono:var(--font-mono),'SF Mono',Menlo,Consolas,monospace;
  margin:26px 0;padding:20px 22px 16px;background:#fff;
  border:1px solid var(--cmp-rule);border-radius:12px
}
/* No dark-scheme override: the card is pinned white in both schemes, so the ink follows the card
   rather than the page. */
.post-content .cmp-cap{margin:0 0 14px;padding:0;text-align:left}
.post-content .cmp-cap h4{margin:0 0 3px;font-size:15.5px;font-weight:700;color:var(--cmp-ink);
  font-family:var(--font-body);letter-spacing:0}
.post-content .cmp-cap p{margin:0;font-size:12.5px;color:var(--cmp-muted);line-height:1.5}

.cmp-picks{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.cmp-pick label{display:block;font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:.05em;color:var(--cmp-muted);margin-bottom:4px}
.cmp select{width:100%;font-family:inherit;font-size:12.5px;color:var(--cmp-ink);background:#fff;
  border:1px solid var(--cmp-rule);border-radius:6px;padding:11px 8px;min-height:44px}
.cmp select:focus-visible{outline:2px solid var(--cmp-ink);outline-offset:2px}

/* ---- summary ---- */
.cmp-leadh{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;
  color:var(--cmp-muted);margin-bottom:9px}
.cmp-p{margin-bottom:11px;padding-bottom:10px;border-bottom:1px solid var(--color-light)}
.cmp-p:last-of-type{border-bottom:0}
.post-content .cmp-p h5{margin:0 0 4px;font-size:12.5px;font-weight:700;color:var(--cmp-ink);
  font-family:var(--font-body)}
.post-content .cmp-p h5 em{font-style:normal;font-family:var(--cmp-mono);font-size:11.5px;
  color:var(--cmp-muted);font-weight:400;margin-left:7px}
.post-content .cmp-p p{margin:0;font-size:12.5px;line-height:1.85;color:var(--cmp-body)}
.cmp-chip{font-family:var(--cmp-mono);font-size:12px;font-weight:700;padding:2px 7px;
  border-radius:5px;background:var(--cmp-soft);color:var(--cmp-ink)}
.cmp-chip.good{background:var(--cmp-good-wash);color:var(--cmp-good)}
.cmp-chip.bad{background:var(--cmp-bad-wash);color:var(--cmp-bad)}
.cmp-ti{font-style:normal;font-size:11px;font-weight:700}
.cmp-ti.good{color:var(--cmp-good)} .cmp-ti.bad{color:var(--cmp-bad)}
.cmp-vs{color:var(--cmp-muted)}
.post-content p.cmp-alike{margin:0 0 5px;font-size:12px;line-height:1.55;color:var(--cmp-muted)}
.cmp-alike b{color:var(--cmp-body)}

/* ---- facts table ---- */
.post-content table.cmp-t{width:100%;border-collapse:collapse;margin:0;font-size:12px}
/* The header band and its 2px rule are what stop it reading as a first row of data. */
.post-content .cmp-t thead th{background:var(--cmp-soft);color:var(--cmp-ink);text-align:right;
  font-size:12px;font-weight:700;text-transform:none;letter-spacing:0;padding:9px 10px;
  border-bottom:2px solid var(--cmp-ink);vertical-align:bottom}
.post-content .cmp-t thead th b{display:block;font-size:12.5px;line-height:1.25}
.post-content .cmp-t thead th span{display:block;font-size:11px;font-weight:400;
  color:var(--cmp-muted);margin-top:1px}
.post-content .cmp-t thead th.cmp-corner{text-align:left;font-size:11px;font-weight:600;
  text-transform:uppercase;letter-spacing:.05em;color:var(--cmp-muted)}
.post-content .cmp-t tbody th{background:transparent;color:var(--cmp-body);text-align:left;
  font-size:11.5px;font-weight:600;text-transform:none;letter-spacing:0;padding:7px 10px;
  border-bottom:1px solid var(--color-light)}
.post-content .cmp-t tbody th i{font-style:normal;font-size:11px;font-weight:400;
  color:var(--cmp-muted);margin-left:5px}
.cmp-note{display:block;font-size:11px;font-weight:400;color:var(--cmp-muted);line-height:1.45;
  margin-top:4px;padding:6px 8px;background:var(--cmp-soft);border-radius:5px}
.cmp-note[hidden]{display:none}
/* A 44px tap target around a 17px glyph — the button is the hit area, the circle is the mark. */
.cmp-q{display:inline-flex;align-items:center;justify-content:center;width:17px;height:17px;
  margin-left:6px;padding:0;border:1px solid var(--cmp-rule);border-radius:50%;background:#fff;
  color:var(--cmp-muted);font-size:11px;font-weight:700;font-family:inherit;line-height:1;
  cursor:pointer;position:relative;vertical-align:-3px}
.cmp-q::after{content:'';position:absolute;top:-14px;right:-14px;bottom:-14px;left:-14px}
.cmp-q:hover{border-color:var(--cmp-ink);color:var(--cmp-ink)}
.cmp-q[aria-expanded="true"]{background:var(--cmp-ink);border-color:var(--cmp-ink);color:#fff}
.cmp-q:focus-visible{outline:2px solid var(--cmp-ink);outline-offset:2px}
.post-content .cmp-t tr.lvl th,.post-content .cmp-t tr.lvl td{color:var(--cmp-muted)}
.post-content .cmp-t td{padding:7px 10px;border-bottom:1px solid var(--color-light);text-align:right;
  font-family:var(--cmp-mono);font-variant-numeric:tabular-nums;color:var(--cmp-body);
  white-space:nowrap;vertical-align:top}
.post-content .cmp-t td i{font-style:normal;font-size:11px;margin-left:3px}
/* The within-building range sits under its median, in muted type, so the median never reads as
   the whole story about a price. */
.cmp-sub{display:block;font-size:11px;font-weight:400;color:var(--cmp-muted);margin-top:1px;
  white-space:nowrap}
.post-content .cmp-t td.is-best{background:var(--cmp-good-wash);color:var(--cmp-good);font-weight:700}
.post-content .cmp-t td.is-worst{background:var(--cmp-bad-wash);color:var(--cmp-bad);font-weight:700}
.post-content p.cmp-empty{margin:0;font-size:12.5px;color:var(--cmp-muted)}

.cmp-fold{margin:14px 0 0;border-top:1px solid var(--cmp-rule);padding-top:6px}
.post-content .cmp-fold>summary{cursor:pointer;list-style:none;font-size:11.5px;font-weight:600;
  color:var(--cmp-muted);padding:6px 0;min-height:44px;display:flex;align-items:center}
.post-content .cmp-fold>summary::-webkit-details-marker{display:none}
.post-content .cmp-fold>summary::before{content:'+';margin-right:7px;font-family:var(--cmp-mono);
  font-weight:700;color:var(--cmp-ink)}
.post-content .cmp-fold[open]>summary::before{content:'\2013'}
.post-content .cmp-fold>summary:hover{color:var(--cmp-ink)}
.post-content .cmp-fold>summary:focus-visible{outline:2px solid var(--cmp-ink);outline-offset:2px}

.post-content p.cmp-say{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--cmp-rule);
  font-size:12.5px;line-height:1.6;color:var(--cmp-body)}
.post-content p.cmp-src{margin:10px 0 0;padding-top:10px;border-top:1px solid var(--cmp-rule);
  font-size:11.5px;line-height:1.55;color:var(--cmp-muted)}

@media (max-width:640px){
  .cmp{padding:16px 14px 13px}
  .cmp-picks{grid-template-columns:1fr;gap:8px}
  .post-content .cmp-p p{line-height:2}
  /* Three condo names plus a measure column will not fit 390px on natural widths — measured at
     567px against a 328px container. Fixed layout instead, so names wrap rather than the table
     scrolling sideways; the descriptive district name is desktop-only, the code carries context. */
  .post-content .cmp-t{table-layout:fixed;width:100%}
  .post-content .cmp-t thead th span em{display:none}
  .post-content .cmp-t thead th,.post-content .cmp-t td,.post-content .cmp-t tbody th{padding:7px 5px}
  .post-content .cmp-t thead th{width:23%}
  .post-content .cmp-t thead th.cmp-corner{width:31%}
  .post-content .cmp-t thead th b{white-space:normal;overflow-wrap:anywhere}
  .post-content .cmp-t tbody th i{display:block;margin-left:0}
  .post-content .cmp-t td{white-space:normal;overflow-wrap:anywhere}
}
</style>
'''
