// ─── Types ────────────────────────────────────────────────────────────────────

export interface AuthorSocialLink {
  icon:  string;
  href:  string;
  label: string;
}

export interface AuthorData {
  id:       string;
  name:     string;
  fullName: string;
  /** Empty string renders a generated monogram avatar (AuthorBio.astro) instead of a photo */
  avatar:   string;
  bio:      string;
  href:     string;
  socials:  AuthorSocialLink[];
  website: string;
  /** Short descriptor line shown under the name, e.g. "Investing, CPF/SRS & Portfolio Frameworks" */
  role?:    string;
}

// ─── Authors Registry ─────────────────────────────────────────────────────────
// FI and RE are TheEnoughPoint's pseudonymous authors (see CLAUDE.md).

export const authors: AuthorData[] = [
  {
    id:       'fi',
    name:     'FI',
    fullName: 'FI',
    avatar:   '',
    role:     'Investing, CPF/SRS & Portfolio Frameworks',
    bio:
      'FI writes about investing, risk, CPF/SRS mechanics, and portfolio frameworks — ' +
      'practical, product-agnostic analysis for readers building toward their own ' +
      'enough point. Views are personal and educational only, and do not reflect the ' +
      'position of any employer.',
    href:     '/author/fi',
    website:  '',
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:telegram',  href: '#', label: 'Telegram'  },
    ],
  },
  {
    id:       're',
    name:     'RE',
    fullName: 'RE',
    avatar:   '',
    role:     'Semi-Retirement, Business Experiments & Value Living',
    bio:
      'RE writes about semi-retirement, small business experiments, side income, and ' +
      'intentional spending — real experiments in building optional income and living ' +
      'well on less. Views are personal and educational only.',
    href:     '/author/re',
    website:  '',
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:telegram',  href: '#', label: 'Telegram'  },
    ],
  },
];

export function getAuthor(id: string): AuthorData {
  return authors.find((a) => a.id === id) ?? authors[0];
}

export const defaultAuthorData: AuthorData = authors[0];
