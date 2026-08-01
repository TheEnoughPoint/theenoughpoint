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
  /** All-in annual cost of the leveraged fund (expense ratio + financing), decimal. */
  annualCost: number;
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
  /** Leveraged fund's compound annual growth rate, after costs. */
  leveragedCagr: number;
  /** Underlying CAGR the fund needs just to match the UNLEVERAGED fund, before costs. */
  breakEvenCagr: number;
}

export function computeDecay(input: DecayInputs): DecayResult {
  const { underlyingCagr: g, volatility: s, leverage: L, years: t, annualCost: c } = input;

  const underlyingTotal = Math.pow(1 + g, t) - 1;
  const naiveTotal = L * underlyingTotal;

  // exp(−L(L−1)σ²/2) — the daily-reset drag, per year
  const dragFactor = Math.exp(-L * (L - 1) * s * s / 2);
  const volatilityDragPerYear = 1 - dragFactor;

  const leveragedCagrGross = Math.pow(1 + g, L) * dragFactor - 1;
  const leveragedCagr = (1 + leveragedCagrGross) * (1 - c) - 1;

  return {
    underlyingTotal,
    naiveTotal,
    leveragedTotalGross: Math.pow(1 + leveragedCagrGross, t) - 1,
    leveragedTotal: Math.pow(1 + leveragedCagr, t) - 1,
    volatilityDragPerYear,
    leveragedCagr,
    // Setting leveraged CAGR = underlying CAGR and solving gives g* = exp(Lσ²/2) − 1
    breakEvenCagr: Math.exp(L * s * s / 2) - 1,
  };
}
