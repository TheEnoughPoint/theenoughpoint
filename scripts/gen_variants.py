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
def variant_a():
    h = ['<div class="va">']
    h.append('<div class="va-heads">' + ''.join(
        '<div><b>%s</b><span>%s</span></div>' % (r['p'], r['d'] + ' · ' + r['n']) for r in TRIO) + '</div>')
    for label, key, d, lead, trail, fmt, short in M:
        lvl = spread(key) < CLOSE
        tag = ('<i class="tag">level — will not decide it</i>' if lvl
               else '<i class="tag">no better end</i>' if d is None else '')
        h.append('<div class="va-m%s"><div class="va-l">%s%s</div><div class="va-r">' % (' lvl' if lvl else '', label, tag))
        for r in TRIO:
            k = rank(key, d, r)
            mark = ('▲ ' + lead) if k == 'best' else ('▼ ' + trail) if k == 'worst' else ''
            h.append('<div class="va-c is-%s"><span class="v">%s</span>%s</div>'
                     % (k, fmt(r), '<span class="s">%s</span>' % mark if mark else ''))
        h.append('</div></div>')
    h.append('</div>')
    return '\n'.join(h)

def variant_b():
    h = ['<div class="vb-wrap"><table class="vb"><thead><tr><th>Development</th>']
    for label, key, d, lead, trail, fmt, short in M:
        h.append('<th>%s</th>' % short)
    h.append('</tr></thead><tbody>')
    for r in TRIO:
        h.append('<tr><th scope="row">%s<span>%s</span></th>' % (r['p'], r['d']))
        for label, key, d, lead, trail, fmt, short in M:
            k = rank(key, d, r)
            h.append('<td class="is-%s">%s%s</td>' % (
                k, fmt(r), '<i>%s</i>' % ('▲' if k == 'best' else '▼' if k == 'worst' else '')))
        h.append('</tr>')
    h.append('</tbody></table></div>')
    return '\n'.join(h)

def variant_c():
    h = ['<div class="vc">']
    for label, key, d, lead, trail, fmt, short in M:
        lvl = spread(key) < CLOSE
        ends = ('<span class="vc-end">fewer</span><span class="vc-end r">more</span>' if d == 'more'
                else '<span class="vc-end">nearer</span><span class="vc-end r">further</span>' if d == 'less'
                else '<span class="vc-end">lower</span><span class="vc-end r">higher</span>')
        h.append('<div class="vc-m%s"><div class="vc-h"><b>%s</b><span>%s</span></div>' % (
            ' lvl' if lvl else '', label, 'level' if lvl else gap_phrase(key)))
        h.append('<div class="vc-track">%s<span class="vc-rail"></span>' % ends)
        for i, r in enumerate(TRIO):
            k = rank(key, d, r)
            h.append('<span class="vc-dot d%d is-%s" style="left:%.1f%%"><i>%s</i><em>%s</em></span>'
                     % (i, k, pos(key, r) * 100, SHORT[i], fmt(r)))
        h.append('</div></div>')
    h.append('</div>')
    return '\n'.join(h)

def variant_d():
    h = ['<div class="vd">']
    for i, r in enumerate(TRIO):
        h.append('<div class="vd-card"><div class="vd-top"><b>%s</b><span>%s · %s</span></div>' % (
            r['p'], r['d'], r['n']))
        for label, key, d, lead, trail, fmt, short in M:
            k = rank(key, d, r)
            h.append('<div class="vd-row"><span class="vd-lab">%s</span>'
                     '<span class="vd-bul"><i style="left:%.1f%%" class="is-%s"></i></span>'
                     '<span class="vd-val">%s</span></div>' % (short, pos(key, r) * 100, k, fmt(r)))
        h.append('</div>')
    h.append('</div>')
    return '\n'.join(h)

def variant_e():
    ranked = sorted(M, key=lambda m: spread(m[1]), reverse=True)
    top = [m for m in ranked if spread(m[1]) >= CLOSE][:3]
    lvl = [m for m in ranked if spread(m[1]) < CLOSE]
    h = ['<div class="ve">']
    for label, key, d, lead, trail, fmt, short in top:
        v = [(key(r), r) for r in TRIO]
        hi = max(v)[1]; lo = min(v)[1]
        front, back = (hi, lo) if d == 'more' else (lo, hi) if d == 'less' else (hi, lo)
        h.append('<div class="ve-p"><h5>%s &mdash; <em>%s</em></h5><p>%s at <b>%s</b>%s; %s at <b>%s</b>.</p></div>'
                 % (label, gap_phrase(key), front['p'], fmt(front),
                    ' <i>(%s)</i>' % lead if d else '', back['p'], fmt(back)))
    h.append('<table class="ve-t"><tbody>')
    for label, key, d, lead, trail, fmt, short in M:
        h.append('<tr><th>%s</th>%s</tr>' % (label, ''.join('<td>%s</td>' % fmt(r) for r in TRIO)))
    h.append('</tbody></table>')
    h.append('<p class="ve-n">Level on %s.</p>' % ', '.join(m[6] for m in lvl))
    h.append('</div>')
    return '\n'.join(h)
