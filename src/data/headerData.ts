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
    src:   '/img/logo.png',
    alt:   'TheEnoughPoint.com',
    width: 120,
  },

  navMenu: pillars.map((p) => ({ label: p.navLabel, href: `/${p.id}` })),

  copyright: 'Copyright 2026 TheEnoughPoint.com',
};
