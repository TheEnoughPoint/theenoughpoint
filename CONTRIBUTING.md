# Publishing to TheEnoughPoint.com

How to write and publish an article, end to end. Deployment is fully
automatic now — merging a pull request is the last step. There is nothing to
run manually, and no Cloudflare account or credentials needed.

## One-time setup

1. **Node.js 22 or later.** Astro requires it — check with `node --version`.
2. **Clone the repo** (you already have GitHub access):
   ```bash
   git clone https://github.com/TheEnoughPoint/theenoughpoint.git
   cd theenoughpoint
   ```
3. **Install dependencies:**
   ```bash
   npm install
   ```
   Run this again any time `package.json` changes, or if `npm run build`
   suddenly can't find `astro` — `node_modules` isn't committed to the repo.

## Every time you sit down to write

**Always start from a fresh `main`** — this is the one step that caused us
grief before (a stale local branch briefly reverted live content):

```bash
git checkout main
git pull origin main
git checkout -b <yourname>/<short-slug>
```

e.g. `git checkout -b re/side-hustle-part-2`.

## Writing the article

Articles are `.mdx` files in `src/content/blog/`. Filename = URL slug, e.g.
`src/content/blog/my-article.mdx` → `theenoughpoint.com/my-article/`.

Frontmatter fields:

```yaml
---
title: "Your Title Here"
cover: "/img/your-cover.jpg"       # put the image in public/img/ first
date: "2026-07-24"
category: "invest-better"           # see the 4 valid values below
tags:
  - Investing
  - Singapore
readTime: 7                          # minutes, your estimate
authorId: "fi"                       # "fi" or "re"
excerpt: |
  One or two sentences — used in card previews and the meta description.

# Optional fields:
featured: false        # show in the homepage featured row
popular: false          # show in the sidebar "Popular Reads"
sponsored: false         # adds a sponsored banner to the article
sponsorName: ""          # required if sponsored: true
showDisclosure: false    # adds the affiliate-disclosure box (use for reviews/comparisons)
lifeStage: []            # e.g. ["In Your 30s"] — shown as pills on featured cards
---

Your article content here, in Markdown/MDX.
```

**Valid `category` values** (must match exactly):
- `build-enough` — FI's pillar (FIRE roadmap, CPF/SRS/HDB, retirement)
- `invest-better` — FI's pillar (brokerages, ETFs/REITs/T-bills, product reviews)
- `optional-income` — RE's pillar (side hustles, small business, acquisitions)
- `spend-with-value` — RE's pillar (cheap hunts, lifestyle, family spending)

**`authorId`** should match whichever of you wrote it — `fi` or `re`.

### Using the reusable components in an article

Import at the top of the `.mdx` file (after the frontmatter), then use anywhere in the body:

```mdx
import ProductComparisonTable from '@src/components/ProductComparisonTable.astro';

<ProductComparisonTable ids={['ibkr', 'syfe', 'endowus']} />
```

Partner IDs are defined in `src/data/partnersData.ts` — add a new one there
if you need a platform that isn't listed yet.

## Preview locally before publishing

```bash
npm run dev
```

Opens at `http://localhost:4321` — check the article renders correctly,
especially any embedded components, before pushing.

## Publish

```bash
git add src/content/blog/your-article.mdx
git commit -m "Add article: Your Title Here"
git push origin <yourname>/<short-slug>
```

Then on GitHub:
1. Open a pull request (base: `main`)
2. Review the diff yourself, or ask the other author to take a look
3. Merge it

**That's it.** GitHub Actions builds and deploys to the live site
automatically — usually live within 1–2 minutes of merging. You can watch
progress under the repo's **Actions** tab; a green checkmark means it's done.

## If something looks wrong after merging

- Check the **Actions** tab on GitHub for a red ✕ on the latest run — click
  in to see the error.
- If the article still isn't showing after ~5 minutes with a green Actions
  run, it's likely a Cloudflare-side hiccup rather than your article. Flag it
  rather than guessing — don't try to "fix" it by rebuilding locally and
  running `wrangler pages deploy` yourself unless specifically asked to; that
  requires Cloudflare credentials neither of you should need day-to-day, and
  doing it from a stale branch is exactly what caused problems before.

## Compliance reminders (see `CLAUDE.md` for the full list)

- No personalised financial advice, no "you should buy/sell/hold," no target prices.
- Sponsored content and affiliate links must be clearly disclosed
  (`sponsored`/`showDisclosure` frontmatter fields handle the on-page labelling).
- Views are personal and educational only.
