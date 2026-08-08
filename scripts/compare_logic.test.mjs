// Tests for the comparison's decision rules. Run: node --test scripts/
//
// Each test names the failure it exists to prevent. Two of them are regressions that actually
// shipped and were caught by reading the page rather than by any check — those are marked.

import test from 'node:test';
import assert from 'node:assert/strict';
import { CLOSE, RANGE_MIN_N, bandOf, mixedTenure, spreadOf, rankOf, bucket, showRange, tagFor }
  from './compare_logic.mjs';

const psf   = { label: 'price', dir: 'none', kind: 'ratio', val: (r) => r.psf };
const lease = { label: 'lease', dir: 'more', kind: 'ratio', fhAware: true, val: (r) => (r.fh ? Infinity : r.lyr) };
const mrt   = { label: 'mrt',   dir: 'less', kind: 'ratio', val: (r) => r.m };
const vsD   = { label: 'vsd',   dir: 'none', kind: 'pp',    val: (r) => r.psf / r.b - 1 };

const B = (o) => ({ p: 'X', psf: 2000, b: 2000, lyr: 90, fh: 0, m: 300, v: 30, ...o });

test('bandOf matches the upstream boundaries exactly', () => {
  // Divergence here silently changes which benchmark a project is compared against.
  assert.equal(bandOf(599), 0);
  assert.equal(bandOf(600), 1);
  assert.equal(bandOf(849), 1);
  assert.equal(bandOf(850), 2);
  assert.equal(bandOf(1149), 2);
  assert.equal(bandOf(1150), 3);
});

test('REGRESSION: a freehold sentinel must not swallow ordinary values', () => {
  // Shipped bug. The old code treated any value >= 999 as freehold, so price psf, floor area and
  // quantum all scored zero spread — a 2.2x price gap was reported as "much the same".
  const a = B({ psf: 2349 }), b = B({ psf: 1053 });
  assert.ok(spreadOf(psf, [a, b]) > 1.2, 'a 2.2x price gap must register as a large spread');
  assert.equal(rankOf(psf, [a, b], a), 'flat', 'price still has no better end');
});

test('freehold vs leasehold is set aside, not called level', () => {
  // The other half of the same bug: a zero spread would have put it in "much the same", which
  // says 91 years and freehold are alike.
  const fh = B({ fh: 1 }), lh = B({ lyr: 91 });
  assert.equal(mixedTenure([fh, lh]), true);
  assert.equal(spreadOf(lease, [fh, lh]), 0);
  const { setAside, alike } = bucket([psf, lease, mrt], [fh, lh]);
  assert.deepEqual(setAside.map((m) => m.label), ['lease']);
  assert.ok(!alike.some((x) => x.mt.label === 'lease'), 'must not be reported as level');
});

test('all-freehold or all-leasehold is not a mixed set', () => {
  assert.equal(mixedTenure([B({ fh: 1 }), B({ fh: 1 })]), false);
  assert.equal(mixedTenure([B({ lyr: 90 }), B({ lyr: 80 })]), false);
});

test('REGRESSION: every measure lands in exactly one bucket', () => {
  // Shipped bug. The old code sliced the top three and filtered the rest on spread, so a measure
  // that differed but ranked fourth appeared in neither list and vanished from the summary.
  const metrics = [psf, lease, mrt, vsD];
  const picked = [B({ psf: 3000, lyr: 95, m: 100, b: 2000 }),
                  B({ psf: 1500, lyr: 60, m: 800, b: 2600 }),
                  B({ psf: 2200, lyr: 80, m: 400, b: 2100 })];
  const { apart, alsoApart, alike, setAside } = bucket(metrics, picked);
  const seen = [...apart, ...alsoApart, ...alike].map((x) => x.mt.label).concat(setAside.map((m) => m.label));
  assert.equal(seen.length, metrics.length);
  assert.equal(new Set(seen).size, metrics.length, 'no measure counted twice or dropped');
});

test('a level row is never marked, however clear its ordering', () => {
  // 92 / 91 / 90 years is a strict ordering and still not a podium.
  const p = [B({ lyr: 92 }), B({ lyr: 91 }), B({ lyr: 90 })];
  assert.ok(spreadOf(lease, p) < CLOSE);
  assert.equal(rankOf(lease, p, p[0]), 'flat');
  assert.equal(rankOf(lease, p, p[2]), 'flat');
});

test('a direction that runs downwards ranks the smallest value best', () => {
  const p = [B({ m: 900 }), B({ m: 200 }), B({ m: 500 })];
  assert.equal(rankOf(mrt, p, p[1]), 'best');
  assert.equal(rankOf(mrt, p, p[0]), 'worst');
  assert.equal(rankOf(mrt, p, p[2]), 'mid');
});

test('ties share a rank rather than breaking arbitrarily', () => {
  const p = [B({ m: 200 }), B({ m: 200 }), B({ m: 900 })];
  assert.equal(rankOf(mrt, p, p[0]), 'best');
  assert.equal(rankOf(mrt, p, p[1]), 'best');
  assert.equal(rankOf(mrt, p, p[2]), 'worst');
});

test('a single selection is never ranked', () => {
  const p = [B({ m: 200 })];
  assert.equal(rankOf(mrt, p, p[0]), 'flat');
});

test('percentage-point measures are scaled onto the ratio scale', () => {
  // 5pp of spread should read like 25%, so a pp measure can be ranked against a ratio one.
  const p = [B({ psf: 2100, b: 2000 }), B({ psf: 1920, b: 2000 })];
  assert.ok(Math.abs(spreadOf(vsD, p) - 0.45) < 0.01);
});

test('REGRESSION: a mixed-tenure lease row is never tagged level', () => {
  // Shipped bug, twice. A mixed set has a spread of 0, and a component deriving its tag straight
  // from spreadOf therefore called "Freehold against 91 years" level.
  const p = [B({ fh: 1 }), B({ lyr: 91 })];
  assert.equal(tagFor(lease, p), 'different in kind');
});

test('tags distinguish level, no-better-end and not-comparable', () => {
  const level = [B({ lyr: 92 }), B({ lyr: 91 })];
  assert.equal(tagFor(lease, level), 'level');
  assert.equal(tagFor(psf, [B({ psf: 3000 }), B({ psf: 1500 })]), 'no better end');
  const count = { label: 'v', dir: 'none', kind: 'ratio', nomark: 'not size-adjusted', val: (r) => r.v };
  assert.equal(tagFor(count, [B({ v: 60 }), B({ v: 20 })]), 'not size-adjusted');
  assert.equal(tagFor(mrt, [B({ m: 200 }), B({ m: 900 })]), '', 'a ranked, differing row has no tag');
});

test('a price range is withheld below the sample floor', () => {
  assert.equal(showRange({ v: RANGE_MIN_N - 1 }), false);
  assert.equal(showRange({ v: RANGE_MIN_N }), true);
});
