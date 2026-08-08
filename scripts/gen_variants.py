"""Emit a prototype page with five visual treatments of the same comparison.

Static on purpose: the point is to judge the LOOK, not the interaction, so all five render the
same fixed trio and the numbers are computed here rather than in the browser. Whichever wins gets
wired back into CondoCompare.astro with its selectors.
"""
import io, json

rows = json.load(io.open('cmp_rows.json', encoding='utf-8'))
BY = {r['p']: r for r in rows}
TRIO = [BY['Parc Clematis'], BY['Treasure At Tampines'], BY['Stirling Residences']]

def sgd(v): return 'S$' + format(round(v), ',')
def num(v): return format(round(v), ',')

# label, key fn, direction ('more'/'less'/None), leader word, trailer word, formatter, short name
M = [
    ('Median resale price', lambda r: r['psf'], None, '', '', lambda r: sgd(r['psf']) + ' psf', 'price psf'),
    ('Against its district', lambda r: r['psf'] / r['b'] - 1, None, '', '',
     lambda r: ('+' if r['psf'] >= r['b'] else '−') + str(round(abs(r['psf'] / r['b'] - 1) * 100)) + '%', 'vs district'),
    ('Resales in 12 months', lambda r: r['v'], 'more', 'most traded', 'least traded', lambda r: num(r['v']), 'turnover'),
    ('Lease remaining', lambda r: r['l'], 'more', 'longest', 'shortest', lambda r: str(r['l']) + ' yrs', 'lease'),
    ('To the nearest MRT', lambda r: r['m'], 'less', 'nearest', 'furthest', lambda r: num(r['m']) + ' m', 'to MRT'),
    ('Size that trades', lambda r: r['s'], None, '', '', lambda r: num(r['s']) + ' sq ft', 'unit size'),
    ('Typical price paid', lambda r: r['q'], None, '', '', lambda r: sgd(r['q']), 'typical price'),
]
CLOSE = 0.15

def spread(key):
    v = [key(r) for r in TRIO]
    hi, lo = max(v), min(v)
    return (hi / lo - 1) if lo > 0 else abs(hi - lo)

def rank(key, direction, r):
    """'best' | 'worst' | 'mid' | 'flat' — flat when unranked or when the row is level."""
    if direction is None or spread(key) < CLOSE:
        return 'flat'
    v = sorted({key(x) for x in TRIO}, reverse=(direction == 'more'))
    i = v.index(key(r))
    return 'best' if i == 0 else 'worst' if i == len(v) - 1 else 'mid'

def pos(key, r):
    """0..1 position of this value within the trio's range, for the dot plot and bullets."""
    v = [key(x) for x in TRIO]
    hi, lo = max(v), min(v)
    return 0.5 if hi == lo else (key(r) - lo) / (hi - lo)

def gap_phrase(key):
    v = [key(x) for x in TRIO]
    hi, lo = max(v), min(v)
    if lo <= 0: return ''
    ratio = hi / lo
    if ratio >= 1.8: return 'about ' + str(round(ratio, 1)) + '× apart'
    return str(round((ratio - 1) * 100)) + '% apart'

NAMES = [r['p'] for r in TRIO]
SHORT = ['Parc Clematis', 'Treasure', 'Stirling']


# ---------------------------------------------------------------- variant builders
def leads_of(r):
    """Measures this building leads — used by B's summary column and E's annotations."""
    out = []
    for label, key, d, lead, trail, fmt, short in M:
        if d and spread(key) >= CLOSE and rank(key, d, r) == 'best':
            out.append((short, lead))
    return out

def variant_b():
    """Transposed screener, now carrying the context the bare table lacked: the station name,
    a per-building summary of what it leads, and a footer row giving each column's spread."""
    h = ['<div class="vb-wrap"><table class="vb"><thead><tr><th>Development</th>']
    for label, key, d, lead, trail, fmt, short in M:
        arrow = ' <i class="dir">more is more</i>' if d == 'more' else \
                ' <i class="dir">less is nearer</i>' if d == 'less' else \
                ' <i class="dir none">no better end</i>'
        h.append('<th>%s%s</th>' % (short, arrow))
    h.append('<th>Leads on</th></tr></thead><tbody>')
    for r in TRIO:
        h.append('<tr><th scope="row">%s<span>%s · %s</span></th>' % (r['p'], r['d'], r['n']))
        for label, key, d, lead, trail, fmt, short in M:
            k = rank(key, d, r)
            extra = '<span class="sub">%s</span>' % r['x'] if short == 'to MRT' else ''
            mark = '<i>▲</i>' if k == 'best' else '<i>▼</i>' if k == 'worst' else ''
            h.append('<td class="is-%s">%s%s%s</td>' % (k, fmt(r), mark, extra))
        led = leads_of(r)
        h.append('<td class="lead-col">%s</td></tr>' % (
            ''.join('<b>%s</b>' % l[1] for l in led) if led else '<em>none</em>'))
    h.append('</tbody><tfoot><tr><th scope="row">Spread across the three</th>')
    for label, key, d, lead, trail, fmt, short in M:
        lvl = spread(key) < CLOSE
        h.append('<td class="%s">%s</td>' % ('lvl' if lvl else '', 'level' if lvl else gap_phrase(key)))
    h.append('<td></td></tr></tfoot></table></div>')
    return '\n'.join(h)

def variant_c():
    """Dot plot, with the positive and negative ends made explicit: the rail carries a tinted span
    running from the trailing value to the leading one, the end captions say which way is which,
    and the leading and trailing dots are enlarged and labelled."""
    h = ['<div class="vc">']
    for label, key, d, lead, trail, fmt, short in M:
        lvl = spread(key) < CLOSE
        if d and not lvl:
            best = min(TRIO, key=lambda r: key(r)) if d == 'less' else max(TRIO, key=lambda r: key(r))
            worst = max(TRIO, key=lambda r: key(r)) if d == 'less' else min(TRIO, key=lambda r: key(r))
            pb, pw = pos(key, best) * 100, pos(key, worst) * 100
            lo, hi = min(pb, pw), max(pb, pw)
            grad = ('linear-gradient(90deg,var(--good),var(--bad))' if pb < pw
                    else 'linear-gradient(90deg,var(--bad),var(--good))')
            span = '<span class="vc-span" style="left:%.1f%%;width:%.1f%%;background:%s"></span>' % (lo, hi - lo, grad)
            ends = ('<span class="vc-end bad">%s ▼</span><span class="vc-end good r">▲ %s</span>' % (trail, lead)
                    if d == 'less' else
                    '<span class="vc-end bad">▼ %s</span><span class="vc-end good r">%s ▲</span>' % (trail, lead))
        else:
            span = ''
            ends = '<span class="vc-end">lower</span><span class="vc-end r">higher</span>'
        h.append('<div class="vc-m%s"><div class="vc-h"><b>%s</b><span>%s</span></div>' % (
            ' lvl' if lvl else '', label, 'level — will not decide it' if lvl else gap_phrase(key)))
        h.append('<div class="vc-track"><span class="vc-rail"></span>%s%s' % (span, ends))
        for i, r in enumerate(TRIO):
            k = rank(key, d, r)
            h.append('<span class="vc-dot d%d is-%s" style="left:%.1f%%"><i>%s</i><em>%s</em></span>'
                     % (i, k, pos(key, r) * 100, SHORT[i], fmt(r)))
        h.append('</div></div>')
    h.append('</div>')
    return '\n'.join(h)

def variant_e():
    """Editorial, now annotated: the headline figures are tinted, the leader and trailer are named
    inline, and the facts table carries the same green/red marks as the other variants."""
    ranked = sorted(M, key=lambda m: spread(m[1]), reverse=True)
    top = [m for m in ranked if spread(m[1]) >= CLOSE][:3]
    lvl = [m for m in ranked if spread(m[1]) < CLOSE]
    h = ['<div class="ve">']
    for label, key, d, lead, trail, fmt, short in top:
        if d:
            front = min(TRIO, key=key) if d == 'less' else max(TRIO, key=key)
            back = max(TRIO, key=key) if d == 'less' else min(TRIO, key=key)
        else:
            front, back = max(TRIO, key=key), min(TRIO, key=key)
        h.append(
            '<div class="ve-p"><h5>%s <em>%s</em></h5><p>'
            '<b class="%s">%s</b> <span class="ve-v %s">%s</span>%s '
            '&nbsp;against&nbsp; <b class="%s">%s</b> <span class="ve-v %s">%s</span>%s</p></div>'
            % (label, gap_phrase(key),
               've-n-good' if d else '', front['p'], 'good' if d else '', fmt(front),
               ' <i class="ve-tag good">▲ %s</i>' % lead if d else '',
               've-n-bad' if d else '', back['p'], 'bad' if d else '', fmt(back),
               ' <i class="ve-tag bad">▼ %s</i>' % trail if d else ''))
    h.append('<table class="ve-t"><thead><tr><th></th>%s</tr></thead><tbody>'
             % ''.join('<th>%s</th>' % r['p'] for r in TRIO))
    for label, key, d, lead, trail, fmt, short in M:
        lvlrow = spread(key) < CLOSE
        h.append('<tr class="%s"><th>%s%s</th>%s</tr>' % (
            'lvl' if lvlrow else '', label,
            '<i>level</i>' if lvlrow else ('' if d else '<i>no better end</i>'),
            ''.join('<td class="is-%s">%s</td>' % (rank(key, d, r), fmt(r)) for r in TRIO)))
    h.append('</tbody></table>')
    if lvl:
        h.append('<p class="ve-n">Level on %s &mdash; those will not decide it.</p>'
                 % ', '.join(m[6] for m in lvl))
    h.append('</div>')
    return '\n'.join(h)
