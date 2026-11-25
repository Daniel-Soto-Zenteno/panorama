const { launchBrowser } = require('./browser-runtime.cjs');
const fs=require('fs');
(async()=>{
 const b=await launchBrowser();const p=await b.newPage({viewport:{width:1366,height:768}});
 await p.goto('http://127.0.0.1:8011/activity/5/');await p.locator('.narrow').screenshot({path:'docs/evidencias/C12-ficha-detalle.png'});
 await p.goto('http://127.0.0.1:8011/community/1/');await p.locator('article.panel').first().screenshot({path:'docs/evidencias/C13-foro-detalle.png'});
 const creds=Object.fromEntries(fs.readFileSync('.demo-credentials.txt','utf8').replace(/^\uFEFF/,'').split(/\r?\n/).filter(l=>l.includes(': ')).map(l=>l.split(': ')));
 await p.goto('http://127.0.0.1:8011/account/login/');await p.locator('#id_username').fill('demo_moderador');await p.locator('#id_password').fill(creds.demo_moderador);await p.getByRole('button',{name:'Continuar'}).click();
 await p.goto('http://127.0.0.1:8011/moderation/');await p.locator('.table-wrap').screenshot({path:'docs/evidencias/C14-auditoria.png'});
 await p.goto('http://127.0.0.1:8011/propose/actividad/');await p.locator('#id_titulo').fill('Encuentro de lectura vecinal');await p.locator('#id_descripcion').fill('Propuesta ficticia de una actividad comunitaria.');
 await p.locator('#id_titulo').locator('..').screenshot({path:'docs/evidencias/C17-propuesta-extracto.png'});
 await p.setViewportSize({width:360,height:800});await p.goto('http://127.0.0.1:8011/propose/actividad/');await p.screenshot({path:'docs/evidencias/C15-propuesta-viewport.png'});
 await p.goto('http://127.0.0.1:8011/');await p.screenshot({path:'docs/evidencias/C16-explorar-viewport.png'});
 await b.close();
})();
