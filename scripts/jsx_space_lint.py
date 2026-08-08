"""Catch the JSX whitespace collapse before it reaches a page.

In Astro/JSX a newline between text and an adjacent expression or element is trimmed entirely, so

    ...homes sold there are under
    <b>{n(x)}</b>

renders as "under807". This has happened five times in this codebase and every one was caught by
reading the built page. The shape is always the same: a line ending in a word character, followed
by a line whose first non-space character starts an expression or a tag.

Called by the generators on their own template before writing. Exits non-zero if run directly and
anything matches.
"""
import io
import re
import sys

# a line ending in a letter/digit, then a line starting with { or < — the collapse shape
PATTERN = re.compile(r'([A-Za-z0-9,;:)])\n(\s*)(\{|<[a-zA-Z])')
# {' '} and &mdash;-style entities before the break are already explicit separators
SAFE_TAIL = re.compile(r"(\{' '\}|&[a-z]+;|&#\d+;)\s*$")


def markup_only(text):
    """The region where the collapse can actually happen: after the frontmatter, before <script>.

    Scanning the whole file yields only false positives — an object literal ending in `},` above a
    line starting with `{` looks identical to the prose case but is code, not template. Returns
    (region, line_offset) so reported line numbers still match the real file.
    """
    lines = text.split('\n')
    fence = [i for i, l in enumerate(lines) if l.strip() == '---']
    start = fence[1] + 1 if len(fence) >= 2 else 0
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].lstrip().startswith(('<script', '<style')):
            end = i
            break
    return lines[start:end], start


def find(text, label='template'):
    hits = []
    lines, offset = markup_only(text)
    for i, line in enumerate(lines[:-1]):
        nxt = lines[i + 1]
        if SAFE_TAIL.search(line):
            continue
        text_then_tag = (re.search(r'[A-Za-z0-9,;:)]$', line.rstrip())
                         and re.match(r'\s*(\{|<[a-zA-Z])', nxt))
        # The mirror image, which shipped once: a line ending in a closing tag or an expression,
        # followed by a line starting with a word. "...neighbourhood.</b>" + "The exit base" ran
        # together as "neighbourhood.The".
        tag_then_text = (re.search(r'(</[a-zA-Z][^>]*>|\})$', line.rstrip())
                         and re.match(r'\s*[A-Za-z0-9]', nxt))
        if text_then_tag or tag_then_text:
            # a line that is pure code, not prose, is not at risk
            if re.search(r'[;{}]\s*$', line) or line.lstrip().startswith('//'):
                continue
            hits.append((label, offset + i + 1, line.strip()[-58:], nxt.strip()[:40]))
    return hits


def assert_clean(text, label='template'):
    hits = find(text, label)
    if hits:
        print(f'JSX whitespace collapse risk in {label}:')
        for _, ln, a, b in hits:
            print(f'  line {ln}: ...{a}\n           {b}...   <- insert {{\' \'}} at the line end')
        raise SystemExit(1)


if __name__ == '__main__':
    bad = 0
    for path in sys.argv[1:]:
        h = find(io.open(path, encoding='utf-8').read(), path)
        for _, ln, a, b in h:
            print(f'{path}:{ln}: ...{a}  ||  {b}...')
        bad += len(h)
    print(f'{bad} risk(s)')
    sys.exit(1 if bad else 0)
