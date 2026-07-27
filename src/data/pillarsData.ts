// ─── Types ────────────────────────────────────────────────────────────────────

export interface PillarChild {
  /** Category slug — must match blog frontmatter `category` and URL paths */
  id:    string;
  /** Nav/footer label for this sub-category */
  label: string;
}

export interface Pillar {
  /** Category slug used for the parent's own link (homepage tile, footer
   *  fallback) — the first child's id for grouped pillars, or the pillar's
   *  own slug when it has no children. */
  id:          string;
  /** Header nav label (top-level) */
  navLabel:    string;
  /** Homepage pillar tile heading */
  tileTitle:   string;
  /** Homepage pillar tile description */
  description: string;
  /** astro-icon name */
  icon:        string;
  /** Which pseudonymous author owns this pillar editorially, if singular */
  authorId?:   'fi' | 're';
  /** Sub-categories shown as a nav dropdown. Empty = no dropdown, just a direct link. */
  children:    PillarChild[];
}

// ─── Pillars Registry ─────────────────────────────────────────────────────────
// Single source of truth for the nav structure — feeds Header nav (with
// dropdowns for grouped pillars), homepage pillar tiles, and Footer's
// Explore menu (flattened to leaf categories).
//
// "Tools We Use" and "Stories Over Coffee" > "Real Stories of true successes
// in SG" are new categories with no existing content yet — their pages will
// 404 until at least one article is published under them.

export const pillars: Pillar[] = [
  {
    id:          'build-enough',
    navLabel:    'Your Enough Point',
    tileTitle:   'Your Enough Point',
    description: 'Age-based guides for every stage of your journey.',
    icon:        'bi:compass',
    authorId:    'fi',
    children: [
      { id: 'build-enough',  label: 'Build Enough' },
      { id: 'invest-better', label: 'Invest Better' },
    ],
  },
  {
    id:          'educational',
    navLabel:    'Tools We Use',
    tileTitle:   'Tools We Use',
    description: 'Honest reviews and real calculators to help you make better money decisions.',
    icon:        'bi:search',
    children: [
      { id: 'educational',       label: 'Educational' },
      { id: 'real-world-tools',  label: 'Real-World Tools' },
    ],
  },
  {
    id:          'optional-income',
    navLabel:    'Stories Over Coffee',
    tileTitle:   'Stories Over Coffee',
    description: 'Real side hustles and true stories of success from Singapore.',
    icon:        'bi:flask',
    authorId:    're',
    children: [
      { id: 'optional-income', label: 'Side Hustles' },
      { id: 'real-stories',    label: 'Real Stories of True Successes in SG' },
    ],
  },
  {
    id:          'spend-with-value',
    navLabel:    'Value Hunts',
    tileTitle:   'Value Hunts',
    description: 'Spend less, live better. Smart cheap hunts & tips.',
    icon:        'bi:tags',
    authorId:    're',
    children: [],
  },
];

export function getPillar(id: string): Pillar | undefined {
  return pillars.find((p) => p.id === id || p.children.some((c) => c.id === id));
}
