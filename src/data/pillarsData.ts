// ─── Types ────────────────────────────────────────────────────────────────────

export interface PillarChild {
  /** Category slug — must match blog frontmatter `category` and URL paths */
  id:           string;
  /** Nav/footer label for this sub-category */
  label:        string;
  /** Shown as the category page's intro/tagline. Falls back to a generic
   *  line (see [category]/index.astro) if omitted. */
  description?: string;
}

export interface Pillar {
  /** Category slug used for the parent's own link (homepage tile, nav label
   *  link) — deliberately chosen per group below, not always the first child. */
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
// Single source of truth for the nav structure — feeds Header nav (parent
// label links + dropdown for grouped pillars), homepage pillar tiles, and
// Footer's Explore menu (flattened to leaf categories). Category pages for
// every child below are generated even with zero posts (see
// [category]/index.astro), so new sub-categories render an "empty" page
// with their description rather than 404ing.

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
      {
        id:          'educational',
        label:       'Educational',
        description: "Educational dashboards for your personal and your child's learning — because of how much we wish our parents gave us lessons on finance when we were younger, we wouldn't have spent so much on arcade games!",
      },
      {
        id:          'real-world-tools',
        label:       'Real-World Tools',
        description: 'Real world money tools we use to reach our enough points.',
      },
    ],
  },
  {
    id:          'real-stories',
    navLabel:    'Stories Over Coffee',
    tileTitle:   'Stories Over Coffee',
    description: 'Real side hustles and true stories of success from Singapore.',
    icon:        'bi:flask',
    authorId:    're',
    children: [
      { id: 'optional-income', label: 'Side Hustles' },
      {
        id:          'real-stories',
        label:       'Real Stories of True Successes in SG',
        description: 'Real inspirational stories of true successes in SG, curated from our personal experiences, friends, friends of friends and so on — sharing how many walked the path may inspire you to create your own!',
      },
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

/** Every leaf category (id, label, description) across all pillars, used to
 *  seed category pages for sub-categories that have no posts yet. */
export const leafCategories = pillars.flatMap((p) =>
  p.children.length > 0
    ? p.children
    : [{ id: p.id, label: p.navLabel, description: p.description }]
);

export function getPillar(id: string): Pillar | undefined {
  return pillars.find((p) => p.id === id || p.children.some((c) => c.id === id));
}
