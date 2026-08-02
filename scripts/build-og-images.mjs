// Rasterise every SVG article cover to a JPEG for link previews.
//
// Why this exists: WhatsApp, Facebook, LinkedIn and X all refuse to render an
// SVG in a link preview. They do not fall back to the page title either — the
// share just collapses to a bare URL. Our covers are SVG, so pointing og:image
// at them silently killed previews everywhere.
//
// Runs on prebuild, so a new SVG cover cannot ship without its raster twin.
// MainLayout still guards with a fallback in case this has not been run.
import { readdir, mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const SRC = 'public/img/brand';
const OUT = 'public/img/brand/og';

// 1200x630 is the size every platform documents. The covers are 1200x600, so
// they are scaled and centre-cropped; the cover artwork keeps its subject well
// inside the safe zone, so the few pixels lost off each edge cost nothing.
const W = 1200;
const H = 630;

await mkdir(OUT, { recursive: true });
const files = (await readdir(SRC)).filter((f) => f.endsWith('.svg'));

let made = 0;
for (const f of files) {
  const from = path.join(SRC, f);
  const to = path.join(OUT, f.replace(/\.svg$/, '.jpg'));

  // Skip when the JPEG is already newer than its source.
  try {
    const [a, b] = await Promise.all([stat(from), stat(to)]);
    if (b.mtimeMs >= a.mtimeMs) continue;
  } catch { /* no output yet — build it */ }

  await sharp(from, { density: 200 })
    .resize(W, H, { fit: 'cover', position: 'centre' })
    .flatten({ background: '#081627' })       // the cover's own field colour
    .jpeg({ quality: 88, progressive: true, mozjpeg: true })
    .toFile(to);
  made++;
  console.log('og image:', to);
}
console.log(`[og] ${made} built, ${files.length - made} already current`);
