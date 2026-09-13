import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

// Record real localhost interactions. Captions exist only in this browser session.
const output = resolve('../docs/demo-video-v2');
await mkdir(output, { recursive: true });
const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1,
  recordVideo: { dir: `${output}/raw`, size: { width: 1440, height: 1000 } },
});
const page = await context.newPage();
const start = Date.now();
const seconds = () => (Date.now() - start) / 1000;
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const chapters = [];
async function caption(label, message) {
  chapters.push({ at: seconds(), label, message });
  console.log(label, message);
  await page.evaluate(({ label, message }) => {
    let bar = document.getElementById('recording-caption');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'recording-caption';
      bar.style.cssText = 'position:fixed;bottom:18px;left:36px;right:36px;z-index:2147483647;pointer-events:none;background:#152934;color:#fff;border-radius:14px;padding:19px 24px;box-shadow:0 6px 32px #0003;display:flex;align-items:center;gap:26px;font-family:Arial,sans-serif;';
      document.body.appendChild(bar);
    }
    bar.replaceChildren();
    const tag = document.createElement('strong');
    tag.textContent = label;
    tag.style.cssText = 'color:#ffab78;font-size:14px;letter-spacing:1.4px;white-space:nowrap';
    const text = document.createElement('span');
    text.textContent = message;
    text.style.cssText = 'font-size:21px;line-height:1.4';
    bar.append(tag, text);
  }, { label, message });
}
const pause = ms => page.waitForTimeout(ms);
async function focus(selector, offset = 90) {
  await page.locator(selector).first().evaluate((el, offset) => {
    window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' });
  }, offset);
  await pause(1000);
}
async function click(locator) {
  await locator.hover();
  await pause(350);
  await locator.click();
}
let waitStart, waitEnd;
let completed = false;
try {
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Local agent ready' }).waitFor({ timeout: 15000 });
  await caption('THE PICK', 'Your personal Bay Area sports concierge. Discover. Decide. Prepare.');
  await pause(4500);
  await focus('.search-section', 80);
  await caption('01 / DISCOVER', 'Start with a family day: four people, nearby, with a $120 total budget.');
  await click(page.getByRole('button', { name: 'Family day, on a budget' }));
  await pause(5500);
  await caption('LOCAL AI', 'Ollama investigates the request and supporting sources. Waiting time shortened.');
  await click(page.locator('.find-button'));
  waitStart = seconds();
  await page.locator('.mode-notice').waitFor({ timeout: 240000 });
  waitEnd = seconds();
  const notice = await page.locator('.mode-notice').innerText();
  if (!notice.includes('Investigated by your local Ollama agent')) throw new Error(notice);
  if (await page.locator('.event-card').count() !== 3) throw new Error('Expected three real recommendations');
  await focus('.results-heading', 100);
  await caption('02 / DECIDE', 'One clear recommendation, chosen for this family’s budget and nearby outing.');
  await pause(5500);
  await focus('.primary-card .score-row', 150);
  await caption('FIT + CONFIDENCE', 'Compare personal fit, evidence confidence, ticket prices and outing estimates.');
  await pause(5500);
  await click(page.locator('.primary-card .score-details summary'));
  await focus('.primary-card .score-details', 95);
  await caption('TRANSPARENT SCORING', 'Open the score breakdown to see the factors and their weights.');
  await pause(6500);
  await click(page.locator('.primary-card .score-details summary'));
  await focus('.alternatives-section', 80);
  await caption('TWO STRONG ALTERNATIVES', 'Two other experiences, with their own scores, costs and tradeoffs.');
  await pause(5500);
  await focus('.guide-preview', 80);
  await caption('03 / PREPARE', 'Bags, food and arrival guidance are right here beneath your pick.');
  await pause(5500);
  await click(page.locator('.guide-preview').getByRole('button', { name: 'Full venue guide' }));
  await caption('THE FULL GUIDE', 'Open detailed policies, practical advice and links to official sources.');
  await pause(4000);
  await caption('UNKNOWNS STAY VISIBLE', 'Conflicting official guidance is flagged so you know what to confirm.');
  await pause(4000);
  await click(page.getByRole('tab', { name: 'food & arrival' }));
  await caption('FOOD + ARRIVAL', 'Food preferences and arrival advice include clear information gaps.');
  await pause(6500);
  await click(page.getByRole('tab', { name: 'sources', exact: true }));
  await caption('CHECK THE EVIDENCE', 'Source links and review dates make the venue guidance easy to inspect.');
  await pause(6000);
  await click(page.getByRole('button', { name: 'Close guide' }));
  await focus('.how-it-works', 180);
  await caption('THE PICK', 'We do the homework. You make the memories.');
  await pause(5000);
  await caption('ABOUT THIS DEMO', 'Recorded from the local app. Event dates and prices are illustrative, not live listings.');
  await pause(5500);
  if (errors.length) throw new Error(errors.join('\n'));
  await page.screenshot({ path: `${output}/poster.png` });
  completed = true;
} finally {
  const duration = seconds();
  await context.close();
  const raw = await page.video().path();
  await writeFile(`${output}/recording.json`, JSON.stringify({ raw, duration, waitStart, waitEnd, chapters, errors, completed }, null, 2));
  await browser.close();
  console.log(JSON.stringify({ raw, duration, waitStart, waitEnd, errors }));
}
