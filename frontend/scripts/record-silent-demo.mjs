import { chromium } from '@playwright/test';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const rehearsal=process.env.DEMO_REHEARSAL==='1';
const baseOutput=resolve('../docs/demo-video-v4');
const output=rehearsal?`${baseOutput}/rehearsal`:baseOutput;
const scenes=JSON.parse(await readFile(`${baseOutput}/storyboard.json`,'utf8'));
const script=Object.fromEntries(scenes.map(s=>[s.id,s]));
await mkdir(`${output}/raw`,{recursive:true});
const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,
 recordVideo:{dir:`${output}/raw`,size:{width:1440,height:1000}}});
const page=await context.newPage();
const start=Date.now(), seconds=()=>(Date.now()-start)/1000;
const chapters=[], waits=[], errors=[];
page.on('pageerror',error=>errors.push(error.message));
const pause=ms=>page.waitForTimeout(rehearsal?Math.min(ms,250):ms);

async function caption(id){
 const scene=script[id];
 await page.evaluate(({label,caption})=>{
  let bar=document.getElementById('recording-caption');
  if(!bar){bar=document.createElement('div');bar.id='recording-caption';
   bar.style.cssText='position:fixed;bottom:16px;left:28px;right:28px;z-index:2147483647;pointer-events:none;background:#173e33;color:#fffdf3;border:1px solid #436454;border-radius:12px;padding:18px 22px;box-shadow:0 5px 28px #0003;display:flex;align-items:center;gap:24px;font-family:Arial,sans-serif;min-height:82px';document.body.appendChild(bar);}
  bar.replaceChildren();
  const tag=document.createElement('strong');tag.textContent=label;tag.style.cssText='color:#ffb487;font-size:13px;letter-spacing:1px;max-width:290px;flex-shrink:0';
  const text=document.createElement('span');text.textContent=caption;text.style.cssText='font-size:22px;line-height:1.35';
  bar.append(tag,text);
 },scene);
 const chapter={...scene,at:seconds()};chapters.push(chapter);console.log(`Scene ${id}`);return chapter;
}
async function scene(id){const s=await caption(id);await pause(s.hold_seconds*1000);}
async function click(locator){await locator.hover();await pause(250);await locator.click();await page.mouse.move(1400,155);}
async function focus(selector,offset=90){
 await page.locator(selector).first().evaluate((el,offset)=>{
  const panel=el.closest('.guide-panel');
  if(panel)panel.scrollTo({top:el.getBoundingClientRect().top-panel.getBoundingClientRect().top+panel.scrollTop-offset,behavior:'smooth'});
  else window.scrollTo({top:el.getBoundingClientRect().top+scrollY-offset,behavior:'smooth'});
 },offset);await pause(900);
}
async function tab(name){await click(page.getByRole('tab',{name,exact:true}));await focus('.guide-body',85);}
async function investigate(id,expected){
 await click(page.locator('.find-button'));
 await page.locator('.investigation').waitFor();
 const chapter=await caption(id),from=chapter.at;
 await page.locator('.mode-notice').waitFor({timeout:240000});
 const to=seconds();waits.push({start:from,end:to,keep_start:4.5,keep_end:1.5});
 await pause(Math.max(500,(chapter.hold_seconds-(seconds()-from))*1000));
 if(!(await page.locator('.mode-notice').innerText()).includes('Investigated by your local Ollama agent'))throw new Error('The recording requires a real agent result.');
 if(!(await page.locator('.primary-card h3').innerText()).includes(expected))throw new Error('Unexpected scenario winner');
 if(await page.locator('.alternative-card').count()!==2)throw new Error('Expected two alternatives');
}
let completed=false, contentEnd=null;
try{
 await page.goto('http://localhost:3000',{waitUntil:'networkidle'});
 await page.getByRole('button',{name:'Local agent ready'}).waitFor({timeout:20000});
 await page.screenshot({path:`${output}/poster.png`});
 await scene('intro');
 await focus('.search-section',80);
 await click(page.getByRole('button',{name:'Family day, on a budget'}));
 await scene('family');
 await click(page.locator('.more-preferences summary'));
 await scene('filters');
 await click(page.locator('.more-preferences summary'));
 await investigate('family-ai','San Jose Giants');
 await focus('.results-heading',85);await scene('family-pick');
 await focus('.primary-card .event-content',90);await scene('details');
 await click(page.locator('.primary-card .score-details summary'));
 await focus('.primary-card .score-details',85);await scene('score');
 await click(page.locator('.primary-card .score-details summary'));
 await focus('.alternatives-section',85);await scene('alternatives');
 await focus('.guide-preview',75);await scene('preview');
 await click(page.locator('.guide-preview').getByRole('button',{name:'Full venue guide'}));
 await focus('.guide-body',85);await scene('bags');
 await focus('.policy-card:nth-child(3)',110);await scene('essentials');
 await tab('food & arrival');await scene('food');
 await focus('.guide-body .subheading:nth-of-type(2)',100);await scene('arrival');
 await tab('parking & comfort');await focus('.preparation-section:nth-child(1)',90);await scene('parking');
 await focus('.preparation-section:nth-child(2)',85);await scene('seating');
 if(await page.locator('.weather-stats').count()!==1)throw new Error('Family forecast must be available for this walkthrough.');
 await focus('.weather-summary',90);await scene('weather');
 await page.screenshot({path:`${output}/weather.png`});
 await focus('.attire-section .suggestion-label',110);await scene('attire');
 await tab('sources');await scene('sources');
 await focus('.feedback',90);await scene('feedback');
 await click(page.getByRole('button',{name:'Thumbs up',exact:true}));
 await click(page.getByRole('button',{name:'I’d attend',exact:true}));
 await page.getByRole('dialog').getByRole('status').filter({hasText:'Saved locally'}).waitFor();
 await pause(900);
 await click(page.getByRole('button',{name:'Close guide'}));
 await focus('.search-section',90);
 await click(page.getByRole('button',{name:'The iconic Bay Area experience'}));
 await scene('iconic');
 await investigate('iconic-ai','Big Game');
 await focus('.results-heading',85);await scene('iconic-pick');
 await focus('.primary-card .event-content',90);await scene('iconic-details');
 await focus('.alternatives-section',85);await scene('iconic-alternatives');
 await focus('.how-it-works',160);await scene('closing');
 contentEnd=seconds();
 if(errors.length)throw new Error(errors.join('\n'));
 completed=true;
}finally{
 const duration=seconds();await context.close();const raw=await page.video().path();
 await writeFile(`${output}/recording.json`,JSON.stringify({raw,duration,chapters,waits,errors,completed,contentEnd},null,2));
 await browser.close();console.log(JSON.stringify({completed,duration,waits,errors}));
}
