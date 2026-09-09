// The arithmetic behind the "Enough Point Check" tool
// (src/components/enough/EnoughPointCheck.astro — see that file for the UI,
// this module for the derivation. If you change one, change both.)
//
// Everything is stored and calculated in integer cents so 0.10 + 0.20 lands
// on exactly 0.30, not 0.30000000000000004. Display formatting (dividing by
// 100, adding "S$") is the component's job, not this module's.

export interface IncomeRow {
  id: string;
  label: string;
  /** Monthly amount, integer cents. Always >= 0 — validation happens before
   *  a row reaches this module. */
  cents: number;
  /** Would this income keep arriving if the reader stopped doing the work
   *  that currently produces it? Not "is it currently passive" — a salary
   *  and a side-hustle both default to false; the reader has to say yes. */
  continuesWithoutWork: boolean;
}

export interface ExpenseRow {
  id: string;
  label: string;
  cents: number;
}

export type Scenario = 'current' | 'withoutWork';

export interface EnoughPointResult {
  currentIncome: number;
  continuingIncome: number;
  expenses: number;
  currentBalance: number;
  withoutWorkBalance: number;
  selectedIncome: number;
  selectedBalance: number;
  /** Percent, e.g. 226.7 for 226.7%. null when expenses are zero — a ratio
   *  against nothing isn't a coverage figure, it's a divide-by-zero wearing
   *  a costume. */
  coveragePercent: number | null;
}

const sumCents = (rows: { cents: number }[]): number =>
  rows.reduce((total, r) => total + Math.round(r.cents), 0);

export function calculate(
  income: IncomeRow[],
  expenses: ExpenseRow[],
  scenario: Scenario,
): EnoughPointResult {
  const currentIncome = sumCents(income);
  const continuingIncome = sumCents(income.filter((r) => r.continuesWithoutWork));
  const expensesTotal = sumCents(expenses);
  const currentBalance = currentIncome - expensesTotal;
  const withoutWorkBalance = continuingIncome - expensesTotal;
  const selectedIncome = scenario === 'current' ? currentIncome : continuingIncome;
  const selectedBalance = selectedIncome - expensesTotal;
  const coveragePercent = expensesTotal > 0 ? (selectedIncome / expensesTotal) * 100 : null;

  return {
    currentIncome,
    continuingIncome,
    expenses: expensesTotal,
    currentBalance,
    withoutWorkBalance,
    selectedIncome,
    selectedBalance,
    coveragePercent,
  };
}

/**
 * Which of the result's fixed messages applies, evaluated in the order the
 * editorial brief specifies. `headline` reflects the scenario the reader is
 * currently looking at; `crossScenario` is the always-on "here's the other
 * side" line (only set for the two cases the brief calls out — a working
 * surplus that turns into a gap or an exact break-even once work income is
 * removed). Neither slot ever says "retire now" or grades the reader.
 */
export type HeadlineTier =
  | 'no-expenses'
  | 'gap'
  | 'breakeven'
  | 'surplus-working'
  | 'covers-without-work';

export type CrossScenarioTier = 'surplus-to-gap' | 'surplus-to-breakeven' | null;

export interface ResultTiers {
  headline: HeadlineTier;
  crossScenario: CrossScenarioTier;
}

export function classify(r: EnoughPointResult, scenario: Scenario): ResultTiers {
  let headline: HeadlineTier;
  if (r.expenses <= 0) {
    headline = 'no-expenses';
  } else if (r.selectedBalance < 0) {
    headline = 'gap';
  } else if (r.selectedBalance === 0) {
    headline = 'breakeven';
  } else if (scenario === 'withoutWork') {
    headline = 'covers-without-work';
  } else {
    headline = 'surplus-working';
  }

  let crossScenario: CrossScenarioTier = null;
  if (r.expenses > 0 && r.currentBalance > 0) {
    if (r.withoutWorkBalance < 0) crossScenario = 'surplus-to-gap';
    else if (r.withoutWorkBalance === 0) crossScenario = 'surplus-to-breakeven';
  }

  return { headline, crossScenario };
}

/** Cents -> "S$1,234" (or "-S$1,234" for a shortfall). No decimals — every
 *  amount in this tool is a monthly round figure, and cents of precision in
 *  the display would imply a false exactness the inputs don't have. */
export function formatSgd(cents: number): string {
  const sign = cents < 0 ? '-' : '';
  const dollars = Math.round(Math.abs(cents) / 100);
  return sign + 'S$' + dollars.toLocaleString('en-SG');
}

export function formatCoverage(percent: number | null): string {
  if (percent === null) return '—';
  return (Math.round(percent * 10) / 10).toFixed(1) + '%';
}

/** Parse a free-typed amount into non-negative integer cents, or null if
 *  the field is invalid (negative, NaN, Infinity) — the caller shows a
 *  validation state rather than silently coercing to zero. Accepts thousands
 *  separators and an optional leading "S$". */
export function parseAmountToCents(raw: string): number | null {
  const cleaned = raw.replace(/[,\s]/g, '').replace(/^S?\$/i, '');
  if (cleaned === '') return 0;
  if (!/^\d+(\.\d{1,2})?$/.test(cleaned)) return null;
  const value = Number(cleaned);
  if (!Number.isFinite(value) || value < 0) return null;
  return Math.round(value * 100);
}
