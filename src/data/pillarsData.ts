// ─── Types ────────────────────────────────────────────────────────────────────

export interface Pillar {
  /** Category slug — must match blog frontmatter `category` and URL paths */
  id:          string;
  /** Header / footer nav label */
  navLabel:    string;
  /** Homepage pillar tile heading */
  tileTitle:   string;
  /** Homepage pillar tile description */
  description: string;
  /** astro-icon name */
  icon:        string;
  /** Which pseudonymous author owns this pillar editorially */
  authorId:    'fi' | 're';
}

// ─── Pillars Registry ─────────────────────────────────────────────────────────
// Single source of truth for the 4 content pillars — feeds Header nav,
// homepage pillar tiles, and Footer's Explore menu.

export const pillars: Pillar[] = [
  {
    id:          'build-enough',
    navLabel:    'Freedom Roadmap',
    tileTitle:   'Freedom Roadmap',
    description: 'Age-based guides for every stage of your journey.',
    icon:        'bi:compass',
    authorId:    'fi',
  },
  {
    id:          'invest-better',
    navLabel:    'Money Tools & Reviews',
    tileTitle:   'Money Tools & Reviews',
    description: 'Honest reviews to help you make better money decisions.',
    icon:        'bi:search',
    authorId:    'fi',
  },
  {
    id:          'optional-income',
    navLabel:    'Business Experiments',
    tileTitle:   'Business Experiments',
    description: 'Real side hustles & small business experiments from Singapore.',
    icon:        'bi:flask',
    authorId:    're',
  },
  {
    id:          'spend-with-value',
    navLabel:    'Value Living',
    tileTitle:   'Value Living',
    description: 'Spend less, live better. Smart cheap hunts & tips.',
    icon:        'bi:tags',
    authorId:    're',
  },
];

export function getPillar(id: string): Pillar | undefined {
  return pillars.find((p) => p.id === id);
}
