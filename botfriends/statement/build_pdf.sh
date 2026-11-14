#!/bin/bash
# Builds botfriends.pdf from index.md (Persian, RTL).
# Requirements: pandoc, node + playwright (Chromium), font "Vazirmatn" (Ubuntu: apt install fonts-vazirmatn).
set -euo pipefail
cd "$(dirname "$0")"
pandoc index.md -s --mathml --metadata pagetitle="دوستان ربات" --metadata lang=fa --metadata dir=rtl --css pdf.css --embed-resources -o .index.pdf.html
# MathML ignores CSS direction: force left-to-right formulas inside RTL text
sed -i -e 's|<math |<span dir="ltr" class="ltr-math"><math dir="ltr" |g' -e 's|</math>|</math></span>|g' .index.pdf.html
node -e '
const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + process.cwd() + "/.index.pdf.html");
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: "botfriends.pdf", format: "A4", printBackground: true, preferCSSPageSize: true });
  await b.close();
})();'
rm -f .index.pdf.html
echo "built $(pwd)/botfriends.pdf"
