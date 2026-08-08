"""Generate CondoCompare.astro.

Three things this does that the first version did not:
  - loads live.json through feed_guard, which refuses to build on a feed that did not fetch
  - inlines scripts/compare_logic.mjs rather than restating its rules, so the tested code and the
    shipped code are the same code
  - stamps the data's true provenance into the generated file
"""
import io
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feed_guard import load_live, rows_for_compare  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.environ.get('LIVE_JSON', r'C:/dev/sg-property-decision/data/live.json')

data, provenance = load_live(LIVE, ['projects', 'districts'])
rows = rows_for_compare(data)

import json  # noqa: E402
DATA = json.dumps(rows, separators=(',', ':'), ensure_ascii=False)

# The rules, verbatim from the tested module. `export ` is stripped because the component's script
# is inline and cannot be a module; nothing else is altered.
logic = io.open(os.path.join(HERE, 'compare_logic.mjs'), encoding='utf-8').read()
LOGIC = re.sub(r'^export ', '', logic, flags=re.M)
LOGIC = re.sub(r'^import .*$\n', '', LOGIC, flags=re.M)

# ---------------------------------------------------------------------------------------------
# The estimated column. Thomson Reserve has no transaction record — nothing has been resold — so
# it cannot be scored against buildings that do have one. It is carried as a reference column,
# never ranked, with each cell stating whether it is a fact, our assumption, or not yet knowable.
#
# Facts and their primary sources:
#   lease   fresh 99 years. The collective sale paid the lease upgrading premium for a fresh
#           99-year lease (Edmund Tie & Company award announcement, 25 November 2024).
#   MRT     about 180 m to Upper Thomson MRT (TE8) exit 1, measured to the site boundary.
#   price   S$2,900 psf is OURS. It is the middle of the three illustrative prices in the article,
#           chosen to straddle what observed land multiples imply. Not a quote, not a forecast.
# ---------------------------------------------------------------------------------------------
D20 = [r for r in data['districts']['rows'] if str(r.get('d')) == '20'][0]
BANDS = [b[2] for b in D20['psf_sz']]          # median psf of each size band, from the feed
ASSUMED = 2900
gaps = sorted(round((ASSUMED / b - 1) * 100) for b in BANDS if b)

REF = {
    'p': 'Thomson Reserve', 'd': 'D20', 'n': D20['name'], 'est': 1,
    'cells': {
        'Median resale price': ['S$2,900 psf', 'our illustration, not a price list'],
        'Price change, 12 months': ['no history', 'nothing has traded'],
        'Against its district': [f'+{gaps[0]}% to +{gaps[-1]}%',
                                 'at S$2,900, against each D20 size band'],
        'Resales in 12 months': ['none', 'nothing has been resold'],
        'Lease remaining': ['99 yrs', 'fresh 99-year lease'],
        # Measured to the site boundary, where the others are measured from a built block. That
        # difference is why it carries a fact and still is not ranked against them.
        'To the nearest MRT': ['about 180 m', 'Upper Thomson (TE8), to the site edge'],
        'Size that actually trades': ['not published', 'no price list until October'],
        'Typical price paid': ['not published', 'depends on the size mix'],
    },
}

from gen_compare_head import HEAD  # noqa: E402
from gen_compare_body import BODY  # noqa: E402

out = (HEAD
       .replace('__DATA__', DATA)
       .replace('__PROVENANCE__', provenance)
       .replace('__REF__', json.dumps(REF, separators=(',', ':'), ensure_ascii=False))
       + BODY.replace('__LOGIC__', LOGIC))

labels = set(re.findall(r"\{ label: '([^']+)'", BODY))
missing = labels - set(REF['cells'])
extra = set(REF['cells']) - labels
if missing or extra:
    raise SystemExit(f'REF cells out of step with METRICS — missing {sorted(missing)}, '
                     f'unknown {sorted(extra)}')

path = os.path.join(HERE, '..', 'src', 'components', 'CondoCompare.astro')
from jsx_space_lint import assert_clean
assert_clean(out, 'CondoCompare.astro')   # a newline before an expression eats the space; five have shipped
io.open(path, 'w', encoding='utf-8').write(out)
print('written', len(out), 'bytes ·', len(rows), 'projects ·',
      len({r['d'] for r in rows}), 'districts')
print('provenance:', provenance)
