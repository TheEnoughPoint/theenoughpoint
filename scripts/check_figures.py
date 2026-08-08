"""Fail if an article's prose has drifted from the data it claims to describe.

The components recompute their own figures from live.json on every regeneration. The articles do
not — their prose carries typed numbers. So a data refresh silently pulls the two apart, which is
exactly the transcription drift the house rules forbid.

This recomputes each load-bearing figure from live.json and asserts it still appears in the BUILT
page — not the MDX. That matters: a figure may live in the prose or inside a component, and it has
moved between the two more than once. Checking the rendered output covers both and asks the only
question that counts, which is whether the reader is shown a number the data still supports.

It is deliberately dumb: substring presence, not parsing. A figure that changes stops appearing and
the check fails; a figure that never appeared fails immediately, catching a typo when it is
introduced rather than a year later. Run it after a build.

Run: python scripts/check_figures.py   (exit 1 on any mismatch)
"""
import io
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feed_guard import load_live  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, '..', 'dist')
LIVE = os.environ.get('LIVE_JSON', r'C:/dev/sg-property-decision/data/live.json')

PAGES = ['price-a-new-launch-before-the-price-list', 'condo-compare']


def fmt(v):
    return format(int(round(v)), ',')


def build_checks(data):
    projects = {r['project']: r for r in data['projects']['rows']}
    d20 = next(r for r in data['districts']['rows'] if r['district'] == 'D20')
    bands = d20['psf_sz']

    # The five District 20 buildings the article names as its nine-year exit comparable:
    # leasehold with 85+ years and at least ten resales.
    comps = [r for r in data['projects']['rows']
             if r['district'] == 'D20' and r['lease'] != 'FH' and r['lease'] is not None
             and int(r['lease']) >= 85 and r['vol_12m'] >= 10]
    comps_median = sorted(r['median_psf'] for r in comps)[len(comps) // 2]

    # The break-even grid. Every one of these fifteen cells is a function of comps_median, so a
    # feed refresh moves all of them at once while the typed table sits still. This is the drift the
    # module exists to catch, and the table is the part of the article a reader is most likely to
    # screenshot and act on.
    ROUND_TRIP = 1.06
    grid = []
    for entry in (2600, 2900, 3100):
        need = entry * ROUND_TRIP / comps_median
        grid.append((f'break-even: {entry} psf, total rise', f'+{round((need - 1) * 100)}%'))
        for yrs in (7, 9, 12, 15):
            rate = (need ** (1 / yrs) - 1) * 100
            grid.append((f'break-even: {entry} psf over {yrs}y', f'{rate:.1f}%'))

    # The entry-gap endpoints. These are derived from the four band medians, which WERE guarded --
    # but the endpoints quoted in the summary and the frontmatter were not, so a refresh moved the
    # 1,150+ band from 1,763 to 1,739 and the article went on claiming +76% while the component
    # beneath it rendered +78%. Guarding an input does not guard what a reader is told about it.
    gaps = [(price / b[2] - 1) * 100 for b in bands for price in (2600, 3100)]
    grid += [
        ('entry gap, narrowest band edge', f'+{round(min(gaps))}%'),
        ('entry gap, widest band edge', f'+{round(max(gaps))}%'),
    ]

    # The hold-length claim: how many of URA's own long-run windows clear the hurdle at each
    # horizon. The window rates are typed (URA full history, cited on the page); the hurdles are
    # feed-derived, so a refresh could move one across a boundary and silently falsify the count.
    URA_WINDOWS = (1.8, 4.7, 2.8, 4.6, 6.1)          # 30y, 20y, 15y, 10y, 5y
    for yrs, word in ((7, 'seven'), (15, 'fifteen')):
        rate = ((2900 * ROUND_TRIP / comps_median) ** (1 / yrs) - 1) * 100
        n = sum(1 for w in URA_WINDOWS if w >= rate)
        grid.append((f'windows clearing the {word}-year hurdle',
                     {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}[n] + ' of the five'))

    # Zyon Grand, carried in the article as a worked example of the same method on a project whose
    # price is already recorded. Its psf is URA's developer-sales median for ONE month, so it moves
    # more than a resale median does — which is exactly why it is guarded rather than trusted.
    zg = next(r for r in data['new_launches']['rows'] if r['project'] == 'ZYON GRAND')
    d3 = [r for r in data['projects']['rows']
          if r['district'] == 'D3' and r['lease'] not in ('FH', None)
          and int(r['lease']) >= 85 and r['vol_12m'] >= 10]
    d3_base = sorted(r['median_psf'] for r in d3)[len(d3) // 2]
    zg_need = zg['psf'] * ROUND_TRIP / d3_base
    grid += [
        ('Zyon Grand new-sale median $psf', fmt(zg['psf'])),
        ('Zyon Grand take-up', f"{zg['takeup'] * 100:.0f}%"),
        ('D3 exit comparables', str(len(d3))),
        ('D3 exit comparable resales', fmt(sum(r['vol_12m'] for r in d3))),
        ('D3 exit comparable $psf', fmt(d3_base)),
        ('Zyon Grand total rise', f'+{round((zg_need - 1) * 100)}%'),
        ('Zyon Grand over 9y', f'{(zg_need ** (1 / 9) - 1) * 100:.1f}%'),
        ('same method at 3100 psf in D3',
         f'+{round((3100 * ROUND_TRIP / d3_base - 1) * 100)}%'),
    ]

    return grid + [
        ('D20 resale median $psf', fmt(d20['median_psf'])),
        ('D20 twelve-month resale count', fmt(d20['vol_12m'])),
        ('size band <600 median', fmt(bands[0][2])),
        ('size band 600-850 median', fmt(bands[1][2])),
        ('size band 850-1150 median', fmt(bands[2][2])),
        ('size band 1150+ median', fmt(bands[3][2])),
        ('exit comparable median $psf', fmt(comps_median)),
        # Both of these were stated in prose, derived from the feed, and unguarded. The momentum
        # shipped as 4.7% after a refresh moved it to 4.6%.
        ('D20 twelve-month momentum', f"{d20['momentum'] * 100:.1f}%"),
        ('D20 gross yield', f"{d20['yield'] * 100:.1f}%"),
        ('2026 land award average $psf ppr', fmt(data['gls']['avg_psf_ppr_year']['2026'])),
        ('2025 land award average $psf ppr', fmt(data['gls']['avg_psf_ppr_year']['2025'])),
        # Rule-derived, not feed-derived, but stated twice in the article and worth pinning:
        # ABSD at 20% on the worked 950 sq ft unit, and a year of District 20 rent on 1,100 sq ft.
        ('ABSD, second property, 950 sq ft at 2,900', fmt(950 * 2900 * 0.20)),
        # The card says "about S$61,000", so the guard asserts the same rounding the article
        # applies rather than the raw product -- otherwise it fails on a deliberate round.
        ('one year of D20 rent on 1,100 sq ft', fmt(round(5100 * 12, -3))),
        ('Jadescape median $psf', fmt(projects['JADESCAPE']['median_psf'])),
        ('Jadescape resale count', fmt(projects['JADESCAPE']['vol_12m'])),
        ('Braddell View median $psf', fmt(projects['BRADDELL VIEW']['median_psf'])),
        ('Braddell View resale count', fmt(projects['BRADDELL VIEW']['vol_12m'])),
    ]


def main():
    data, provenance = load_live(LIVE, ['projects', 'districts', 'new_launches', 'gls'], allow_stale=True)
    checks = build_checks(data)

    paths = [os.path.join(DIST, p, 'index.html') for p in PAGES]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print('build the site first — not found:\n  ' + '\n  '.join(missing))
        return 2

    # Strip <script> blocks before searching. CondoCompare embeds 318 projects as JSON, so a raw
    # substring search over the HTML matches almost any four-digit number and passes everything —
    # this check reported "ok" on five stale figures before that was fixed. Only what a reader can
    # actually read counts.
    #
    # Then strip the markup itself, for the same reason from the other direction: a figure is often
    # split across tags for typography — the break-even table sets its "%" in a span so it can be
    # sized down — and searching raw HTML would report a number missing that a reader can see
    # perfectly well. Compare against rendered text, which is the only thing the reader gets.
    text = ''
    for p in paths:
        html = io.open(p, encoding='utf-8').read()
        html = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', html, flags=re.S | re.I)
        html = re.sub(r'<[^>]+>', '', html)
        text += re.sub(r'[ \t\r\n]+', ' ', html)

    print('checking the built pages: ' + ', '.join(PAGES))
    print(f'  against {provenance}\n')
    bad = []
    for label, value in checks:
        ok = value in text
        print(f'  {"ok  " if ok else "FAIL"}  {label:<32} {value}')
        if not ok:
            bad.append((label, value))

    # A second kind of check. Presence is not enough when a component on the same page renders the
    # right number: the entry gap shipped as "+18% to +76%" in the summary while the component
    # beneath it drew +78% from the same feed, and searching for "+78%" found the component's copy
    # and passed. This captures every occurrence of the phrase shape and requires them to agree.
    d20r = next(r for r in data['districts']['rows'] if r['district'] == 'D20')
    gaps = [(price / b[2] - 1) * 100 for b in d20r['psf_sz'] for price in (2600, 3100)]
    want = (str(round(min(gaps))), str(round(max(gaps))))
    # Anchored on "runs", which is how the entry gap is phrased in all three places it appears.
    # An unanchored pattern also swept up the break-even note's estimator spread, a different
    # range that is legitimately different -- a check that cries wolf gets switched off.
    found = set(re.findall(r'runs (?:from )?\+(\d+)% to \+(\d+)%', text))
    wrong = sorted(f for f in found if f != want)
    consistent = bool(found) and not wrong
    print(f'  {"ok  " if consistent else "FAIL"}  {"entry-gap range, every statement":<32} '
          f'+{want[0]}% to +{want[1]}%' + ('' if consistent else f'   page also says {wrong}'))
    if not consistent:
        bad.append(('entry-gap range stated inconsistently',
                    f'every statement to read +{want[0]}% to +{want[1]}%'
                    + (f'; found {wrong}' if wrong else '; found none')))

    if bad:
        print(f'\n{len(bad)} figure(s) shown to readers no longer match the data:')
        for label, value in bad:
            print(f'  - {label}: expected to find "{value}" on the page')
        print('\nRegenerate the components, or the data moved and the prose needs a re-read.')
        return 1
    print(f'\nall {len(checks)} load-bearing figures still match what the data says.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
