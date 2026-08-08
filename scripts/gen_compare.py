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

from gen_compare_head import HEAD  # noqa: E402
from gen_compare_body import BODY  # noqa: E402

out = (HEAD
       .replace('__DATA__', DATA)
       .replace('__PROVENANCE__', provenance)
       + BODY.replace('__LOGIC__', LOGIC))

path = os.path.join(HERE, '..', 'src', 'components', 'CondoCompare.astro')
from jsx_space_lint import assert_clean
assert_clean(out, 'CondoCompare.astro')   # a newline before an expression eats the space; five have shipped
io.open(path, 'w', encoding='utf-8').write(out)
print('written', len(out), 'bytes ·', len(rows), 'projects ·',
      len({r['d'] for r in rows}), 'districts')
print('provenance:', provenance)
