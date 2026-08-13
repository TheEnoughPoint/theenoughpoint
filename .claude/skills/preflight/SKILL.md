---
name: preflight
description: Pre-publication check for a TheEnoughPoint article. Measures the rendered page at three viewports for overflow, contrast, fused words and jargon, then walks the editorial questions no script can answer. Use before opening a PR for any new or materially rewritten article, and before merging one. Triggers: "preflight", "check this before publishing", "is this ready to ship", "run the render check".
---

# Preflight

Two halves. Do not skip the second because the first went green.

**The build passing, `check_page.py` passing, and the CSS looking right in
source have all coexisted with defects that shipped to production.** Every
check in part 1 exists because something got through. Everything in part 2 got
through *and* would have got through part 1 — those were the ones that mattered.

## Part 1 — measure the rendered page

`scripts/render-audit.js` holds the assertions. It runs in page context and
returns `{ pass, failures, warnings, measured }`.

1. Start the dev server: `preview_start` with `{name: "astro-dev"}`.
2. Navigate to the article.
3. For each viewport — **390, 768, 1280** — resize, then read the file with
   Read, evaluate its contents in the page, and call:

   ```js
   renderAudit({ jargon: [/* terms this piece claims to have removed */] })
   ```

   The jargon list is per-article. If the piece was rewritten to drop insider
   vocabulary, list those words; a rewrite that leaves the terms in a
   JavaScript-rendered table has not happened.

4. **Every `failure` blocks.** `warnings` need a judgement — a wide numeric
   table or a chart scrolling sideways is usually fine; a table of sentences
   doing it is not.

Two traps this catches that manual checking does not:

- **Static HTML is not the page.** Anything a component renders with JavaScript
  — table rows, verdict sentences, computed figures — is absent from `dist/*.html`.
  Grepping the built file for a banned word will report zero while five sit on
  screen. Only the live DOM tells the truth.
- **Partial CSS overrides.** Overriding `content` and `color` on a marker
  leaves an inherited `background` and `border-radius` behind it. The result
  measured 1.54:1 and looked like a smudge.

## Part 2 — the questions no script answers

Read the rendered page as a stranger would. Ask these out loud.

1. **Does the title state the finding in words a non-specialist parses?**
   Not clever, not elegant — parseable. "4 mpd pays 1.30" fails; it is a
   punchline to a joke the reader has not heard. Under 60 characters, with the
   searchable phrase first.

2. **Does the cover explain or decorate?** If it needs a term from inside the
   article to make sense, it is decoration. Draw the mechanism instead of
   naming it.

3. **Does every chart encode the variable its caption claims?** A chart of
   ratios must not draw absolute magnitudes. This one shipped: bars scaled to a
   global maximum while the surrounding text argued about multiples, so the
   picture said something true, irrelevant, and different from the sentence
   beside it.

4. **How many examples does each point need?** Usually one. Fifteen bars to
   support a claim that is one number with a range is a cost paid by every
   reader. Feature one case and state the range; put the rest behind a
   disclosure.

5. **If a featured example is the most flattering one, say so or change it.**
   Pick the below-median case where you can.

6. **Is every load-bearing figure sourced, and does any appear in only one
   place?** If it cannot be corroborated twice, do not print it — say what you
   could not verify.

7. **Does any static label hardcode a value that is an editable input
   elsewhere?** A header reading "Beats 1.7% cashback?" lies the moment a
   reader changes the rate.

8. **Read the opening paragraph alone.** Does it describe a person or a
   situation the reader recognises, or does it start with mechanism?

## Part 3 — before the PR

- `npm run build` clean.
- `python C:/dev/scripts/check_page.py dist/<slug>/index.html` at 0 fail.
- Confirm the og raster regenerated if the cover changed.
- If the piece names figures that decay — card rates, award charts, fees —
  check whether the monthly routine's prompt still describes the article
  accurately. A rewrite can leave that prompt describing a page that no longer
  exists.

## Adding a check

When a defect gets through, add its assertion to `scripts/render-audit.js`
rather than remembering it. The file is the accumulated list of everything this
site has got wrong once. Verify any new check against a page you know is clean
before trusting it — the audit itself shipped three false-positive classes on
its first run, and a checker that cries wolf gets ignored.
