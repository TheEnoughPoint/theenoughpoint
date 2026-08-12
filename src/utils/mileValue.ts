/**
 * What a redeemed mile is actually worth — and what that makes your card.
 *
 * This module is the 2026 rebuild of a spreadsheet one of us wrote in December
 * 2013 to decide which card to carry. That sheet did two things, and they are
 * still the only two things that matter:
 *
 *   1. Price the redemption:  (value of the seat - taxes paid) / miles used
 *   2. Turn it into a rebate:  value per mile x miles earned per dollar spent
 *
 * The one thing the 2013 sheet got wrong — and nearly every miles comparison
 * still gets wrong — is step 1's numerator. It valued the seat at the published
 * fare of the cabin flown. That flatters the answer whenever you would never
 * have bought that cabin with cash. The honest numerator is a counterfactual:
 * what you would genuinely have spent had the miles not existed.
 *
 * So `seatValue` interpolates between the fare you would actually have bought
 * (`fareAlternative`) and the fare of the cabin you flew (`fareRedeemed`), by
 * the share of that premium you would genuinely have paid (`willingness`).
 * willingness = 1 means you would have bought the business ticket outright;
 * willingness = 0 means you would have flown economy and the upgrade, however
 * pleasant, saved you nothing in cash. Both ends are legitimate; most honest
 * answers sit between them, which is exactly the haircut this module exists
 * to apply.
 *
 * Everything here is arithmetic on the reader's own inputs. No fare is asserted,
 * no valuation is recommended, and nothing predicts what a mile will be worth
 * later — the November 2025 devaluation is the standing reminder that award
 * charts are revisable at the issuer's discretion.
 */

/** SIA's guaranteed exit for a KrisFlyer mile, in Singapore dollars.
 *  From 1 July 2025 the rate across Miles+Cash on SIA and Scoot tickets, Kris+,
 *  KrisShop and Pelago was harmonised at 100 miles = S$1. It is the floor every
 *  redemption should be measured against, because it is available to everyone
 *  with no seat to hunt for. */
export const FLOOR_SGD_PER_MILE = 0.01;

export interface RedemptionInput {
  /** Total miles surrendered for the whole booking (all passengers, all legs). */
  miles: number;
  /** Cash paid on the award ticket — taxes, fees and any carrier surcharges, S$. */
  awardTaxes: number;
  /** Published cash price of the cabin actually flown, S$, taxes included. */
  fareRedeemed: number;
  /** Published cash price of the cabin you would otherwise have bought, S$. */
  fareAlternative: number;
  /** Share of the premium between the two fares you would genuinely have paid, 0–1. */
  willingness: number;
}

export interface RedemptionResult {
  /** The counterfactual worth of the seat after the haircut, S$. */
  seatValue: number;
  /** Cash genuinely not spent because the miles existed, S$. */
  cashSaved: number;
  /** Value per mile, in Singapore cents. */
  centsPerMile: number;
  /** What the same miles would have returned at the 1-cent floor, S$. */
  floorValue: number;
  /** How many times better than the floor. 1.0 means the floor would have matched it. */
  vsFloor: number;
  /** True when the redemption failed to beat the floor available to everyone. */
  belowFloor: boolean;
}

/** Clamp to a sane range without throwing on a reader's stray keystroke. */
const clamp = (n: number, lo: number, hi: number): number =>
  !isFinite(n) ? lo : Math.min(hi, Math.max(lo, n));

/**
 * Price one redemption.
 *
 * cashSaved can legitimately go negative — an award ticket whose taxes exceed
 * the fare you would actually have paid is a real outcome on short-haul economy
 * redemptions, and the tool must be willing to say so rather than floor it at
 * zero.
 */
export function priceRedemption(input: RedemptionInput): RedemptionResult {
  const miles = Math.max(0, input.miles);
  const w = clamp(input.willingness, 0, 1);
  const lo = Math.max(0, input.fareAlternative);
  const hi = Math.max(0, input.fareRedeemed);

  // The counterfactual seat: the fare you would have bought, plus the slice of
  // the upgrade premium you would genuinely have paid for. Guard hi < lo so a
  // mis-entered pair cannot invert the interpolation.
  const premium = Math.max(0, hi - lo);
  const seatValue = lo + w * premium;

  const cashSaved = seatValue - Math.max(0, input.awardTaxes);
  const centsPerMile = miles > 0 ? (cashSaved / miles) * 100 : 0;
  const floorValue = miles * FLOOR_SGD_PER_MILE;
  const vsFloor = floorValue > 0 ? cashSaved / floorValue : 0;

  return {
    seatValue,
    cashSaved,
    centsPerMile,
    floorValue,
    vsFloor,
    belowFloor: miles > 0 && cashSaved < floorValue,
  };
}

/**
 * The earning side. A card's rebate is not its earn rate — it is its earn rate
 * priced at what you actually get per mile.
 *
 * effective rebate (%) = value per mile (cents) x miles per dollar
 *
 * because cents-per-mile x miles-per-dollar = cents returned per dollar spent,
 * which is a percentage by construction. This is the identity the 2013 sheet
 * was built on and it has not aged.
 */
export function effectiveRebate(centsPerMile: number, milesPerDollar: number): number {
  return centsPerMile * Math.max(0, milesPerDollar);
}

/**
 * The hurdle. Below this value per mile, a flat cashback card returns more on
 * the same spending than the miles card does — no judgement about the seat,
 * just the arithmetic of the two rebates.
 *
 * breakeven (cents per mile) = cashback rate (%) / miles per dollar
 */
export function breakevenCentsPerMile(cashbackPct: number, milesPerDollar: number): number {
  return milesPerDollar > 0 ? cashbackPct / milesPerDollar : Infinity;
}

/** Miles needed for a whole booking. Award charts are published one-way and
 *  per passenger, which is where most back-of-envelope estimates go wrong. */
export function bookingMiles(oneWayMiles: number, passengers: number, legs: number): number {
  return Math.max(0, oneWayMiles) * Math.max(1, passengers) * Math.max(1, legs);
}
