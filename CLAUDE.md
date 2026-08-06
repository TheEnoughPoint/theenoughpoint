# TheEnoughPoint.com — Claude Instructions

This is TheEnoughPoint.com, a Singapore-born personal finance media site.

## Brand positioning

TheEnoughPoint helps financially aware Singaporeans and Asia-based readers invest better, build optional income, spend with value, and reach their own “enough point” by 40ish.

## Brand tone

- Trustworthy
- Calm
- Practical
- Relatable
- Singapore-aware
- Financially literate but not intimidating
- No hype
- No get-rich-quick language

## Visual direction

Adapt the Astromag theme toward the reference mockup:
- Deep navy header
- Jade / teal primary accent
- Warm gold for highlights
- Ivory or soft off-white background
- Rounded content cards
- Clean magazine-style article pages
- Right sidebar on desktop
- Mobile-first responsive layout

## Core content pillars

1. Build Enough
   - FIRE roadmap
   - CPF, SRS, HDB, retirement planning
   - How much is enough

2. Invest Better
   - Brokerages
   - ETFs, REITs, T-bills, SSBs
   - Financial product reviews
   - Platform comparisons

3. Optional Income
   - Side hustles
   - Small business experiments
   - Acquisitions
   - Income streams

4. Spend With Value
   - Cheap hunts
   - Lifestyle optimisation
   - Family spending
   - Smart purchases

## Authors

Use anonymous author identities:
- FI: investing, risk, CPF/SRS, portfolio frameworks, product analysis
- RE: semi-retirement, business experiments, lifestyle design, value living

## Compliance rules

- Do not present personalised financial advice.
- Do not say “you should buy/sell/hold”.
- Do not create target prices.
- Do not create model portfolios unless clearly labelled hypothetical.
- Sponsored content must be clearly labelled.
- Affiliate links must include disclosure.
- Add the disclosure component to all review/comparison articles.
- Avoid implying that FI’s employer endorses any view.
- Views are personal and educational only.

## Technical rules

- Keep components reusable.
- Prefer MDX content files.
- Use Astro content collections where available.
- Do not hardcode repeated article lists if they can be driven from frontmatter or data files.
- Keep styling centralised in Tailwind/CSS variables.
- Every interactive tool and chart card ends with the `ToolBrand` credit
  component (`src/components/ToolBrand.astro`) as the last child inside the
  card border, so screenshots carry the site's name. New tools and charts
  include it from their first commit.
- Make all changes through branches and pull requests unless asked otherwise.
- Deployment is automatic: merging a PR into `main` triggers GitHub Actions,
  which builds and deploys to Cloudflare Pages via `cloudflare/wrangler-action`
  (see `.github/workflows/deploy.yml`), authenticated with the
  `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` repo secrets. No manual step
  needed for normal publishing. Cloudflare's own "Automatic deployments" is
  paused on the project to avoid two systems deploying the same push.
- Emergency fallback only, if the Actions deploy ever fails: run these two
  lines locally from an up-to-date `main` (needs `wrangler login` or a
  `CLOUDFLARE_API_TOKEN` env var with Cloudflare Pages: Edit permission):
  - `npm run build`
  - `npx wrangler pages deploy dist --project-name=theenoughpoint --branch=main`