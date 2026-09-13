import { test,expect, type Page } from '@playwright/test';

async function preferences(page:Page) {
 const toggle=page.getByRole('button',{name:'Your preferences',exact:true});
 if(await toggle.isVisible() && await toggle.getAttribute('aria-expanded')==='false')await toggle.click();
 await page.locator('.more-preferences summary').click();
}

test('discover, decide, prepare and save feedback through the real API',async({page},testInfo)=>{
 const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto('/');
 await expect(page.getByRole('heading',{level:1})).toContainText('experience.');
 await page.screenshot({path:`../docs/screenshots/v2-${testInfo.project.name}-landing.png`,fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
 await preferences(page);
 await page.getByLabel('Concierge mode').selectOption('fallback');
 await page.locator('.find-button').click();
 await expect(page.locator('.mode-notice')).toContainText('Fallback mode', {timeout:30000});
 await expect(page.locator('.event-card')).toHaveCount(3);
 await expect(page.locator('.primary-card h3')).toContainText('San Jose Giants');
 await expect(page.locator('.comparison')).toHaveCount(0);
 await expect(page.locator('.pick-ribbon')).toContainText('THE PICK FOR YOU');
 await expect(page.locator('.alternative-card')).toHaveCount(2);
 await expect(page.locator('.guide-preview')).toContainText('Official sources disagree');
 await expect(page.locator('.guide-preview')).toContainText('Vegetarian unverified');
 await expect(page.locator('.preparation-preview')).toContainText('Seating convenience');
 await page.locator('.preparation-preview').getByRole('button',{name:'Parking & comfort'}).click();
 await expect(page.getByRole('tab',{name:'parking & comfort',exact:true})).toHaveAttribute('aria-selected','true');
 await expect(page.locator('.preparation-details')).toContainText('Older guidance');
 await expect(page.locator('.preparation-details')).toContainText('third-base line');
 await expect(page.locator('.preparation-details')).toContainText('comfort suggestions');
 await expect(page.locator('.weather-summary')).toContainText('Weather for your outing');
 await expect(page.locator('.preparation-details')).toContainText('cannot be opened in seating areas');
 expect(await page.locator('.guide-panel').evaluate(el=>el.scrollWidth<=el.clientWidth)).toBeTruthy();
 await page.screenshot({path:`../docs/screenshots/parking-comfort-${testInfo.project.name}.png`});
 await page.locator('.weather-summary').scrollIntoViewIfNeeded();
 await page.screenshot({path:`../docs/screenshots/weather-${testInfo.project.name}.png`});
 await page.getByRole('dialog').getByRole('tab',{name:'sources',exact:true}).click();
 await expect(page.getByRole('dialog').locator('.source-card').first()).toBeVisible();
 await page.getByRole('button',{name:'Close guide'}).click();
 await expect(page.locator('.hero')).toHaveClass(/hero-compact/);
 await page.locator('.primary-card .score-details summary').click();
 await expect(page.locator('.primary-card .score-explainer')).toBeVisible();
 await page.locator('.primary-card .score-details summary').click();
 await page.locator('.results-section').screenshot({path:`../docs/screenshots/v2-${testInfo.project.name}-results.png`});
 await page.locator('.primary-card').getByRole('button',{name:'Know before you go'}).click();
 const dialog=page.getByRole('dialog');
 await expect(dialog).toBeVisible();
 await expect(dialog).toContainText('Official sources disagree');
 await page.screenshot({path:`../docs/screenshots/v2-${testInfo.project.name}-guide.png`});
 await dialog.getByRole('tab',{name:'food & arrival'}).click();
 await expect(dialog).toContainText('Vegetarian unverified');
 await dialog.getByRole('tab',{name:'sources',exact:true}).click();
 await expect(dialog.locator('.source-card').first()).toBeVisible();
 await dialog.getByRole('button',{name:'Thumbs up',exact:true}).click();
 await dialog.getByLabel('Anything we should know?').fill('Browser verification: the local outing fits my budget.');
 await dialog.getByRole('button',{name:'I’d attend'}).click();
 await expect(dialog.getByRole('status')).toContainText('Saved locally');
 await page.keyboard.press('Escape');
 await expect(dialog).toHaveCount(0);
 expect(errors).toEqual([]);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
});

test('strict constraints produce an honest no-results state',async({page})=>{
 await page.goto('/');await preferences(page);
 await page.getByLabel('Concierge mode').selectOption('fallback');
 await page.getByLabel('Budget ($)',{exact:true}).fill('0');
 await page.locator('.find-button').click();
 await expect(page.getByText('No qualifying events in this small sampler.')).toBeVisible({timeout:30000});
 await expect(page.locator('.event-card')).toHaveCount(0);
});

test('backend failure is visible and recoverable',async({page})=>{
 await page.route('**/api/providers',r=>r.abort());
 await page.route('**/api/jobs',r=>r.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'The local concierge is offline.'})}));
 await page.goto('/');await expect(page.getByRole('button',{name:/Backend unavailable/})).toBeVisible();
 await page.locator('.find-button').click();
 await expect(page.getByText('The local concierge is offline.')).toBeVisible();
 await expect(page.getByRole('button',{name:'Try again',exact:true})).toBeVisible();
});

test('Ollama setup state explains the missing models',async({page})=>{
 await page.route('**/api/providers',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({agent_ready:false,vector_ready:false,documents:44,chat_model:'qwen3:8b',embedding_model:'embeddinggemma',ollama:{reachable:false,chat_installed:false,embedding_installed:false}})}));
 await page.goto('/');
 await page.getByRole('button',{name:/Setup needed/}).click();
 await expect(page.locator('.provider-panel')).toContainText('ollama pull qwen3:8b');
 await expect(page.locator('.provider-panel')).toContainText('Run ingestion');
});


test('changed preferences keep the previous pick labeled until updated',async({page})=>{
 await page.goto('/');await preferences(page);
 await page.getByLabel('Concierge mode').selectOption('fallback');
 await page.locator('.find-button').click();
 await expect(page.locator('.primary-card h3')).toContainText('San Jose Giants',{timeout:30000});
 await page.getByRole('button',{name:'The iconic Bay Area experience'}).click();
 await expect(page.locator('.stale-results')).toContainText('previous search');
 await expect(page.locator('.primary-card h3')).toContainText('San Jose Giants');
 await page.locator('.stale-results').getByRole('button',{name:'Update my pick'}).click();
 await expect(page.locator('.primary-card h3')).toContainText('Big Game',{timeout:30000});
 await expect(page.locator('.stale-results')).toHaveCount(0);
 await expect(page.locator('.intent-summary')).toContainText('Open budget');
});

test('busy model has a retry action and leaves preferences editable',async({page})=>{
 await page.route('**/api/jobs',r=>r.fulfill({status:429,contentType:'application/json',body:JSON.stringify({detail:'The local model is working on another outing. Try again shortly.'})}));
 await page.goto('/');await page.locator('.find-button').click();
 await expect(page.getByText('The local model is working on another outing. Try again shortly.')).toBeVisible();
 await expect(page.getByRole('button',{name:'Try again',exact:true})).toBeEnabled();
 await expect(page.getByLabel('Describe your ideal outing')).toBeEnabled();
});
