import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import icon from 'astro-icon';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://theenoughpoint.com',
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [
    mdx(),
    // Google treats redirects, sitemap membership and rel=canonical as one set
    // of signals when choosing which duplicate URL represents a page — the
    // sitemap must therefore carry the same URL forms the canonical tags use.
    // scripts/seo-audit.py asserts that agreement on every build.
    sitemap(),
    icon({
      include: {
        bi: [
          // ── Navigation & Header ──────────────────────────────
          'list',           // hamburger menu
          'x-lg',           // close menu
          'chevron-down',   // dropdown arrow
          'search',         // search button
          'lightning-charge-fill',
          'envelope-fill',

          // ── Social Media ─────────────────────────────────────
          'facebook',
          'instagram',
          'twitter-x',
          'linkedin',
          'tiktok',
          'whatsapp',
          'telegram',
          'youtube',
          'skype',
          'apple',
          'google-play',

          // ── Article sharing ──────────────────────────────────
          'share-fill',     // native OS share sheet button
          'link-45deg',     // copy link
          'check-lg',       // copy confirmation

          // ── Post Meta ────────────────────────────────────────
          'person',         // author
          'calendar',       // date
          'bookmark',       // category
          'clock',          // read time
          'tags',           // tags label

          // ── Navigation Arrows ────────────────────────────────
          'chevron-left',
          'chevron-right',
          'arrow-up',       // back to top

          // ── Footer / Contact Info ────────────────────────────
          'geo-alt',        // address
          'phone',          // phone (icon component)
          'telephone',      // telephone (contact page text)
          'envelope',       // email

          // ── Gallery & Media ──────────────────────────────────
          'images',         // FullGallery button
          'eye',
          'globe-americas',
          'lightning-charge',
          'chat-quote',
          'people',

          // ── Pages (MDX frontmatter icon field) ───────────────
          'shield-check',   // privacy policy
          'file-text',      // terms of use
          'cookie',         // cookie policy

          // ── Brand / finance components ───────────────────────
          'compass',              // Freedom Roadmap pillar, footer trust badge
          'flask',                // Business Experiments pillar
          'bank',                 // CPF strategy icon
          'piggy-bank',           // SRS strategy icon
          'house-door',           // HDB strategy icon
          'graph-up',             // T-bills strategy icon
          'graph-up-arrow',       // footer trust badge
          'airplane',             // Miles & Cashback strategy icon
          'gift',                 // Partner Offers heading
          'star-fill',            // comparison table ratings
          'arrow-right',          // CTA / read more links
          'trophy',               // footer trust badge
        ],
      },
    }),
  ],
  fonts: [
    {
      provider: fontProviders.google(),
      name: 'Sora',
      cssVariable: '--font-heading',
      weights: ['400','500','600', '700'],
      styles: ['normal', 'italic'],
    },
    {
      provider: fontProviders.google(),
      name: 'Inter',
      cssVariable: '--font-body',
      weights: ['400', '500', '600', '700'],
    },
    {
      // Loaded only on pages that render <Font cssVariable="--font-mono" />
      // (currently the estate-tax tool) — figures are monospaced so digits
      // do not jump while sliders drag.
      provider: fontProviders.google(),
      name: 'JetBrains Mono',
      cssVariable: '--font-mono',
      weights: ['400', '600'],
    },
  ],
});
