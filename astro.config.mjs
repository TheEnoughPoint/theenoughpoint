import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import icon from 'astro-icon';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://portal.madethemes.com',
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [
    mdx(),
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
  ],
});
