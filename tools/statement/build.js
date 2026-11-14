// usage: node build.js <statement.md> <out.pdf> [out.html]
// Requires: npm install (in this directory) and Playwright + Chromium (preinstalled or `npm i playwright`).
const fs = require('fs'), path = require('path');
const md = require('markdown-it')({ html: true });
const tm = require('markdown-it-texmath');
md.use(tm, { engine: require('katex'), delimiters: 'dollars', katexOptions: { throwOnError: true } });

const [src, outPdf, outHtml] = process.argv.slice(2);
const nm = path.join(__dirname, 'node_modules');
const font = (f) => 'data:font/woff2;base64,' + fs.readFileSync(path.join(nm, '@fontsource/vazirmatn/files', f)).toString('base64');
const katexCss = 'file://' + path.join(nm, 'katex/dist/katex.min.css');
const body = md.render(fs.readFileSync(src, 'utf8'));
const title = (fs.readFileSync(src, 'utf8').match(/^# (.*)$/m) || [, 'statement'])[1];

const html = `<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>${title}</title>
<link rel="stylesheet" href="${katexCss}">
<style>
@font-face{font-family:Vaz;font-weight:400;src:url(${font('vazirmatn-arabic-400-normal.woff2')}) format('woff2');unicode-range:U+0600-06FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFF;}
@font-face{font-family:Vaz;font-weight:700;src:url(${font('vazirmatn-arabic-700-normal.woff2')}) format('woff2');unicode-range:U+0600-06FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFF;}
@font-face{font-family:Vaz;font-weight:400;src:url(${font('vazirmatn-latin-400-normal.woff2')}) format('woff2');}
@font-face{font-family:Vaz;font-weight:700;src:url(${font('vazirmatn-latin-700-normal.woff2')}) format('woff2');}
@page{size:A4;margin:18mm 16mm;}
body{font-family:Vaz,sans-serif;font-size:11.5pt;line-height:1.85;color:#111;text-align:justify;}
h1{text-align:center;font-size:22pt;border-bottom:2px solid #333;padding-bottom:6px;margin-top:0}
h2{font-size:14pt;border-bottom:1px solid #bbb;padding-bottom:2px;margin-top:22px}
pre,code{font-family:"DejaVu Sans Mono",monospace;font-size:9.5pt;direction:ltr;unicode-bidi:isolate}
pre{background:#f4f4f4;border:1px solid #ddd;padding:8px 10px;text-align:left;white-space:pre-wrap;page-break-inside:avoid;margin:6px 0}
p code,li code{background:#f1f1f1;padding:0 3px;border-radius:3px}
.katex{direction:ltr;unicode-bidi:isolate;font-size:1.05em}
eq,eqn{direction:ltr} section.eqno, .katex-display{direction:ltr}
table{border-collapse:collapse;margin:8px auto;page-break-inside:avoid}
th,td{border:1px solid #999;padding:4px 12px;vertical-align:top}
th{background:#eee}
td pre{border:none;background:none;margin:0;padding:0}
.io{display:flex;gap:16px;direction:rtl;page-break-inside:avoid}
.io>div:first-child{flex:3}.io>div:last-child{flex:1}
pre.cols{column-count:4;column-rule:1px solid #ddd}
</style></head><body>${body}</body></html>`;

(async () => {
  const tmp = path.join(path.dirname(path.resolve(outPdf)), '.statement-build.html');
  fs.writeFileSync(outHtml || tmp, html);
  const { chromium } = require('playwright');
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(outHtml || tmp));
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: outPdf, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
  if (!outHtml) fs.unlinkSync(tmp);
  console.log('written', outPdf);
})().catch(e => { console.error(e); process.exit(1); });
