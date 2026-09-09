// Pads a cover image to an exact 2:1 canvas so the article hero's fixed
// aspect-2/1 crop (src/pages/[slug].astro) never has to slice into real
// content. Any cover shorter/narrower than 2:1 gets cropped top-and-bottom
// by that container's object-cover — this script prevents that by widening
// the canvas instead, with color bars sampled from the image's own edges so
// the seam is as close to invisible as a flat fill can get.
//
// Usage: node scripts/pad-cover-to-2x1.cjs <input> <output> [maxWidth=1600]
//
// Why a script and not one-off shell one-liners: this defect has shipped
// repeatedly (rising-rates, where-is-your-enough-point, and a 2026-09-09
// sweep found it on 16 of 25 live covers at once) because every cover
// gets authored at whatever ratio the source art happens to be, and
// nothing checks it against the 2:1 container before publishing. Run this
// on every new cover before it goes into public/img/Published/.
//
// A cover already at (or past) 2:1 is left alone — extend() with 0 padding
// on both sides is a safe no-op, so it is always fine to run this
// unconditionally rather than checking the ratio yourself first.
const sharp = require('sharp');
const path = require('path');

async function padToTwoToOne(inputPath, outputPath, maxWidth = 1600) {
  const meta = await sharp(inputPath).metadata();
  const targetW = meta.height * 2;
  const padTotal = Math.max(0, targetW - meta.width);
  const left = Math.floor(padTotal / 2);
  const right = padTotal - left;

  if (padTotal === 0) {
    await sharp(inputPath)
      .resize({ width: maxWidth, withoutEnlargement: true })
      .jpeg({ quality: 82, mozjpeg: true })
      .toFile(outputPath);
    return { padded: false, width: meta.width, height: meta.height };
  }

  const leftStrip = await sharp(inputPath)
    .extract({ left: 0, top: 0, width: Math.min(10, meta.width), height: meta.height })
    .resize(1, 1).raw().toBuffer();
  const rightStrip = await sharp(inputPath)
    .extract({ left: Math.max(0, meta.width - 10), top: 0, width: Math.min(10, meta.width), height: meta.height })
    .resize(1, 1).raw().toBuffer();

  // Two sequential extend() calls, each round-tripped through a buffer
  // rather than chained straight into resize().toFile() — chaining
  // extend+extend+resize+toFile in one pipeline has silently produced the
  // wrong output dimensions before (sharp/libvips quirk under this
  // combination); going through intermediate buffers has been reliable.
  const step1 = await sharp(inputPath)
    .extend({ left, right: 0, top: 0, bottom: 0, background: { r: leftStrip[0], g: leftStrip[1], b: leftStrip[2] } })
    .png().toBuffer();

  const step2 = await sharp(step1)
    .extend({ left: 0, right, top: 0, bottom: 0, background: { r: rightStrip[0], g: rightStrip[1], b: rightStrip[2] } })
    .png().toBuffer();

  await sharp(step2)
    .resize({ width: maxWidth, withoutEnlargement: true })
    .jpeg({ quality: 82, mozjpeg: true })
    .toFile(outputPath);

  return { padded: true, width: targetW, height: meta.height, left, right };
}

module.exports = { padToTwoToOne };

if (require.main === module) {
  const [, , input, output, maxWidthArg] = process.argv;
  if (!input || !output) {
    console.error('Usage: node scripts/pad-cover-to-2x1.cjs <input> <output> [maxWidth=1600]');
    process.exit(1);
  }
  padToTwoToOne(path.resolve(input), path.resolve(output), maxWidthArg ? Number(maxWidthArg) : 1600)
    .then((r) => console.log(JSON.stringify(r)))
    .catch((e) => { console.error(e); process.exit(1); });
}
