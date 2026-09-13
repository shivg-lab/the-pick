import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

await mkdir('../docs/screenshots/redesign', {recursive:true});
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const errors=[];const runs=[];const layouts=[];
page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://localhost:3000');
await page.getByRole('button',{name:'Local agent ready'}).waitFor();
for (const scenario of ['family','iconic']) {
 if(scenario==='iconic')await page.getByRole('button',{name:'The iconic Bay Area experience'}).click();
 const start=Date.now();
 await page.locator('.find-button').click();
 await page.locator('.investigation').waitFor();
 if(!await page.locator('#query').isDisabled())throw new Error('Request editable during inference');
 await page.screenshot({path:`../docs/screenshots/redesign/${scenario}-investigation.png`});
 await page.locator('.mode-notice').waitFor({timeout:240000});
 if(!(await page.locator('.mode-notice').innerText()).includes('Investigated by your local Ollama agent'))throw new Error('Unexpected fallback');
 const title=await page.locator('.primary-card h3').innerText();
 if(!title.includes(scenario==='family'?'San Jose Giants':'Big Game'))throw new Error(`Unexpected winner: ${title}`);
 if(await page.locator('.alternative-card').count()!==2)throw new Error('Expected two alternatives');
 const winner=await page.locator('.primary-card').boundingBox();
 const alternative=await page.locator('.alternative-card').first().boundingBox();
 if(winner.width<alternative.width*1.8)throw new Error('Winner lacks visual priority');
 await page.locator('.results-heading').evaluate(el=>window.scrollTo({top:el.getBoundingClientRect().top+scrollY-65}));
 await page.waitForTimeout(700);
 await page.screenshot({path:`../docs/screenshots/redesign/${scenario}-desktop.png`});
 await page.screenshot({path:`../docs/screenshots/redesign/${scenario}-full.png`,fullPage:true});
 runs.push({scenario,winner:title,milliseconds:Date.now()-start,agent:true,alternatives:2});
 console.log(runs.at(-1));
 await page.locator('.preparation-preview').getByRole('button',{name:'Parking & comfort'}).click();
 await page.getByRole('dialog').waitFor();
 if(await page.locator('.preparation-source').count()<2)throw new Error('Missing parking or seating sources');
 await page.locator('.attire-section').scrollIntoViewIfNeeded();
 if(scenario==='family' && await page.locator('.weather-stats').count()!==1)throw new Error('Live weather unavailable in family demo');
 if(scenario==='iconic' && !(await page.locator('.weather-summary').innerText()).includes('outside the available forecast window'))throw new Error('Distant event showed a forecast');
 await page.screenshot({path:`../docs/screenshots/redesign/${scenario}-comfort.png`});
 if(!(await page.locator('.attire-section').innerText()).includes('comfort suggestions'))throw new Error('Missing comfort-suggestion label');
 await page.keyboard.press('Escape');
 if(scenario==='family') {
  for(const width of [768,900,1024,390,360]) {
   await page.setViewportSize({width,height:900});
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error(`Overflow at ${width}`);
   await page.locator('.primary-card').evaluate(el=>window.scrollTo({top:el.getBoundingClientRect().top+scrollY-20}));
   await page.waitForTimeout(500);
   await page.screenshot({path:`../docs/screenshots/redesign/family-${width}.png`});
   layouts.push({width,overflow:false});
  }
  await page.setViewportSize({width:390,height:844});
  await page.locator('.preparation-preview').getByRole('button',{name:'Parking & comfort'}).click();
  await page.locator('.weather-summary').scrollIntoViewIfNeeded();
  await page.screenshot({path:'../docs/screenshots/redesign/mobile-weather.png'});
  await page.keyboard.press('Escape');
  await page.locator('.guide-preview').getByRole('button',{name:'Full venue guide'}).click();
  await page.getByRole('dialog').waitFor();
  await page.screenshot({path:'../docs/screenshots/redesign/mobile-guide.png'});
  await page.keyboard.press('Shift+Tab');
  if(!await page.getByRole('dialog').evaluate(el=>el.contains(document.activeElement)))throw new Error('Dialog lost keyboard focus');
  await page.keyboard.press('Escape');
  if(!await page.locator('.guide-preview').getByRole('button',{name:'Full venue guide'}).evaluate(el=>el===document.activeElement))throw new Error('Guide did not restore focus');
  await page.setViewportSize({width:1440,height:1000});
 }
}
if(errors.length)throw new Error(errors.join('\n'));
await writeFile('../evals/redesign-integration.json',JSON.stringify({runs,layouts,errors,verifiedAt:new Date().toISOString()},null,2));
await browser.close();
