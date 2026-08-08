"""Refuse to build a published figure on a feed that did not actually fetch.

live.json is produced weekly by another repo. When an upstream endpoint returns nothing, that
pipeline preserves the previous values and records it under `_meta.carried_forward` — which is the
right call for a dashboard that must keep rendering, and the wrong thing to silently freeze into an
article that states an as-of date.

This happened on 2026-08-07: every URA feed came back empty, the no-auth feeds succeeded so the
all-failed guard never fired, and the empty result was committed and published. The snapshot these
components were first generated from carries exactly that flag on `projects`, `districts`,
`new_launches` and `segments_official`.

So: fail closed. A generator asks for the feeds it needs; if any is in `errors` or
`carried_forward`, it stops. Building on stale-but-good data is sometimes the right call, and then
it must be a decision someone made — pass allow_stale=True (or set ALLOW_STALE=1) and the true
origin timestamp is returned so the generator can stamp it into the file it writes.
"""
import io
import json
import os


class FeedUnhealthy(RuntimeError):
    pass


def load_live(path, feeds, allow_stale=None):
    """Return (data, provenance). Raises FeedUnhealthy unless every named feed fetched cleanly.

    provenance is a one-line string naming the true as-of, for stamping into generated output.
    """
    data = json.load(io.open(path, encoding='utf-8'))
    meta = data.get('_meta', {})
    if allow_stale is None:
        allow_stale = os.environ.get('ALLOW_STALE') == '1'

    errored = sorted(set(feeds) & set((meta.get('errors') or {}).keys()))
    cf = meta.get('carried_forward') or {}
    carried = sorted(set(feeds) & set(cf.get('feeds') or []))

    fetched = meta.get('fetched')
    origin = cf.get('from') or fetched
    provenance = f'live.json fetched {fetched}'
    if carried:
        provenance = (f'live.json fetched {fetched}; feeds {", ".join(carried)} were CARRIED '
                      f'FORWARD from {origin} — they returned no data on that run')

    if errored or carried:
        detail = []
        if errored:
            detail.append(f'errored: {", ".join(errored)}')
        if carried:
            detail.append(f'carried forward from {origin}: {", ".join(carried)}')
        msg = ('feed is not healthy for the figures being generated (' + '; '.join(detail) + '). '
               'Re-run the upstream fetch, or set ALLOW_STALE=1 to build on the preserved values '
               'and stamp their true origin into the output.')
        if not allow_stale:
            raise FeedUnhealthy(msg)
        print('WARNING: ' + msg)

    return data, provenance


def rows_for_compare(data, min_sales=10):
    """The project rows both components draw on, with tenure as an explicit flag.

    `fh` is a boolean, not a sentinel. The feed contains numeric leases of 968, 9968 and 999963,
    so any `>= 999` test would silently reclassify real leaseholds as freehold.
    """
    def band(sqft):
        return 0 if sqft < 600 else 1 if sqft < 850 else 2 if sqft < 1150 else 3

    BAND_LABEL = ['under 600', '600–850', '850–1,150', '1,150+']

    districts = {r['district']: r for r in data['districts']['rows']}
    out = []
    for r in data['projects']['rows']:
        if r['vol_12m'] < min_sales or r['lease'] is None or r['mrt_m'] is None:
            continue
        d = districts.get(r['district'])
        if not d or not d.get('psf_sz'):
            continue
        b = d['psf_sz'][band(r['size'])]
        pp = r.get('psf_p')
        if not b or not pp or len(pp) < 5:
            continue
        fh = r['lease'] == 'FH'
        out.append({
            'p': r['project'].title(), 'd': r['district'], 'n': d['name'],
            'psf': r['median_psf'], 'v': r['vol_12m'],
            'fh': 1 if fh else 0, 'lyr': None if fh else int(r['lease']),
            'm': r['mrt_m'], 'x': r['mrt'], 's': r['size'], 'b': b[2],
            'bl': BAND_LABEL[band(r['size'])], 'q': r['price'],
            'lo': pp[0], 'hi': pp[4], 'mo': r.get('momentum'),
        })
    out.sort(key=lambda r: (r['d'], r['p']))
    return out
