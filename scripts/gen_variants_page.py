"""Emit the five-variant prototype page. Imports the builders from gen_variants.py."""
import io
from gen_variants import variant_a, variant_b, variant_c, variant_d, variant_e

CSS = r'''
<style is:global>
.vx{--ink:#0B1D33;--body:#33414F;--mut:#6B7280;--rule:#E3DDCF;--lite:#F0ECE2;
  --good:#0ca30c;--goodw:#EBF6EB;--bad:#d03b3b;--badw:#FBEDED;
  --mono:var(--font-mono),'SF Mono',Menlo,Consolas,monospace}
.vx-sec{margin:0 0 34px;padding:20px 22px 16px;background:#fff;border:1px solid var(--rule);border-radius:12px}
.post-content .vx-sec h3{margin:0 0 2px;font-size:16px;font-weight:700;color:var(--ink);font-family:var(--font-body)}
.post-content .vx-sec p.vx-note{margin:0 0 16px;font-size:12.5px;line-height:1.5;color:var(--mut)}

/* A - sticky spec matrix (what ships today) */
.va-heads{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding-bottom:8px;
  border-bottom:1px solid var(--rule);margin-bottom:10px}
.va-heads b{display:block;font-size:13px;color:var(--ink)}
.va-heads span{font-size:11px;color:var(--mut)}
.va-m{margin-bottom:12px}
.va-l{font-size:11.5px;font-weight:600;color:var(--body);margin-bottom:5px}
.va-m.lvl .va-l{color:var(--mut);font-weight:500}
.va-l .tag{display:inline-block;margin-left:6px;font-style:normal;font-size:11px;font-weight:600;
  border:1px solid var(--rule);border-radius:999px;padding:0 7px;color:var(--mut)}
.va-r{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.va-c{padding:6px 8px;border-radius:6px;border-left:3px solid transparent;background:var(--lite)}
.va-c.is-best{background:var(--goodw);border-left-color:var(--good)}
.va-c.is-worst{background:var(--badw);border-left-color:var(--bad)}
.va-m.lvl .va-c{background:transparent;border-left-color:var(--rule)}
.va-c .v{display:block;font-family:var(--mono);font-size:12px;font-weight:600;color:var(--ink)}
.va-c .s{display:block;margin-top:2px;font-size:11px;font-weight:700}
.va-c.is-best .s{color:var(--good)} .va-c.is-worst .s{color:var(--bad)}

/* B - transposed screener */
.vb-wrap{overflow-x:auto}
.post-content table.vb{width:100%;min-width:660px;border-collapse:collapse;margin:0;font-size:12px}
.post-content .vb th,.post-content .vb td{padding:8px 9px;text-align:right;border-bottom:1px solid var(--lite)}
.post-content .vb thead th{background:var(--ink);color:#fff;font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.04em;text-align:right;white-space:nowrap}
.post-content .vb thead th:first-child{text-align:left}
.post-content .vb tbody th{text-align:left;font-size:12.5px;color:var(--ink);white-space:nowrap;background:#fff}
.post-content .vb tbody th span{display:block;font-size:11px;font-weight:400;color:var(--mut)}
.post-content .vb td{font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--body);white-space:nowrap}
.post-content .vb td i{font-style:normal;margin-left:5px;font-size:11px}
.post-content .vb td.is-best{background:var(--goodw);color:var(--ink);font-weight:700}
.post-content .vb td.is-best i{color:var(--good)}
.post-content .vb td.is-worst{background:var(--badw);color:var(--ink);font-weight:700}
.post-content .vb td.is-worst i{color:var(--bad)}

/* C - dot plot per measure */
.vc-m{margin-bottom:30px}
.vc-h{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:26px}
.vc-h b{font-size:12.5px;color:var(--ink)} .vc-h span{font-family:var(--mono);font-size:11px;color:var(--mut)}
.vc-m.lvl .vc-h b{color:var(--mut);font-weight:500}
/* 44px inset, not 10: a dot at 0% or 100% centres its label on the track end, so half the label
   hangs outside. The widest label here is a price at about 72px, so 44px of inset clears it.
   Measured against the card's padding box, not guessed. */
.vc-track{position:relative;height:36px;margin:0 44px}
.vc-rail{position:absolute;left:0;right:0;top:16px;height:2px;background:var(--lite);border-radius:1px}
.vc-end{position:absolute;top:25px;left:0;font-size:11px;color:var(--mut)}
.vc-end.r{left:auto;right:0}
.vc-dot{position:absolute;top:10px;transform:translateX(-50%);width:14px;height:14px;
  border-radius:50%;background:var(--mut);border:2px solid #fff;box-shadow:0 0 0 1px var(--rule)}
.vc-dot.is-best{background:var(--good)} .vc-dot.is-worst{background:var(--bad)}
.vc-dot i{position:absolute;bottom:19px;left:50%;transform:translateX(-50%);font-style:normal;
  font-size:11px;color:var(--mut);white-space:nowrap}
.vc-dot em{position:absolute;bottom:31px;left:50%;transform:translateX(-50%);font-style:normal;
  font-family:var(--mono);font-size:11.5px;font-weight:700;color:var(--ink);white-space:nowrap}
.vc-dot.d1 i{bottom:auto;top:19px} .vc-dot.d1 em{bottom:auto;top:31px}

/* D - building cards with position bullets */
.vd{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.vd-card{border:1px solid var(--rule);border-radius:10px;padding:12px}
.vd-top b{display:block;font-size:13px;color:var(--ink)}
.vd-top span{display:block;font-size:11px;color:var(--mut);margin-bottom:10px}
.vd-row{margin-bottom:10px}
.vd-lab{display:block;font-size:11px;color:var(--mut)}
.vd-bul{position:relative;display:block;height:5px;background:var(--lite);border-radius:3px;margin:4px 0 3px}
.vd-bul i{position:absolute;top:-3px;width:11px;height:11px;border-radius:50%;
  transform:translateX(-50%);background:var(--mut);border:2px solid #fff;box-shadow:0 0 0 1px var(--rule)}
.vd-bul i.is-best{background:var(--good)} .vd-bul i.is-worst{background:var(--bad)}
.vd-val{display:block;font-family:var(--mono);font-size:11.5px;font-weight:600;color:var(--ink)}

/* E - editorial */
.ve-p{margin-bottom:13px}
.post-content .ve-p h5{margin:0 0 2px;font-size:12.5px;font-weight:700;color:var(--ink);font-family:var(--font-body)}
.post-content .ve-p h5 em{font-style:normal;font-family:var(--mono);font-size:11.5px;color:var(--mut);font-weight:400}
.post-content .ve-p p{margin:0;font-size:12.5px;line-height:1.55;color:var(--body)}
.post-content .ve-p p i{font-style:normal;color:var(--mut)}
.post-content table.ve-t{width:100%;border-collapse:collapse;margin:14px 0 8px;font-size:12px}
.post-content .ve-t th{background:transparent;color:var(--mut);text-align:left;font-size:11.5px;
  font-weight:600;text-transform:none;letter-spacing:0;padding:6px 8px;border-bottom:1px solid var(--lite)}
.post-content .ve-t td{padding:6px 8px;border-bottom:1px solid var(--lite);text-align:right;
  font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--body);white-space:nowrap}
.post-content p.ve-n{margin:0;font-size:11.5px;color:var(--mut)}

@media (max-width:640px){
  .vx-sec{padding:16px 14px 13px}
  .va-heads,.va-r{gap:6px}
  .va-heads b{font-size:11.5px} .va-c .v{font-size:11px} .va-c{padding:5px 6px}
  .vd{grid-template-columns:1fr}
  .vc-dot em{font-size:11px}
}
</style>
'''

SECS = [
    ('A', 'Sticky spec matrix',
     'What ships today. Columns are buildings, rows are measures, cells tint green or red only where '
     'the measure has a better end. Honest and complete; visually it is a form.', variant_a()),
    ('B', 'Transposed screener',
     'Buildings become rows and measures become columns, the way SquareFoot HK and a pricing table do '
     'it. Reads as market data rather than a duel and fits far more on one screen &mdash; at the cost '
     'of scrolling sideways on a phone.', variant_b()),
    ('C', 'Dot plot per measure',
     'One axis per measure with the three buildings placed on it. The only variant where the SIZE of a '
     'difference is visible rather than stated &mdash; two buildings sitting on top of each other says '
     '&ldquo;level&rdquo; without needing a label.', variant_c()),
    ('D', 'Cards with position bullets',
     'One card per building; inside it every measure shows where that building sits within the trio. '
     'Stacks natively on a phone and reads building-first, which is how people actually shortlist.',
     variant_d()),
    ('E', 'Editorial, facts under prose',
     'The Stacked Homes shape: lead with sentences naming the real differences, keep a compact facts '
     'table underneath. Least tool-like, most readable, hardest to generate honestly for an arbitrary '
     'trio.', variant_e()),
]

body = [CSS, '<div class="vx">']
for k, title, note, html in SECS:
    body.append('<section class="vx-sec"><h3>%s &mdash; %s</h3><p class="vx-note">%s</p>%s</section>'
                % (k, title, note, html))
body.append('</div>')

PAGE = '''---
// PROTOTYPE - five visual treatments of the same three-building comparison, for choosing between.
// Not linked from navigation. Static on purpose: the trio is fixed and every number is computed at
// build time by scripts/gen_condo_variants.py, because the question here is which treatment reads
// best, not whether the selectors work. Whichever wins gets wired back into CondoCompare.astro.
//
// All five obey the same two rules the real component does: only the three measures with a genuine
// direction are marked, and no variant produces a composite score.
import MainLayout from '@src/layouts/MainLayout.astro';

const title = 'Prototype - five ways to show a condominium comparison';
---

<MainLayout title={title} description="Internal prototype. Five visual treatments of the same comparison.">
  <div class="container xl:max-w-7xl mx-auto px-4">
    <div class="py-6 max-w-4xl">
      <h1 class="text-2xl md:text-3xl font-heading font-bold text-navy py-4">Five ways to show the same comparison</h1>
      <p class="text-sm text-muted pb-6">Same three buildings, same seven measures, same data throughout
      &mdash; Parc Clematis, Treasure at Tampines and Stirling Residences. Only the presentation changes.
      Internal prototype; not linked from anywhere.</p>
      <div class="post-content">
__BODY__
      </div>
    </div>
  </div>
</MainLayout>
'''

out = PAGE.replace('__BODY__', '\n'.join(body))
io.open(r'C:\TheEnoughPoint-wt-newlaunch\src\pages\condo-compare-variants.astro', 'w', encoding='utf-8').write(out)
print('variants page written,', len(out), 'bytes')
