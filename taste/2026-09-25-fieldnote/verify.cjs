// Archive regression only; this does not rerun the model. Requires Playwright.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({viewport: {width:1512,height:717}});
    const report = {date:new Date().toISOString(),kind:'archive-desktop-regression',model_rerun:false,browser:browser.version(),viewport:[1512,717],pages:{}};
    for (const name of ['baseline','with-taste']) {
      const file = path.join(__dirname,name,'index.html');
      const requests = [], errors = [];
      const onRequest = r => {if (/^https?:/.test(r.url())) requests.push(r.url());};
      const onError = e => errors.push(e.message);
      page.on('request',onRequest); page.on('pageerror',onError);
      await page.goto(pathToFileURL(file).href);
      const checks = await page.evaluate(() => ({images:[...document.images].every(i=>i.complete && i.naturalWidth>0 && i.alt),no_overflow:document.documentElement.scrollWidth<=innerWidth,h1:document.querySelectorAll('h1').length,sections:document.querySelectorAll('main section').length,title:document.querySelector('h1').innerText.replace(/\s+/g,' ').trim()}));
      assert(checks.images && checks.no_overflow && checks.h1===1 && checks.sections===4);
      assert.equal(checks.title,'Keep the source close.');
      await page.getByRole('button',{name:/Download macOS beta/}).first().click();
      assert.equal(await page.locator('dialog[open]').count(),1);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('dialog[open]').count(),0);
      assert.deepEqual(requests,[]); assert.deepEqual(errors,[]);
      const html=fs.readFileSync(file,'utf8');
      assert(html.includes(':focus-visible') && html.includes('prefers-reduced-motion'));
      report.pages[name]={...checks,dialog_open_close:true,remote_requests:requests,page_errors:errors,focus_and_reduced_motion_source:true,html_sha256:crypto.createHash('sha256').update(html).digest('hex')};
      page.off('request',onRequest); page.off('pageerror',onError);
    }
    await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href);
    assert(await page.evaluate(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0)));
    for(const href of await page.locator('a').evaluateAll(as=>as.map(a=>a.getAttribute('href')).filter(h=>!/^https?:/.test(h)))) assert(fs.existsSync(path.join(__dirname,href==='verification.json'?'verify.cjs':href)));
    report.comparison_images_and_local_links=true;
    fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(report,null,2)+'\n');
    console.log('PASS: two original pages, desktop dialogs, assets and comparison links');
  } finally {await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1)});
