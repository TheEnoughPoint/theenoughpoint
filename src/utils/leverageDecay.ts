// The arithmetic behind daily-reset leveraged funds.
//
// A fund that promises "3x the daily return" does NOT promise 3x the return over
// any longer period, and the gap is not a fee — it is arithmetic. This module
// derives it, so the numbers on the page can be audited rather than trusted.
//
// ── The derivation ───────────────────────────────────────────────────────────
// Model the underlying as geometric Brownian motion with drift μ and volatility σ:
//     dS/S = μ dt + σ dW
// Its log return per year is therefore (μ − σ²/2).
//
// A fund that resets to L× exposure every day tracks L× the underlying's *daily*
// return, so its own dynamics are:
//     dF/F = L·(dS/S) = L·μ dt + L·σ dW
// giving a log return per year of (L·μ − L²σ²/2).
//
// Substituting the underlying's compound annual growth rate g, where
//     ln(1+g) = μ − σ²/2   ⇒   μ = ln(1+g) + σ²/2
// the leveraged fund's annual log return becomes
//     L·ln(1+g) + (L − L²)·σ²/2  =  L·ln(1+g) − L(L−1)·σ²/2
//
// So, before costs:
//     leveraged CAGR = (1+g)^L · exp(−L(L−1)σ²/2) − 1
//
// The exp(−L(L−1)σ²/2) term is the whole story. It does not depend on direction —
// only on volatility and leverage — and it is always a drag for L > 1. At L = 1 it
// vanishes, which is why an unleveraged fund has no such term.
//
// ── What this model does and does not capture ────────────────────────────────
// Captures: the compounding cost of resetting exposure daily in a volatile market.
// Does not capture: gap risk, borrowing costs that move, tracking error, tax, or
// the fact that real returns are not lognormal. Costs are handled as a single
// user-supplied annual figure rather than modelled, because a fund's expense ratio
// and its financing spread are published separately and change.
//
// This is a model, not a forecast. It answers "what does this structure do to a
// path with these characteristics", not "what will this fund return".

export interface DecayInputs {
  /** Underlying's compound annual growth rate, as a decimal (0.10 = 10% a year). */
  underlyingCagr: number;
  /** Underlying's annualised volatility, as a decimal (0.30 = 30%). */
  volatility: number;
  /** Daily-reset multiple: 2 for a 2x fund, 3 for a 3x fund. */
  leverage: number;
  /** Holding period in years. */
  years: number;
  /** The fund's published expense ratio, as a decimal (0.0132 = 1.32%). */
  expenseRatio: number;
  /**
   * All-in annual financing rate the fund pays on its borrowed exposure —
   * a short-term benchmark plus the counterparty spread (0.0455 = 4.55%).
   *
   * This is the cost the published expense ratio does NOT contain. Direxion's
   * own expense-limitation agreement excludes "swap financing and related
   * costs" and states plainly: "If these expenses were included, the expense
   * ratio would be higher."
   */
  financingRate: number;
}

export interface DecayResult {
  /** Total return of the underlying over the period, as a decimal. */
  underlyingTotal: number;
  /** What "L times the underlying's return" would naively imply. */
  naiveTotal: number;
  /** What the daily-reset fund actually delivers, before costs. */
  leveragedTotalGross: number;
  /** The same, after the stated annual cost. */
  leveragedTotal: number;
  /** Annual drag from the daily reset alone, as a decimal. */
  volatilityDragPerYear: number;
  /** Annual financing cost on the borrowed exposure, (L-1) x financingRate. */
  financingCostPerYear: number;
  /** Expense ratio plus financing — the cost that actually applies. */
  allInCostPerYear: number;
  /** Leveraged fund's compound annual growth rate, after costs. */
  leveragedCagr: number;
  /** Underlying CAGR at which the leveraged fund merely breaks even, after all costs. */
  breakEvenCagr: number;
}

export function computeDecay(input: DecayInputs): DecayResult {
  const { underlyingCagr: g, volatility: s, leverage: L, years: t,
          expenseRatio: e, financingRate: f } = input;

  const underlyingTotal = Math.pow(1 + g, t) - 1;
  const naiveTotal = L * underlyingTotal;

  // exp(−L(L−1)σ²/2) — the daily-reset drag, per year
  const dragFactor = Math.exp(-L * (L - 1) * s * s / 2);

  // The fund holds L units of exposure against 1 unit of investor equity, so it
  // finances (L−1). KORU's own filings show swap notional running a little above
  // that (2.49x for a 3x fund), which makes this model conservative rather than
  // alarmist.
  const financingCostPerYear = (L - 1) * f;
  const allInCostPerYear = e + financingCostPerYear;
  const costFactor = 1 - allInCostPerYear;

  const leveragedCagrGross = Math.pow(1 + g, L) * dragFactor - 1;
  const leveragedCagr = (1 + leveragedCagrGross) * costFactor - 1;

  return {
    underlyingTotal,
    naiveTotal,
    leveragedTotalGross: Math.pow(1 + leveragedCagrGross, t) - 1,
    leveragedTotal: Math.pow(1 + leveragedCagr, t) - 1,
    volatilityDragPerYear: 1 - dragFactor,
    financingCostPerYear,
    allInCostPerYear,
    leveragedCagr,
    // Break-even: the underlying CAGR at which the leveraged fund returns zero,
    // i.e. (1+g)^L · dragFactor · costFactor = 1.
    breakEvenCagr: Math.pow(1 / (dragFactor * costFactor), 1 / L) - 1,
  };
}
