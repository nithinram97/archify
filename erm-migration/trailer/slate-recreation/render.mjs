// Renders the recreated Slate screens to ../textures/slate_<name>.png (1600 x 1000).
// Run from a folder where Playwright is installed:  node <path>/render.mjs
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
for (const s of ['heat', 'report', 'onepager', 'tracker', 'table', 'search']) {
  await page.goto(`file://${here}/slate.html?s=${s}`);
  await page.waitForFunction(() => window.__done === true);
  await page.waitForTimeout(200);
  await page.screenshot({ path: path.join(here, '..', 'textures', `slate_${s}.png`) });
  console.log('slate_' + s);
}
await browser.close();
