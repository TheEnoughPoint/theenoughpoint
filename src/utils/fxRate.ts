// Build-time SGD-per-USD rate for the estate-tax calculator.
//
// Chain, in order of preference:
//   1. MAS daily interbank series — the preferred source, but its API has been
//      down for stretches (404 on 2026-07-18 and 2026-07-24).
//   2. US Federal Reserve H.10 weekly release — official US series, worked on
//      2026-07-24. The estate tax itself is a US tax assessed in USD, so this
//      is a defensible stand-in.
//   3. A stored, audited constant — last resort so the page always renders.
//
// Every tier is validated for plausibility and freshness before being trusted.
// Failures log loudly in the build output and fall through to the next tier.
// The site rebuilds on every push, so the page refreshes itself whenever
// anything else ships.

export interface FxRate {
  sgdPerUsd: number;
  /** Display form for the on-page "rate as at" line, e.g. "17 July 2026". */
  asOf: string;
  /** Display form for the on-page source attribution. */
  source: string;
  tier: 'mas' | 'h10' | 'fallback';
}

const FALLBACK: FxRate = {
  sgdPerUsd: 1.2911,
  asOf: '17 July 2026',
  source: 'US Federal Reserve H.10 weekly release',
  tier: 'fallback',
};

const MAS_URL =
  'https://eservices.mas.gov.sg/api/action/datastore_search' +
  '?resource_id=10eafb90-11a2-4fbd-b7a7-ac15a42d60b6&limit=1&sort=end_of_day%20desc';
const H10_URL = 'https://www.federalreserve.gov/releases/h10/current/';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

function displayDate(d: Date): string {
  return `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}
function plausible(rate: number): boolean {
  // USD/SGD has traded roughly 1.2–1.8 over recent decades; anything outside
  // a generous band means we parsed the wrong thing.
  return Number.isFinite(rate) && rate > 1.0 && rate < 1.9;
}
function ageDays(d: Date): number {
  return (Date.now() - d.getTime()) / 86_400_000;
}

async function get(url: string): Promise<Response> {
  const res = await fetch(url, { signal: AbortSignal.timeout(8000), headers: { accept: '*/*' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res;
}

async function fromMas(): Promise<FxRate> {
  const json: any = await (await get(MAS_URL)).json();
  const rec = json?.result?.records?.[0];
  const rate = Number(rec?.usd_sgd);
  const d = new Date(`${rec?.end_of_day}T00:00:00Z`);
  if (!plausible(rate)) throw new Error(`implausible rate "${rec?.usd_sgd}"`);
  if (Number.isNaN(d.getTime()) || ageDays(d) > 14 || ageDays(d) < -1) {
    throw new Error(`stale or invalid date "${rec?.end_of_day}"`);
  }
  return { sgdPerUsd: rate, asOf: displayDate(d), source: 'MAS daily interbank series', tier: 'mas' };
}

async function fromH10(): Promise<FxRate> {
  const html = await (await get(H10_URL)).text();

  // Row: <th ...>  SINGAPORE  </th><td>DOLLAR</td><td>1.2930</td> ... </tr>
  const sg = html.indexOf('SINGAPORE');
  if (sg < 0) throw new Error('SINGAPORE row not found');
  const row = html.slice(sg, html.indexOf('</tr>', sg));
  const rates = [...row.matchAll(/>\s*(\d+\.\d{4})\s*</g)].map((m) => Number(m[1]));
  const rate = rates[rates.length - 1];
  if (!plausible(rate)) throw new Error(`implausible rate "${rate}"`);

  // The last data cell names its column header (headers="a7 ..."); that header
  // cell carries the observation date, e.g. "Jul 17". Year comes from the
  // release date printed on the page, stepping back a year across Dec→Jan.
  const headerRefs = [...row.matchAll(/headers="(a\d+)/g)].map((m) => m[1]);
  const lastCol = headerRefs[headerRefs.length - 1];
  if (!lastCol) throw new Error('no column header refs in row');
  const headerCell = new RegExp(`<th[^>]*id="${lastCol}"[^>]*>([\\s\\S]*?)</th>`).exec(html)?.[1] ?? '';
  const headerText = headerCell.replace(/<[^>]+>/g, ' ');
  const md = /([A-Za-z]{3,9})\.?\s+(\d{1,2})/.exec(headerText);
  if (!md) throw new Error(`unparseable column header "${headerText.trim()}"`);
  const obsMonth = MONTHS.findIndex((m) => m.toLowerCase().startsWith(md[1].toLowerCase().slice(0, 3)));
  if (obsMonth < 0) throw new Error(`unknown month "${md[1]}"`);

  const rel = new RegExp(`(${MONTHS.join('|')})\\s+\\d{1,2},\\s*(\\d{4})`).exec(html);
  if (!rel) throw new Error('release date not found');
  const relMonth = MONTHS.indexOf(rel[1]);
  const year = Number(rel[2]) - (obsMonth > relMonth ? 1 : 0);

  const d = new Date(Date.UTC(year, obsMonth, Number(md[2])));
  if (ageDays(d) > 35 || ageDays(d) < -1) throw new Error(`stale observation ${displayDate(d)}`);
  return { sgdPerUsd: rate, asOf: displayDate(d), source: 'US Federal Reserve H.10 weekly release', tier: 'h10' };
}

let cached: Promise<FxRate> | null = null;

export function getSgdPerUsd(): Promise<FxRate> {
  cached ??= (async () => {
    const tiers = [['MAS', fromMas], ['H.10', fromH10]] as const;
    for (const [name, fn] of tiers) {
      try {
        const fx = await fn();
        console.log(`[estate-fx] ${name}: S$${fx.sgdPerUsd} per US$1, as at ${fx.asOf}`);
        return fx;
      } catch (e) {
        console.warn(`[estate-fx] ${name} source failed (${(e as Error).message}) — trying next tier`);
      }
    }
    console.warn(
      `[estate-fx] ALL live sources failed — using stored fallback ` +
      `(S$${FALLBACK.sgdPerUsd}, ${FALLBACK.asOf}). If this persists, refresh src/utils/fxRate.ts.`,
    );
    return FALLBACK;
  })();
  return cached;
}
