// Run: node --test src/utils/enoughPointCheck.test.ts
// Each test names the reader-facing failure it exists to prevent — see the
// "Required automated calculation tests" table in the editorial handoff for
// the source of each case.

import test from 'node:test';
import assert from 'node:assert/strict';
import {
  calculate, classify, formatSgd, formatCoverage, parseAmountToCents,
  type IncomeRow, type ExpenseRow,
} from './enoughPointCheck.ts';

const inc = (cents: number, continuesWithoutWork = false, id = 'i', label = 'income'): IncomeRow =>
  ({ id, label, cents, continuesWithoutWork });
const exp = (cents: number, id = 'e', label = 'expense'): ExpenseRow =>
  ({ id, label, cents });

test('all blank/zero: no success, no divide-by-zero', () => {
  const r = calculate([], [], 'current');
  assert.equal(r.expenses, 0);
  assert.equal(r.coveragePercent, null, 'coverage against zero expenses must not be a number');
  assert.equal(classify(r, 'current').headline, 'no-expenses');
});

test('expenses 2,000; no income: both balances -2,000', () => {
  const expenses = [exp(200000)];
  const current = calculate([], expenses, 'current');
  const without = calculate([], expenses, 'withoutWork');
  assert.equal(current.currentBalance, -200000);
  assert.equal(without.withoutWorkBalance, -200000);
  assert.equal(classify(current, 'current').headline, 'gap');
});

test('salary 5,000; expenses 3,000: current +2,000, without-work -3,000', () => {
  const income = [inc(500000, false)];
  const expenses = [exp(300000)];
  const r = calculate(income, expenses, 'current');
  assert.equal(r.currentBalance, 200000);
  assert.equal(r.withoutWorkBalance, -300000);
});

test('gig income 4,000 with the "continues" flag off is NOT independent of work', () => {
  // The regression this guards: classifying income as passive because it
  // isn't literally called "salary", rather than by the flag the reader set.
  const income = [inc(400000, false, 'gig', 'Gig income')];
  const expenses = [exp(200000)];
  const r = calculate(income, expenses, 'current');
  assert.equal(r.currentBalance, 200000);
  assert.equal(r.withoutWorkBalance, -200000, 'unflagged income must vanish in the without-work scenario');
});

test('continuing income 2,000; expenses 2,000: break-even, no buffer', () => {
  const income = [inc(200000, true)];
  const expenses = [exp(200000)];
  const r = calculate(income, expenses, 'withoutWork');
  assert.equal(r.selectedBalance, 0);
  assert.equal(classify(r, 'withoutWork').headline, 'breakeven');
});

test('continuing income 2,500; expenses 2,000: +500, not a retirement certification', () => {
  const income = [inc(250000, true)];
  const expenses = [exp(200000)];
  const r = calculate(income, expenses, 'withoutWork');
  assert.equal(r.selectedBalance, 50000);
  assert.equal(classify(r, 'withoutWork').headline, 'covers-without-work');
});

test('custom income 1,000 toggled off then on: without-work income moves by exactly 1,000, current unchanged', () => {
  const base = [inc(500000, false, 'salary')];
  const withCustomOff = [...base, inc(100000, false, 'custom-1', 'Custom')];
  const withCustomOn = [...base, inc(100000, true, 'custom-1', 'Custom')];
  const expenses = [exp(100000)];

  const off = calculate(withCustomOff, expenses, 'withoutWork');
  const on = calculate(withCustomOn, expenses, 'withoutWork');
  assert.equal(on.continuingIncome - off.continuingIncome, 100000);

  const offCurrent = calculate(withCustomOff, expenses, 'current');
  const onCurrent = calculate(withCustomOn, expenses, 'current');
  assert.equal(offCurrent.currentIncome, onCurrent.currentIncome, 'the flag must not touch the current-scenario total');
});

test('deleting a custom expense of 100 improves both balances by exactly 100', () => {
  const income = [inc(500000, true)];
  const before = [exp(200000, 'rent'), exp(10000, 'custom-1')];
  const after = [exp(200000, 'rent')];
  const rBefore = calculate(income, before, 'current');
  const rAfter = calculate(income, after, 'current');
  assert.equal(rAfter.currentBalance - rBefore.currentBalance, 10000);
  assert.equal(rAfter.withoutWorkBalance - rBefore.withoutWorkBalance, 10000);
});

test('0.10 + 0.20 income against 0.30 expenses is exactly break-even', () => {
  // The reason everything downstream of parseAmountToCents is integer cents:
  // in floating dollars this is 0.30000000000000004, not a clean zero.
  const c1 = parseAmountToCents('0.10')!;
  const c2 = parseAmountToCents('0.20')!;
  const income = [inc(c1, true, 'a'), inc(c2, true, 'b')];
  const expenses = [exp(parseAmountToCents('0.30')!)];
  const r = calculate(income, expenses, 'withoutWork');
  assert.equal(r.selectedBalance, 0);
});

test('negative, non-finite or malformed input fails to parse rather than computing something misleading', () => {
  assert.equal(parseAmountToCents('-50'), null);
  assert.equal(parseAmountToCents('abc'), null);
  assert.equal(parseAmountToCents('Infinity'), null);
  assert.equal(parseAmountToCents('NaN'), null);
  assert.equal(parseAmountToCents('1e999'), null, 'a string that parses to Infinity must not slip through');
});

test('an amount above the initial slider maximum is preserved, not silently capped', () => {
  // This module never clamps to a UI slider's max — it stores whatever
  // valid amount it's given. The component is responsible for widening the
  // slider; this test is here so nobody "fixes" the module into clamping.
  const big = parseAmountToCents('75,000')!;
  assert.equal(big, 7500000);
  const r = calculate([inc(big, false)], [], 'current');
  assert.equal(r.currentIncome, big);
});

test('switching scenarios repeatedly causes no mutation or lost inputs', () => {
  const income = [inc(500000, false, 'salary'), inc(150000, true, 'rental')];
  const expenses = [exp(300000)];
  const snapshotIncome = JSON.stringify(income);
  for (let i = 0; i < 5; i++) {
    calculate(income, expenses, i % 2 === 0 ? 'current' : 'withoutWork');
  }
  assert.equal(JSON.stringify(income), snapshotIncome, 'calculate() must not mutate its inputs');
});

test('worked example from the article: 226.7% current coverage, 60% without-work', () => {
  const income = [
    inc(500000, false, 'salary', 'Salary'),
    inc(150000, true, 'rental', 'Rental income'),
    inc(30000, true, 'dividends', 'Dividends'),
  ];
  const expenses = [exp(300000, 'exp', 'Expenses')];
  const current = calculate(income, expenses, 'current');
  const without = calculate(income, expenses, 'withoutWork');

  assert.equal(current.currentIncome, 680000);
  assert.equal(current.currentBalance, 380000);
  assert.equal(without.continuingIncome, 180000);
  assert.equal(without.withoutWorkBalance, -120000);
  assert.equal(formatCoverage(current.coveragePercent), '226.7%');
  assert.equal(formatCoverage(without.coveragePercent), '60.0%');
});

test('formatSgd renders whole dollars with thousands separators, sign for a shortfall', () => {
  assert.equal(formatSgd(680000), 'S$6,800');
  assert.equal(formatSgd(-120000), '-S$1,200');
  assert.equal(formatSgd(0), 'S$0');
});

test('surplus while working that becomes a gap without work income gets the cross-scenario flag', () => {
  const income = [inc(500000, false)];
  const expenses = [exp(300000)];
  const r = calculate(income, expenses, 'current');
  assert.equal(classify(r, 'current').headline, 'surplus-working');
  assert.equal(classify(r, 'current').crossScenario, 'surplus-to-gap');
});

test('surplus while working that becomes an exact break-even without work income', () => {
  const income = [inc(300000, false, 'a'), inc(300000, true, 'b')];
  const expenses = [exp(300000)];
  const r = calculate(income, expenses, 'current');
  assert.equal(r.withoutWorkBalance, 0);
  assert.equal(classify(r, 'current').crossScenario, 'surplus-to-breakeven');
});
