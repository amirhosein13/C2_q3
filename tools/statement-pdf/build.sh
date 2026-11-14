#!/bin/bash
# Builds a Persian (RTL) PDF from a statement written in Markdown with $...$ / $$...$$ math.
# usage: tools/statement-pdf/build.sh <statement.md> <out.pdf>
# Requirements: pandoc (>= 2.19, for --embed-resources), node with the "playwright" package
# and its Chromium, and the font Vazirmatn installed system-wide (Ubuntu: apt install fonts-vazirmatn).
# Math is rendered as MathML by pandoc and laid out by Chromium.
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: $0 <statement.md> <out.pdf>" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
src="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
out="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
fc-list : family | grep -i vazirmatn > /dev/null || { echo "font Vazirmatn is not installed" >&2; exit 1; }
title="$(grep -m1 '^# ' "${src}" | sed 's/^# //')"
html="$(mktemp --suffix=.html)"
trap 'rm -f "${html}"' EXIT
pandoc "${src}" -f markdown -t html5 -s --mathml \
	--metadata pagetitle="${title:-statement}" --metadata lang=fa --metadata dir=rtl \
	--css "${here}/style.css" --embed-resources -o "${html}"
# Chromium lays out MathML using the inherited text direction; isolate every formula as LTR.
sed -i -e 's|<math |<span dir="ltr" class="ltr-math"><math dir="ltr" |g' -e 's|</math>|</math></span>|g' "${html}"
HTML="${html}" OUT="${out}" node -e '
const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + process.env.HTML);
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: process.env.OUT, format: "A4", printBackground: true, preferCSSPageSize: true });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });'
echo "written ${out}"
