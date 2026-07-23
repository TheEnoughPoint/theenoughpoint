// ─── Types ────────────────────────────────────────────────────────────────────
// Dummy / placeholder partner data. All CTAs are non-functional ("#") and no
// real partner logos are used — names are rendered as styled wordmark text to
// avoid trademark/asset-licensing issues. Replace with real, contracted
// partners (and real disclosure terms) before launch.

export interface Partner {
  id:            string;
  name:          string;
  category:      'bank' | 'brokerage' | 'robo' | 'comparison';
  /** Short description used in cards (sidebar / homepage strip) */
  blurb:         string;
  /** Small highlight badge, e.g. "Up to 5.00% p.a." */
  badge?:        string;
  /** Used by ProductComparisonTable */
  bestFor?:      string;
  fees?:         string;
  /** Out of 5, used by ProductComparisonTable */
  rating?:       number;
  ctaLabel:      string;
  ctaHref:       string;
  /** Tailwind text-color class for the styled wordmark badge */
  wordmarkClass: string;
}

// ─── Partners Registry ─────────────────────────────────────────────────────────

export const partners: Partner[] = [
  {
    id: 'uob', name: 'UOB', category: 'bank',
    blurb: 'UOB ONE Account — up to 5.00% p.a. on your savings.',
    badge: 'Up to 5.00% p.a.',
    ctaLabel: 'Learn More', ctaHref: '#',
    wordmarkClass: 'text-red-700',
  },
  {
    id: 'dbs', name: 'DBS/POSB', category: 'bank',
    blurb: 'DBS/POSB Everyday Card — up to 10% cashback on essentials.',
    badge: 'Up to 10% cashback',
    ctaLabel: 'Learn More', ctaHref: '#',
    wordmarkClass: 'text-red-600',
  },
  {
    id: 'moomoo', name: 'moomoo SG', category: 'brokerage',
    blurb: 'Free Apple shares* with qualifying deposit.',
    badge: 'Free shares*',
    ctaLabel: 'Learn More', ctaHref: '#',
    wordmarkClass: 'text-orange-500',
  },
  {
    id: 'ibkr', name: 'Interactive Brokers', category: 'brokerage',
    blurb: 'Low-cost global investing. Access 150+ markets.',
    bestFor: 'Global market access', fees: 'From US$0 commission', rating: 4.6,
    ctaLabel: 'Learn more', ctaHref: '#',
    wordmarkClass: 'text-red-600',
  },
  {
    id: 'syfe', name: 'Syfe', category: 'robo',
    blurb: 'Automated investing powered by ETFs.',
    bestFor: 'Hands-off investing', fees: '0.35%–0.65% p.a.', rating: 4.4,
    ctaLabel: 'Learn more', ctaHref: '#',
    wordmarkClass: 'text-indigo-600',
  },
  {
    id: 'endowus', name: 'Endowus', category: 'robo',
    blurb: 'Cash Smart & CPF investing. Low fees, high transparency.',
    bestFor: 'CPF/SRS investing', fees: '0.25%–0.60% p.a.', rating: 4.5,
    ctaLabel: 'Learn more', ctaHref: '#',
    wordmarkClass: 'text-blue-700',
  },
  {
    id: 'tiger', name: 'Tiger Brokers', category: 'brokerage',
    blurb: 'Invest in US, HK & SG. Low commissions.',
    bestFor: 'Multi-market, low fees', fees: 'From S$2.88 flat', rating: 4.3,
    ctaLabel: 'Learn more', ctaHref: '#',
    wordmarkClass: 'text-orange-600',
  },
  {
    id: 'singsaver', name: 'SingSaver', category: 'comparison',
    blurb: 'Compare insurance, cards, loans & more.',
    bestFor: 'Comparing financial products', rating: 4.2,
    ctaLabel: 'Learn more', ctaHref: '#',
    wordmarkClass: 'text-emerald-600',
  },
];

export function getPartners(ids: string[]): Partner[] {
  return ids
    .map((id) => partners.find((p) => p.id === id))
    .filter((p): p is Partner => Boolean(p));
}
