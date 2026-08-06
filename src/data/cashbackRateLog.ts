// ─── Observed cashback rates, dated ──────────────────────────────────────────
// The memory behind /cashback-calendar's rate table. Rate pages show today and
// remember nothing; this file is the history nobody else in Singapore keeps.
//
// Append-only, in chronological order: every time a ShopBack rate is verified
// for a piece or a real booking, add one reading at the end with the date it
// was read. Never edit an old reading to "correct" it — a reading is what the
// page said on that day, and the drift is the point.

export interface RateReading {
  /** ISO date the rate was read off the page or dashboard (YYYY-MM-DD) */
  date: string;
  /** Store name as ShopBack lists it */
  store: string;
  /** The tier the rate applies to, as the merchant page names it */
  tier: string;
  /** Display rate, e.g. "14%" — a string because rates come in odd shapes
   *  ("up to S$35" for flat-amount insurance offers) */
  rate: string;
  /** everyday = the standing rate on the merchant page;
   *  upsized  = a campaign window we actually caught, not a ceiling */
  kind: 'everyday' | 'upsized';
  /** One line of context: what was running, or what we did with it */
  note: string;
  /** Where the reading came from — a merchant page, or our own dashboard */
  source: { label: string; href: string };
}

export const rateLog: RateReading[] = [
  {
    date: '2026-07-25',
    store: 'Trip.com',
    tier: 'hotels',
    rate: '14%',
    kind: 'upsized',
    note: 'Payday-window upsize, roughly three times the everyday 4.5% — our S$468.01 stay returned S$65.52.',
    source: { label: 'our booking, in the routing guide', href: '/shopback-used-properly/' },
  },
  {
    date: '2026-08-06',
    store: 'Booking.com',
    tier: 'stays',
    rate: '5.5%',
    kind: 'everyday',
    note: 'Confirms up to 70 days after the trip ends.',
    source: { label: 'merchant page', href: 'https://www.shopback.sg/booking-com' },
  },
  {
    date: '2026-08-06',
    store: 'Trip.com',
    tier: 'hotels',
    rate: '4.5%',
    kind: 'everyday',
    note: 'Confirms up to 120 days after the trip ends.',
    source: { label: 'merchant page', href: 'https://www.shopback.sg/trip-com' },
  },
  {
    date: '2026-08-06',
    store: 'Agoda',
    tier: 'hotels',
    rate: '4.5%',
    kind: 'everyday',
    note: 'Confirms up to 120 days after the trip ends.',
    source: { label: 'merchant page', href: 'https://www.shopback.sg/agoda' },
  },
  {
    date: '2026-08-06',
    store: 'Klook',
    tier: 'hotels',
    rate: '6%',
    kind: 'everyday',
    note: 'The fattest everyday hotel rate of the four portals; confirms up to 120 days after the trip ends.',
    source: { label: 'merchant page', href: 'https://www.shopback.sg/klook' },
  },
];
