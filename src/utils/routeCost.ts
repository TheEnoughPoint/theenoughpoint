// Route-cost arithmetic — the total cost of owning S$X of gold exposure for
// N years, by route, with no price path assumed.
//
// This module is the canonical derivation. RouteCostTool.astro mirrors it in an
// inline script so the page works without a client bundle; if you change one,
// change both.
//
// Derivation notes
// ----------------
// Every route reduces to a triplet of fractions of the amount:
//   entry  — paid once going in (dealer premium/spread, brokerage, FX)
//   annual — paid every year held (storage and insurance, account fee, TER)
//   exit   — paid once coming out (sell spread, brokerage, FX)
// Total cost over N years on a constant notional A:
//   cost = A × (entry + annual × N + exit)
// Costs are charged on a CONSTANT notional deliberately: introducing a price
// path would smuggle a return assumption into a cost comparison, and the whole
// point of the tool is that cost is the only dimension it can know. The
// consequence to state honestly: in reality annual fees are charged on value,
// not notional, so a route's true cost scales with how the price actually goes
// — this is a comparison of fee STRUCTURES, not a bill forecast.
//
// The teaching point the arithmetic produces by itself: entry/exit costs are
// horizon-independent while annual costs scale with N, so the cheapest route
// flips with holding period — spreads punish short holdings, running fees
// punish long ones. The crossover between two routes (e1,a1,x1) and (e2,a2,x2)
// sits at N* = ((e2+x2) − (e1+x1)) / (a1 − a2) years.

export interface Route {
  key: string;
  label: string;
  entry: number;  // fraction, e.g. 0.02
  annual: number; // fraction per year
  exit: number;   // fraction
}

export interface RouteCost {
  key: string;
  entryCost: number;  // S$
  runCost: number;    // S$ over the horizon
  exitCost: number;   // S$
  total: number;      // S$
  totalPct: number;   // fraction of amount
}

export function computeRouteCosts(amount: number, years: number, routes: Route[]): RouteCost[] {
  return routes.map((r) => {
    const entryCost = amount * r.entry;
    const runCost = amount * r.annual * years;
    const exitCost = amount * r.exit;
    const total = entryCost + runCost + exitCost;
    return { key: r.key, entryCost, runCost, exitCost, total, totalPct: amount > 0 ? total / amount : 0 };
  });
}
