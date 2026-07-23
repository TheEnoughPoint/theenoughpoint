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

export interface FooterAppButton {
  icon:     string;
  caption:  string;
  label:    string;
  href:     string;
}

export interface FooterAppData {
  title:       string;
  description: string;
  buttons:     FooterAppButton[];
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

export const defaultFooterData: FooterData = {
  about: {
    logoSrc:     '/img/logo.png',
    logoAlt:     'Logo',
    description: 'Delivering accurate, balanced, and timely news from every corner of the world.',
    socials: [
      { icon: 'bi:facebook',  label: 'Facebook',  href: '#' },
      { icon: 'bi:twitter-x', label: 'X',         href: '#' },
      { icon: 'bi:instagram', label: 'Instagram', href: '#' },
      { icon: 'bi:youtube',   label: 'YouTube',   href: '#' },
      { icon: 'bi:linkedin',  label: 'LinkedIn',  href: '#' },
    ],
  },

  menus: [
    {
      title: 'Explore',
      links: [
        { label: 'News',          href: '/news' },
        { label: 'Travel',        href: '/travel' },
        { label: 'Technology',    href: '/technology' },
        { label: 'Business',      href: '/business' },
        { label: 'Entertainment', href: '/entertainment' },
        { label: 'Sports',        href: '/sports' },
        { label: 'Lifestyle',     href: '/lifestyle' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { label: 'About Us',    href: '/about' },
        { label: 'Contact Us',  href: '/contact' },
        { label: 'Newsletter',  href: '#' },
        { label: 'Sitemap',     href: '#' },
        { label: 'Advertise',   href: '#' },
        { label: 'Careers',     href: '#' },
        { label: 'Press Room',  href: '#' },
      ],
    },
    {
      title: 'Services',
      links: [
        { label: 'Video',       href: '#' },
        { label: 'Podcasts',    href: '#' },
        { label: 'E-Paper',     href: '#' },
        { label: 'Archive',     href: '#' },
        { label: 'RSS Feeds',   href: '#' },
        { label: 'Mobile App',  href: '#' },
      ],
    },
  ],

  app: {
    title:       'Top Stories in Your Inbox',
    description: 'Join thousands of readers and never miss important news.',
    buttons: [
      { icon: 'bi:apple',       caption: 'Download on the', label: 'App Store',   href: '#' },
      { icon: 'bi:google-play', caption: 'GET IT ON',       label: 'Google Play', href: '#' },
    ],
  },

  copyright: {
    text: '© 2026 Portal. All rights reserved.',
    links: [
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms of Use',   href: '/terms'   },
      { label: 'Cookie Policy',  href: '/cookies'  },
    ],
  },
};
