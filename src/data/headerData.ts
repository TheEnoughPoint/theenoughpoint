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

import { pillars } from './pillarsData';

export const defaultHeaderData: HeaderData = {
  logo: {
    src:   '/img/brand/logo-icon-96.png',
    alt:   'TheEnoughPoint.com',
    width: 120,
  },

  navMenu: pillars.map((p) => ({
    label: p.navLabel,
    href:  `/${p.id}`,
    ...(p.children.length > 0
      ? { children: p.children.map((c) => ({ label: c.label, href: `/${c.id}` })) }
      : {}),
  })),

  copyright: 'Copyright 2026 TheEnoughPoint.com',
};
