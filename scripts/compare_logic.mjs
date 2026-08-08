// The comparison's decision rules, in one place so they can be tested.
//
// This module is the single source of truth. gen_compare.py inlines it verbatim into
// CondoCompare.astro's client script, and compare_logic.test.mjs tests it with `node --test`.
// Editing the copy inside the .astro file is a mistake — it is generated.
//
// Everything here is pure: no DOM, no formatting, no data. Formatting lives in the component
// because it needs Intl; these are the rules that decide what a reader is told.

export const CLOSE = 0.15;   // below 15% apart, buildings are "level" on that measure
export const RANGE_MIN_N = 20; // below 20 sales a p10-p90 range is min-to-max, so it is withheld

// Size bands mirror scripts/fetch_data.py::_sizeband exactly. Duplicated deliberately — the
// benchmark a project is compared against is chosen upstream by these boundaries, and a silent
// divergence between the two would change what "against its district" means without any error.
export function bandOf(sqft) {
  return sqft < 600 ? 0 : sqft < 850 ? 1 : sqft < 1150 ? 2 : 3;
}

/** Is this selection a mix of freehold and leasehold? Then lease is a difference in KIND and no
 *  ratio of it means anything. Driven by an explicit flag, never by a sentinel value: an earlier
 *  version used `>= 999` and the feed genuinely contains leases of 968, 9968 and 999963. */
export function mixedTenure(picked) {
  const fh = picked.filter((r) => r.fh).length;
  return fh > 0 && fh < picked.length;
}

/** How far apart the selection sits on a measure, on a scale comparable across measures.
 *  'ratio'  — max/min - 1.
 *  'pp'     — range in percentage points over a 20pp reference, so 5pp reads like 25%.
 *  Freehold in a mixed set returns 0: the caller must have set that measure aside already. */
export function spreadOf(mt, picked) {
  if (mt.fhAware && mixedTenure(picked)) return 0;
  const vals = picked.map(mt.val);
  const hi = Math.max(...vals), lo = Math.min(...vals);
  if (mt.kind === 'pp') return Math.abs(hi - lo) * 100 / 20;
  return lo > 0 ? hi / lo - 1 : 0;
}

/** 'best' | 'worst' | 'mid' | 'flat'. Flat covers three cases that must not be marked: a measure
 *  with no better end, a single selection, and a level row — 92/91/90 years is not a podium. */
export function rankOf(mt, picked, r) {
  if (mt.dir === 'none' || picked.length < 2 || spreadOf(mt, picked) < CLOSE) return 'flat';
  const vals = picked.map(mt.val);
  const ordered = [...new Set(vals)].sort((a, b) => (mt.dir === 'more' ? b - a : a - b));
  if (ordered.length < 2) return 'flat';
  const i = ordered.indexOf(mt.val(r));
  return i === 0 ? 'best' : i === ordered.length - 1 ? 'worst' : 'mid';
}

/** Every measure must land in exactly one of these. An earlier version sliced the top three and
 *  filtered the rest on spread, so a measure that differed but ranked fourth vanished entirely. */
export function bucket(metrics, picked) {
  const setAside = metrics.filter((mt) => mt.fhAware && mixedTenure(picked));
  const ranked = metrics
    .filter((mt) => !setAside.includes(mt))
    .map((mt) => ({ mt, s: spreadOf(mt, picked) }))
    .sort((a, b) => b.s - a.s);
  const differing = ranked.filter((x) => x.s >= CLOSE);
  return {
    apart: differing.slice(0, 3),
    alsoApart: differing.slice(3),
    alike: ranked.filter((x) => x.s < CLOSE),
    setAside,
  };
}

/** The short tag a measure carries in the table. Lives here, not in the component: the component
 *  previously derived it from spreadOf directly, and because a mixed-tenure set has a spread of 0
 *  it labelled "Freehold against 91 years" as LEVEL — the exact claim bucket() exists to avoid. */
export function tagFor(mt, picked) {
  if (mt.fhAware && mixedTenure(picked)) return 'different in kind';
  if (picked.length > 1 && spreadOf(mt, picked) < CLOSE) return 'level';
  if (mt.nomark) return mt.nomark;
  if (mt.dir === 'none') return 'no better end';
  return '';
}

/** Row order for the table: the measures that actually separate these buildings first, the ones
 *  that cannot decide anything last. Without this the reader met price and 12-month change at the
 *  top — both greyed as level on most selections — so the faintest rows were the first ones seen.
 *
 *  Within the discriminating group, widest spread first, which is the same priority the summary
 *  above the table already uses. Order therefore changes with the selection; that is the point,
 *  and the row labels travel with the values so nothing is ambiguous. A single selection ranks
 *  nothing, so it keeps the canonical order. */
export function orderFor(metrics, picked) {
  if (picked.length < 2) return [...metrics];
  return [...metrics].sort((a, b) => {
    const al = tagFor(a, picked) === 'level' ? 1 : 0;
    const bl = tagFor(b, picked) === 'level' ? 1 : 0;
    if (al !== bl) return al - bl;
    return spreadOf(b, picked) - spreadOf(a, picked);
  });
}

/** Whether a project's p10-p90 price range is stable enough to print. */
export function showRange(r) {
  return r.v >= RANGE_MIN_N;
}
