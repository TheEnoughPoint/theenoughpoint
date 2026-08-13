/**
 * What a card stack actually earns, once the caps bite.
 *
 * The companion to src/utils/mileValue.ts. That module answers "what is a mile
 * worth?"; this one answers the question the miles piece deliberately left
 * open: which card should you carry, and how many.
 *
 * The mechanism is a single piece of arithmetic that card marketing never
 * shows you. A Singapore bonus card pays its headline rate — typically 4 miles
 * per dollar — only up to a monthly cap, and everything above that cap drops to
 * a base rate of 0.4 mpd, which is the standard across Citi, DBS and UOB. So
 * the advertised rate is a rate on a slice of your spending, and the rate you
 * actually earn is a weighted average that falls as you spend more:
 *
 *   blended = (bonus spend x bonus rate + the rest x base rate) / total spend
 *
 * One 4 mpd card with a S$1,000 cap pays 4.00 mpd at S$1,000 a month and
 * 1.30 mpd at S$4,000. The card did not change. The denominator did.
 *
 * Which is why the honest question is not which card but HOW MANY, since each
 * additional card adds another capped bucket of bonus-rate spending. Nothing
 * here recommends a card, a bank or a strategy: it is arithmetic on the
 * reader's own numbers, and the friction it deliberately makes visible —
 * annual fees, conversion fees — usually argues for fewer cards, not more.
 */

/** The base rate that spending above a bonus cap falls to. 0.4 mpd is the
 *  standard across the major Singapore issuers (1 point per S$1 at Citi,
 *  1 unit per S$5 at DBS and UOB, all landing at the same 0.4). */
export const BASE_MPD = 0.4;

/** At exactly one cent a mile, miles-per-dollar and percentage rebate are the
 *  same number, because 1 mpd x 1 cent = 1 cent per dollar = 1%. It makes the
 *  comparison against a cashback card immediate, and it is the reason the
 *  one-cent exit is such a useful yardstick. */
export const CENTS_AT_PARITY = 1.0;

export interface StackInput {
  /** Total monthly spend put on cards, S$. */
  monthlySpend: number;
  /** How many bonus cards you will actually operate each month. */
  cards: number;
  /** Monthly bonus cap per card, S$. */
  capPerCard: number;
  /** Headline miles per dollar inside the cap. */
  bonusMpd: number;
  /** Miles per dollar above the cap, or outside the bonus category. */
  baseMpd: number;
  /**
   * Share of spending that actually falls into a bonus category you hold a card
   * for, 0–1. Defaults to 1 for the idealised case.
   *
   * This is the input most comparisons omit, and leaving it out is how a stack
   * gets oversold. Bonus capacity is NOT a fungible pool: a card capped at
   * S$1,000 of online spending does nothing for your contactless spending, and
   * a second online card does nothing once your online spending is exhausted.
   * Four cards only deliver four caps' worth of bonus if your spending happens
   * to distribute across their four categories — and real spending does not
   * arrive pre-sorted. Groceries, insurance, school fees, tax and rent are
   * either excluded outright or carry an admin fee that exceeds the reward.
   */
  categoryFit?: number;
}

export interface StackResult {
  /** Spending that earns the bonus rate, S$ a month. */
  bonusSpend: number;
  /** Spending that drops to the base rate, S$ a month. */
  baseSpend: number;
  /** Miles earned a month. */
  monthlyMiles: number;
  /** The rate you actually earn, across everything. */
  blendedMpd: number;
  /** True once spending has overflowed every cap. */
  capped: boolean;
  /** Share of spending earning only the base rate, 0–1. */
  overflowShare: number;
  /**
   * Which ceiling is actually costing you miles — the useful diagnostic, because
   * the two have opposite remedies. 'caps' means another card would help;
   * 'categories' means it would not, and the spending itself is the problem.
   */
  binding: 'caps' | 'categories' | 'neither';
}

const clampMin = (n: number, lo: number) => (isFinite(n) && n > lo ? n : lo);

/** The blended rate, which is the only earn rate that describes your wallet. */
export function priceStack(input: StackInput): StackResult {
  const spend = clampMin(input.monthlySpend, 0);
  const cards = Math.max(0, Math.floor(input.cards));
  const cap = clampMin(input.capPerCard, 0);
  const bonus = clampMin(input.bonusMpd, 0);
  const base = clampMin(input.baseMpd, 0);

  const fit = Math.min(1, Math.max(0, input.categoryFit ?? 1));

  // Two ceilings bind, and the binding one is whichever is lower: the caps you
  // hold, and the spending that actually qualifies for them.
  const capacity = cards * cap;
  const eligible = spend * fit;
  const bonusSpend = Math.min(eligible, capacity);
  const baseSpend = Math.max(0, spend - bonusSpend);
  const monthlyMiles = bonusSpend * bonus + baseSpend * base;

  return {
    bonusSpend,
    baseSpend,
    monthlyMiles,
    blendedMpd: spend > 0 ? monthlyMiles / spend : 0,
    capped: spend > capacity,
    overflowShare: spend > 0 ? baseSpend / spend : 0,
    binding: baseSpend <= 0 ? 'neither' : capacity <= eligible ? 'caps' : 'categories',
  };
}

/**
 * The rebate, net of what the stack costs to run.
 *
 * Annual fees are the drag most comparisons omit, and on a multi-card stack
 * they are not small: four cards at around S$196 each is S$784 a year, which
 * on S$48,000 of spending is 1.6 percentage points — more than the entire
 * advantage of a cashback card. Most are waivable on request; none should be
 * assumed away.
 */
export function netRebatePct(
  blendedMpd: number,
  centsPerMile: number,
  annualFees: number,
  annualSpend: number,
): number {
  const gross = blendedMpd * centsPerMile;
  const drag = annualSpend > 0 ? (annualFees / annualSpend) * 100 : 0;
  return gross - drag;
}

/** The value per mile this stack must achieve to match a flat cashback card. */
export function breakevenCentsPerMile(cashbackPct: number, blendedMpd: number): number {
  return blendedMpd > 0 ? cashbackPct / blendedMpd : Infinity;
}

/**
 * The spend at which this stack stops beating cashback.
 *
 * Solved by scanning rather than algebraically: the blended rate is piecewise
 * and the fee drag is hyperbolic in spend, so the net-rebate curve is not
 * monotonic in a form worth inverting by hand. Returns null when the stack
 * beats cashback across the whole range scanned.
 */
export function crossoverSpend(
  stack: Omit<StackInput, 'monthlySpend'>,
  centsPerMile: number,
  annualFees: number,
  cashbackPct: number,
  maxMonthly = 30000,
): number | null {
  const step = 50;
  let wasAhead: boolean | null = null;

  for (let s = step; s <= maxMonthly; s += step) {
    const { blendedMpd } = priceStack({ ...stack, monthlySpend: s });
    const net = netRebatePct(blendedMpd, centsPerMile, annualFees, s * 12);
    const ahead = net >= cashbackPct;
    if (wasAhead === true && !ahead) return s;
    wasAhead = ahead;
  }
  return null;
}
