// Singapore private-property affordability — what a purchase demands of you before
// anything else about it matters.
//
// This module is the canonical derivation. AffordabilityTool.astro mirrors it in an
// inline script so the page works without a client bundle; if you change one, change
// both.
//
// The rules, and why each one is here
// -----------------------------------
// Four published rules decide almost the whole answer, and three of them are about age
// rather than money, which is why buyers are so often surprised by the result.
//
//   TDSR   Total debt payments cannot exceed 55% of gross monthly income. MAS.
//   FLOOR  The instalment in that test is computed at a 4% medium-term rate, not at the
//          rate you will actually pay. A package quoted near 1.5% does not help you
//          qualify — it only changes what you hand over afterwards.
//   LTV    75% ceiling on a first housing loan, but ONLY if the loan runs no more than
//          30 years AND finishes by age 65. Breach either and the ceiling drops to 55%
//          and the minimum cash portion doubles from 5% to 10% of price.
//   BSD    Marginal brackets on the higher of price or market value. ABSD sits on top
//          and is due within 14 days of signing, in cash, and cannot be borrowed.
//
// The consequence worth seeing: usable tenure is min(30, 65 − age), so every year of age
// past 35 shortens the loan one-for-one and raises the income needed to carry the same
// home. Nothing about the property changes. This is why the tool takes an age.
//
// What this deliberately does NOT do: it does not value anything, does not forecast, and
// does not tell anyone what they can "afford" in the sense of what is wise. It computes
// what the published rules demand. Whether a household should sit at the ceiling those
// rules allow is a different question and not one arithmetic can answer.

export interface Rules {
  tdsr: number;          // 0.55
  stressRate: number;    // 0.04
  ltvFull: number;       // 0.75
  ltvReduced: number;    // 0.55
  cashMinFull: number;   // 0.05
  cashMinReduced: number;// 0.10
  tenureCap: number;     // 30 years
  ageCap: number;        // loan must end by 65
  legalFees: number;     // conventional allowance, not a quote
}

export const RULES: Rules = {
  tdsr: 0.55, stressRate: 0.04,
  ltvFull: 0.75, ltvReduced: 0.55,
  cashMinFull: 0.05, cashMinReduced: 0.10,
  tenureCap: 30, ageCap: 65,
  legalFees: 3000,
};

/** IRAS Buyer's Stamp Duty, residential, rates effective 15 Feb 2023. Marginal brackets.
 *  Checkpoints: 1.0m -> 24,600 · 1.5m -> 44,600 · 2.0m -> 69,600. */
export function bsd(price: number): number {
  const brackets: [number, number][] = [
    [180_000, 0.01], [360_000, 0.02], [1_000_000, 0.03],
    [1_500_000, 0.04], [3_000_000, 0.05], [Infinity, 0.06],
  ];
  let duty = 0, prev = 0;
  for (const [cap, rate] of brackets) {
    const band = Math.max(0, Math.min(price, cap) - prev);
    duty += band * rate;
    prev = cap;
    if (price <= cap) break;
  }
  return duty;
}

/** IRAS Additional Buyer's Stamp Duty, rates effective 27 Apr 2023.
 *  Index is the property count: [first, second, third or more]. */
export const ABSD: Record<string, number[]> = {
  SC: [0, 0.20, 0.30],
  PR: [0.05, 0.30, 0.35],
  Foreigner: [0.60, 0.60, 0.60],
};

/** Level monthly payment on an amortising loan. */
export function instalment(principal: number, annualRate: number, years: number): number {
  if (principal <= 0 || years <= 0) return 0;
  const r = annualRate / 12, n = years * 12;
  return r === 0 ? principal / n : (principal * r) / (1 - Math.pow(1 + r, -n));
}

export interface Inputs {
  psf: number; sqft: number; age: number;
  profile: keyof typeof ABSD; count: 1 | 2 | 3;
  packageRate: number;   // what you would actually pay, for contrast only
}

export interface Result {
  price: number; tenure: number; ltv: number;
  loan: number; downpayment: number; minCash: number;
  bsd: number; absd: number; upfront: number;
  incomeNeeded: number;      // gross monthly household income to clear TDSR at the floor
  actualInstalment: number;  // at the package rate, once you have qualified
  stressInstalment: number;  // what the bank tests you on
}

export function compute(i: Inputs, R: Rules = RULES): Result {
  const price = i.psf * i.sqft;

  // Usable tenure for the FULL ceiling: no more than 30 years, and finished by 65. We
  // always solve for the full ceiling, so tenure is the variable that gives way — that
  // is the choice most buyers actually make. Taking a LONGER loan instead is allowed and
  // simply drops you to the reduced ceiling; that path is atReducedLtv() below, and the
  // tool shows both rather than pretending only one exists.
  const tenure = Math.max(1, Math.min(R.tenureCap, R.ageCap - i.age));
  const ltv = R.ltvFull;

  const loan = price * ltv;
  const downpayment = price - loan;
  const minCash = price * R.cashMinFull;
  const duty = bsd(price);
  const absd = price * (ABSD[i.profile]?.[i.count - 1] ?? 0);

  const stressInstalment = instalment(loan, R.stressRate, tenure);
  return {
    price, tenure, ltv, loan, downpayment, minCash,
    bsd: duty, absd,
    upfront: downpayment + duty + absd + R.legalFees,
    incomeNeeded: stressInstalment / R.tdsr,
    actualInstalment: instalment(loan, i.packageRate, tenure),
    stressInstalment,
  };
}

/** The same purchase at the reduced ceiling — what a longer loan, or one running past
 *  65, actually costs you in cash at the front. */
export function atReducedLtv(i: Inputs, R: Rules = RULES): { loan: number; upfront: number } {
  const price = i.psf * i.sqft;
  const loan = price * R.ltvReduced;
  const absd = price * (ABSD[i.profile]?.[i.count - 1] ?? 0);
  return { loan, upfront: price - loan + bsd(price) + absd + R.legalFees };
}

/** Compound annual growth the district must deliver over `years` for a buyer entering at
 *  `psf` to sell at their own entry price, after round-trip costs. Not a forecast — a
 *  hurdle rate implied by the entry price and the comparable that exists today. */
export function breakEvenCagr(psf: number, comparablePsf: number, years = 9, roundTrip = 0.06): number {
  return Math.pow((psf * (1 + roundTrip)) / comparablePsf, 1 / years) - 1;
}

/** District 20 resale median $psf by size band, twelve months to Aug 2026 (URA, our own
 *  computation). Bands mirror the pipeline: <600, 600-850, 850-1150, >=1150 sq ft. */
export const D20_BAND_PSF = [1966, 2205, 2042, 1763];
export function bandOf(sqft: number): number {
  return sqft < 600 ? 0 : sqft < 850 ? 1 : sqft < 1150 ? 2 : 3;
}
