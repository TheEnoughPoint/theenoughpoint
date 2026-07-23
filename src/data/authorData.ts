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
// FI and RE are TheEnoughPoint's pseudonymous authors (see CLAUDE.md). The
// remaining demo authors below are Astromag theme sample data, kept in place
// but unused by real content.

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
  {
    id:       'adam',
    name:     'Adam',
    fullName: 'Adam Thomson',
    avatar:   '/img/personal/avatar.jpg',
    bio:      'adam is a dynamic individual who embodies the essence of adventure, seamlessly blending her roles as a traveler, blogger, and photographer.',
    href:     '/author/adam',
    website: 'https://example.com/adam',
    socials: [
      { icon: 'bi:facebook',  href: '#', label: 'Facebook'  },
      { icon: 'bi:instagram', href: '#', label: 'Instagram' },
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:linkedin',  href: '#', label: 'LinkedIn'  },
      { icon: 'bi:tiktok',    href: '#', label: 'TikTok'    },
    ],
  },
  {
    id: "james-carter",
    name: "James Carter",
    fullName: "James Carter",
    avatar: "/img/male1.jpg",
    bio:
      "Award-winning journalist with over 12 years of experience covering global sports events and emerging technology trends. Previously with Reuters and The Guardian.",
    href: "/author/james-carter",
    website: "https://example.com/james-carter",
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:linkedin',  href: '#', label: 'LinkedIn'  },
    ],
  },
  {
    id: "priya-nambiar",
    name: "Priya Nambiar",
    fullName: "Priya Nambiar",
    avatar: "/img/female1.jpg",
    bio:
      "Priya covers emerging technologies with a focus on AI policy, ethics, and the societal impact of machine intelligence. Former researcher at MIT Media Lab.",
    href: "/author/priya-nambiar",
    website: "https://example.com/priya-nambiar",
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:linkedin',  href: '#', label: 'LinkedIn'  },
      { icon: 'bi:envelope',   href: 'mailto:priya@astromag.com', label: 'Email' },
    ],
  },
  {
    id: "sophie-delacroix",
    name: "Sophie Delacroix",
    fullName: "Sophie Delacroix",
    avatar: "/img/female2.jpg",
    bio:
      "Sophie writes about the intersection of modern life, culture, and wellbeing. Based between Paris and Bali, she advocates for intentional, design-led living.",
    href: "/author/sophie-delacroix",
    website: "https://example.com/sophie-delacroix",
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:linkedin',  href: '#', label: 'LinkedIn'  },
      { icon: 'bi:instagram', href: '#', label: 'Instagram' },
    ],
  },
  {
    id: "marcus-tan",
    name: "Marcus Tan",
    fullName: "Marcus Tan",
    avatar: "/img/male2.jpg",
    bio:
      "Marcus covers global markets, venture capital, and emerging economies. He has reported from Singapore, Jakarta, Ho Chi Minh City, and Nairobi for over a decade.",
    href: "/author/marcus-tan",
    website: "https://example.com/marcus-tan",
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:linkedin',  href: '#', label: 'LinkedIn'  },
      { icon: 'bi:envelope',   href: 'mailto:marcus@astromag.com', label: 'Email' },
    ],
  },
  {
    id: "amara-osei",
    name: "Amara Osei",
    fullName: "Amara Osei",
    avatar: "/img/female3.jpg",
    bio:
      "Amara has covered international climate negotiations since COP21 in Paris. She has reported from over 30 countries and is a World Press Freedom Award nominee.",
    href: "/author/amara-osei",
    website: "https://example.com/amara-osei",
    socials: [
      { icon: 'bi:twitter-x', href: '#', label: 'Twitter/X' },
      { icon: 'bi:linkedin',  href: '#', label: 'LinkedIn'  },
      { icon: 'bi:envelope',   href: 'mailto:amara@astromag.com', label: 'Email' },
    ],
  },
];

export function getAuthor(id: string): AuthorData {
  return authors.find((a) => a.id === id) ?? authors[0];
}

export const defaultAuthorData: AuthorData = authors[0];
