const { launchBrowser } = require('./browser-runtime.cjs');
const fs=require('fs');
(async()=>{
 const browser=await launchBrowser();
 const page=await browser.newPage({viewport:{width:360,height:800}});
 const creds=Object.fromEntries(fs.readFileSync('.demo-credentials.txt','utf8').replace(/^\uFEFF/,'').split(/\r?\n/).filter(l=>l.includes(': ')).map(l=>l.split(': ')));
 await page.goto('http://127.0.0.1:8011/account/login/');await page.locator('#id_username').fill('demo_vecina');await page.locator('#id_password').fill(creds.demo_vecina);await page.getByRole('button',{name:'Continuar'}).click();
 const sizes=[];
 for(const route of ['/propose/actividad/','/profile/','/mine/']){
  await page.goto('http://127.0.0.1:8011'+route);sizes.push({route,...await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}))});
 }
 await page.goto('http://127.0.0.1:8011/propose/actividad/');
 await page.screenshot({path:'docs/evidencias/C11-propuesta-movil.png',fullPage:true});
 await page.keyboard.press('Tab');const firstFocus=await page.evaluate(()=>document.activeElement.textContent.trim());
 await page.locator('#id_titulo').focus();await page.keyboard.type('Propuesta mediante teclado');await page.keyboard.press('Tab');const nextFocus=await page.evaluate(()=>document.activeElement.id);
 const result={id:'CP36',test:'Propuesta móvil y recorrido parcial por teclado',sizes,firstFocus,nextFocus,passed:sizes.every(s=>s.width>=s.scroll)&&firstFocus==='Saltar al contenido'&&nextFocus==='id_descripcion'};
 fs.writeFileSync('docs/evidencias/acceso.json',JSON.stringify(result,null,2));console.log(result);await browser.close();
 if(!result.passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
