// ─── Standing tools ──────────────────────────────────────────────────────────
// The site's own free utilities — pages kept current after the articles that
// spawned them age. Drives ToolsWidget (sidebar); one entry per tool so new
// tools are a data change, not a markup change.
//
// Not to be confused with partnersData.ts, which is the affiliate "Partner
// Offers" inventory. Nothing here is monetised, which is the point of keeping
// the two lists apart.

export interface ToolEntry {
  name: string;
  href: string;
  blurb: string;
  /** astro-icon name from the bi set (must be in astro.config's include list) */
  icon: string;
}

export const tools: ToolEntry[] = [
  {
    name: 'The Singapore cashback calendar',
    href: '/cashback-calendar/',
    blurb:
      'When the next upsized window lands — the payday rhythm, the double-digit days, and a dated log of observed rates.',
    icon: 'bi:calendar',
  },
  {
    name: 'Compare three condominiums',
    // No project or district count in the blurb: both are recomputed from URA's record on a
    // weekly refresh, and this file is static, so a number here would drift silently.
    href: '/condo-compare/',
    blurb:
      'Three buildings side by side on price per square foot, resales in the year, lease left, the walk to MRT and how each stands against its own district.',
    icon: 'bi:house-door',
  },
];
