import { chromium } from 'playwright';
const only = process.argv[2];
const browser = await chromium.launch({ ...(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {}) });
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 } });
await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: 'http://127.0.0.1:5174' });
const page = await ctx.newPage();
page.on('pageerror', e => console.log('pageerror:', e.message.slice(0, 200)));
const base = 'http://127.0.0.1:5174/dashboard/1782864000000___2___1';
const go = async (p, w = 3500) => { await page.goto(base + p); await page.waitForTimeout(w); };
const shot = async (n) => { await page.screenshot({ path: `out/f-${n}.png` }); console.log('shot', n); };
const steps = {
  heat_title: async () => { await go('/maps'); await page.getByText('Title', { exact: true }).first().click(); await page.waitForTimeout(800); await shot('heat_title'); },
  search: async () => { await go('/maps'); await page.locator('header, div').getByText('Programme X · Quarterly risk review').first().click(); await page.waitForTimeout(600); await page.getByPlaceholder('Search dashboards...').fill('Prog'); await page.waitForTimeout(700); await shot('search'); },
  share: async () => { await go('/onepager'); await page.locator('[title="Copy Dashboard Link"]').first().click(); await page.waitForTimeout(500); await shot('share'); },
  slide: async () => { await go('/report', 4500); await page.getByRole('button', { name: /Slideshow/ }).first().click(); await page.waitForTimeout(2500); await shot('slide'); },
  filters: async () => { await go('/table'); await page.locator('[title="Toggle Filters"]').first().click(); await page.waitForTimeout(900); await shot('filters'); },
  onepager: async () => { await go('/onepager', 4500); await shot('onepager'); },
  report: async () => { await go('/report', 4500); await shot('report'); },
  tracker: async () => { await go('/action-tracker'); await shot('tracker'); },
  share2: async () => { await go('/maps'); await page.locator('[title="Copy Dashboard Link"]').first().click(); await page.waitForTimeout(400); await shot('share2'); },
  layout: async () => { await go('/onepager', 4500); await page.getByText('EDIT', { exact: true }).first().click(); await page.waitForTimeout(900); await shot('onepager_edit'); await page.getByText('Select Layout').first().click(); await page.waitForTimeout(1200); await shot('layout'); },
  slide2: async () => { await go('/report', 4500); await page.getByRole('button', { name: /Slideshow/ }).first().click(); await page.waitForTimeout(1500); for (let i = 0; i < 2; i++) { await page.keyboard.press('ArrowRight'); await page.waitForTimeout(900); } await shot('slide2'); },
  locked: async () => { await page.goto('http://127.0.0.1:5174/dashboards'); await page.waitForTimeout(3000); const row = page.locator('tr', { hasText: 'Operations · Hamburg risks' }).first(); await row.locator('button').last().click(); await page.waitForTimeout(700); await shot('locked_menu'); await page.getByText('Edit permissions').first().click(); await page.waitForTimeout(1800); await shot('locked_dialog'); },
  toast: async () => { await go('/maps'); await page.getByText('R-2041').first().click(); await page.waitForTimeout(800); await page.getByRole('button', { name: /^Edit$/ }).first().click(); await page.waitForTimeout(1500); await shot('drawer'); await page.getByRole('button', { name: /Validate$/ }).last().click(); for (const t of [150, 350, 600]) { await page.waitForTimeout(t); await shot('toast_' + t); } },
  tablesave: async () => { await go('/table'); await page.getByRole('button', { name: /^Save$/ }).first().click(); for (const t of [200, 500, 900]) { await page.waitForTimeout(t); await shot('tablesave_' + t); } },
  pill: async () => { await go('/maps'); await page.getByText('R-2041').first().click(); await page.waitForTimeout(1500); await shot('pill'); },
};
for (const [k, f] of Object.entries(steps)) {
  if (only && only !== k) continue;
  try { await f(); } catch (e) { console.log('FAIL', k, e.message.split('\n')[0].slice(0, 160)); }
}
await browser.close();
