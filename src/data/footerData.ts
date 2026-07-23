// ─── Types ────────────────────────────────────────────────────────────────────

export interface FooterSocialLink {
  icon:  string;
  label: string;
  href:  string;
}

export interface FooterAboutData {
  logoSrc:     string;
  logoAlt:     string;
  description: string;
  socials:     FooterSocialLink[];
}

export interface FooterMenuLink {
  label: string;
  href:  string;
}

export interface FooterMenuData {
  title: string;
  links: FooterMenuLink[];
}

export interface FooterTrustItem {
  icon:        string;
  label:       string;
  description: string;
}

export interface FooterAppData {
  items: FooterTrustItem[];
}

export interface FooterCopyrightLink {
  label: string;
  href:  string;
}

export interface FooterCopyrightData {
  text:  string;
  links: FooterCopyrightLink[];
}

export interface FooterData {
  about:      FooterAboutData;
  menus:      FooterMenuData[];
  app:        FooterAppData;
  copyright:  FooterCopyrightData;
}

// ─── Default Data ─────────────────────────────────────────────────────────────

import { pillars } from './pillarsData';

export const defaultFooterData: FooterData = {
  about: {
    logoSrc:     '/img/logo.png',
    logoAlt:     'TheEnoughPoint.com',
    description: 'Practical personal finance and lifestyle insights to help Singaporeans reach their own enough point.',
    socials: [
      { icon: 'bi:facebook',  label: 'Facebook',  href: '#' },
      { icon: 'bi:twitter-x', label: 'X',         href: '#' },
      { icon: 'bi:instagram', label: 'Instagram', href: '#' },
      { icon: 'bi:telegram',  label: 'Telegram',  href: '#' },
      { icon: 'bi:linkedin',  label: 'LinkedIn',  href: '#' },
    ],
  },

  menus: [
    {
      title: 'Explore',
      links: pillars.map((p) => ({ label: p.navLabel, href: `/${p.id}` })),
    },
    {
      title: 'Resources',
      links: [
        { label: 'About Us',    href: '/about' },
        { label: 'Contact Us',  href: '/contact' },
        { label: 'FI',          href: '/author/fi' },
        { label: 'RE',          href: '/author/re' },
      ],
    },
    {
      title: 'Compliance',
      links: [
        { label: 'Privacy Policy',  href: '/privacy' },
        { label: 'Terms of Use',    href: '/terms' },
        { label: 'Cookie Policy',   href: '/cookies' },
        { label: 'Editorial Policy', href: '/docs' },
      ],
    },
  ],

  app: {
    items: [
      { icon: 'bi:shield-check',    label: 'Financial Freedom', description: 'Build wealth with confidence.' },
      { icon: 'bi:graph-up-arrow',  label: 'Smart Growth',      description: 'Make informed decisions.' },
      { icon: 'bi:compass',         label: 'Purposeful Path',   description: 'Stay focused on what matters.' },
      { icon: 'bi:trophy',          label: 'Live Your Freedom', description: 'Design the life you want.' },
    ],
  },

  copyright: {
    text: '© 2026 TheEnoughPoint.com. All rights reserved.',
    links: [
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms of Use',   href: '/terms'   },
      { label: 'Cookie Policy',  href: '/cookies'  },
    ],
  },
};
