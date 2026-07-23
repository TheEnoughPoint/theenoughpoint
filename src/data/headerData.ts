// ─── Types ────────────────────────────────────────────────────────────────────

export interface NavDropdownItem {
  label: string;
  href: string;
}

export interface NavMenuItem {
  label: string;
  href?: string;
  children?: NavDropdownItem[];
}

export interface HeaderData {
  logo: {
    src: string;
    alt: string;
    width: number;
  };
  navMenu: NavMenuItem[];
  copyright: string;
}

// ─── Default Data ─────────────────────────────────────────────────────────────

export const defaultHeaderData: HeaderData = {
  logo: {
    src:   '/img/logo.png',
    alt:   'Logo',
    width: 120,
  },

  navMenu: [
    { label: 'Home',          href: '/'         },
    { label: 'Business',      href: '/business'    },
    { label: 'Sports',        href: '/sports'    },
    { label: 'Travel',        href: '/travel'    },
    { label: 'Politics',      href: '/politics'     },
    { label: 'Lifestyle',     href: '/lifestyle' },
    { label: 'Technology',    href: '/technology'    },
    {
      label: 'More',
      children: [
        { label: 'Foods',         href: '/foods'             },
        { label: 'Science',       href: '/science'          },
        { label: 'Entertainment',     href: '/entertainment'           },
        { label: 'News',          href: '/news'           },
        { label: 'Health',        href: '/health'             },
        { label: 'Finance',       href: '/finance'              },
      ],
    },
  ],

  copyright: 'Copyright 2026',
};
