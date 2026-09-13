import {test,expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const output='../output/qa';fs.mkdirSync(output,{recursive:true});
const fixture=(name:string)=>fs.readFileSync(path.join('..','sample-data',name),'utf-8');
for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
 test(`complete manual journey ${viewport.width}px`,async({page})=>{
  await page.setViewportSize(viewport);const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('/');
  await page.getByText('Or paste resume text',{exact:true}).click();
  await page.getByLabel('Base resume text',{exact:true}).fill(fixture('candidate-base.md'));
  await page.getByRole('button',{name:'Save resume text',exact:true}).click();
  await expect(page.getByText('Base resume added',{exact:true})).toBeVisible();
  await page.getByLabel('Add supporting evidence').setInputFiles({name:'project-evidence.md',mimeType:'text/plain',buffer:Buffer.from(fixture('project-evidence.md'))});
  await page.getByLabel('Add supporting evidence').setInputFiles({name:'course-evidence.md',mimeType:'text/plain',buffer:Buffer.from(fixture('course-evidence.md'))});
  if(await page.getByRole('button',{name:'Edit header',exact:true}).count())await page.getByRole('button',{name:'Edit header',exact:true}).click();
  await page.getByLabel('Full name',{exact:true}).fill('Mira Rao');
  await page.getByLabel('Contact line',{exact:true}).fill('mira@example.com');
  await page.getByLabel('Role title',{exact:true}).fill('Junior Frontend Developer');  await page.getByLabel('Company',{exact:true}).fill('CedarWorks Labs');
  await page.getByLabel('Job description Required',{exact:true}).fill(fixture('job-frontend.md'));
  await page.getByRole('button',{name:'Save job description',exact:true}).click();
  await page.locator('.kb-details summary').click();
  await page.getByPlaceholder('Relevant company or product facts').fill(fixture('company-knowledge.md'));
  await page.getByRole('button',{name:'Save company knowledge',exact:true}).click();
  await page.screenshot({path:`${output}/prepare-${viewport.width}.png`,fullPage:true});
  await page.getByRole('button',{name:'Review my evidence',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Here is what your documents support.'})).toBeVisible();
  await page.locator('.source-link').first().click();await expect(page.getByRole('dialog')).toBeVisible();
  await page.screenshot({path:`${output}/source-${viewport.width}.png`});
  await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).not.toBeVisible();
  await page.getByRole('button',{name:'Approve supported excerpts'}).click();
  await expect(page.getByRole('button',{name:'Build my application'})).toBeEnabled();
  await page.evaluate(()=>window.scrollTo(0,0));
  await page.screenshot({path:`${output}/evidence-${viewport.width}.png`});
  await page.getByRole('button',{name:'Build my application'}).click();
  await expect(page.getByRole('heading',{name:'Your application package is ready.'})).toBeVisible({timeout:30000});
  await expect.poll(()=>page.evaluate(()=>window.scrollY)).toBe(0);
  await expect(page.locator('.result-metrics')).toContainText('92');
  await expect(page.locator('.resume-image')).toBeVisible();
  expect(await page.locator('.resume-image').evaluate((img:HTMLImageElement)=>img.complete&&img.naturalWidth>0)).toBeTruthy();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
  await page.screenshot({path:`${output}/results-${viewport.width}.png`,fullPage:true});
  for(const name of ['Download resume','JSON report','Evidence report']){
   const url=await page.getByRole('link',{name,exact:true}).getAttribute('href');const response=await page.request.get(url!);expect(response.status()).toBe(200);expect(response.headers()['content-disposition']).toContain('attachment');
  }
  await page.getByRole('button',{name:'Claim sources',exact:true}).click();await page.locator('.claim .source-link').first().click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.getByRole('heading',{name:'Final draft claim',exact:true})).toBeVisible();await expect(page.getByRole('heading',{name:'Original document evidence',exact:true})).toBeVisible();await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Changes',exact:true}).click();await expect(page.getByRole('heading',{name:'What changed, and why'})).toBeVisible();
  await page.getByRole('button',{name:'Inspect activity log'}).click();await expect(page.getByRole('heading',{name:'Activity log'})).toBeVisible();
  await page.screenshot({path:`${output}/build-${viewport.width}.png`,fullPage:true});
  await page.reload();await expect(page.getByRole('heading',{name:'Your application package is ready.'})).toBeVisible();
  expect(errors).toEqual([]);
 });
}
test('invalid upload exposes useful error and clear session recovers',async({page})=>{
 await page.goto('/');await expect(page.getByLabel('Upload base resume')).toBeEnabled();await page.getByLabel('Upload base resume').setInputFiles({name:'broken.pdf',mimeType:'application/pdf',buffer:Buffer.from('not a PDF')});
 await expect(page.locator('.alert.error')).toContainText('could not be parsed');
  await page.getByRole('button',{name:'Clear temporary session'}).click();
  await expect(page.getByLabel('Upload base resume')).toBeEnabled();
 });

test('mobile pasted resume and long filename remain usable',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');
 await page.getByText('Or paste resume text',{exact:true}).click();
 await page.getByLabel('Base resume text',{exact:true}).fill('EDUCATION\nB. Tech in Information Technology at Example Institute.\nSKILLS\nReact, TypeScript, Git.');
 await page.getByRole('button',{name:'Save resume text',exact:true}).click();
 await expect(page.getByText('Base resume added',{exact:true})).toBeVisible();
 await page.getByLabel('Add supporting evidence').setInputFiles({name:'portfolio-'+('x'.repeat(130))+'.md',mimeType:'text/plain',buffer:Buffer.from('PROJECT\nBuilt a fictional React booking interface.')});
 await expect(page.locator('.file-list')).toContainText('portfolio-');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
  await page.getByRole('button',{name:'Review my evidence',exact:true}).click();
  await expect(page.getByText('B. Tech in Information Technology at Example Institute.',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Clear temporary session',exact:true}).click();
  await expect(page.getByLabel('Upload base resume')).toBeEnabled();
 });

test('company clarification resumes to a checked result in the UI',async({page})=>{
 await page.goto('/');await page.getByText('Or paste resume text',{exact:true}).click();
 await page.getByLabel('Base resume text',{exact:true}).fill('SKILLS\nReact, TypeScript, Git.');
  await page.getByRole('button',{name:'Save resume text',exact:true}).click();
  if(await page.getByRole('button',{name:'Edit header',exact:true}).count())await page.getByRole('button',{name:'Edit header',exact:true}).click();
  await page.getByLabel('Full name',{exact:true}).fill('Mira Rao');
  await page.getByLabel('Role title',{exact:true}).fill('Junior Frontend Developer');
 await page.getByLabel('Company',{exact:true}).fill('CedarWorks Labs');
 await page.getByLabel('Job description Required',{exact:true}).fill('Required qualifications\n1. Experience building interfaces with React.\nPreferred qualification\n2. Experience using Docker.');
 await page.getByRole('button',{name:'Save job description',exact:true}).click();
  await page.getByRole('button',{name:'Review my evidence',exact:true}).click();
  await page.getByRole('button',{name:'Approve supported excerpts'}).click();
 await page.getByRole('button',{name:'Build my application'}).click();
 await expect(page.getByRole('heading',{name:'Company research needed'})).toBeVisible({timeout:20000});
 await page.getByLabel('Company knowledge',{exact:true}).fill('Fictional supplied knowledge: CedarWorks builds booking software and values accessible frontend forms.');
 await page.getByRole('button',{name:'Continue with this source'}).click();
 await expect(page.getByRole('heading',{name:'Your application package is ready.'})).toBeVisible({timeout:30000});
});

test('controlled needs-review UI hides verified downloads',async({page})=>{
 const run={id:'controlled-ui',status:'needs_review',graph_stage:'needs_review',mode:'mock',version:1,model_attempts:0,mock_calls:1,revision_count:1,research_calls:1,execution_elapsed_seconds:1,error:{code:'controlled_ui_fixture',message:'Controlled UI fixture: an unsupported claim remains.'}};
 await page.route('**/api/runs/controlled-ui',route=>route.fulfill({json:run}));
 await page.route('**/api/runs/controlled-ui/events?after=*',route=>route.fulfill({json:{events:[],next_cursor:0}}));
 await page.route('**/api/runs/controlled-ui/result',route=>route.fulfill({json:{status:'needs_review',mode:'mock',claims:[],matches:[],requirements:[],changes:[],research:[],artifacts:[],base_omissions:[],evaluations:{checks:{passed:false,pdf:{passed:true,page_count:1}},issues:[{id:'issue1',category:'semantic_support',explanation:'Controlled UI fixture: 40% time saving is unsupported.'}],semantic_review_mode:'offline_exact_excerpt'}}}));
 await page.goto('/?run=controlled-ui&view=results');
 await expect(page.getByRole('button',{name:'Verified downloads unavailable'})).toBeDisabled();
 await expect(page.getByRole('link',{name:'Download resume',exact:true})).toHaveCount(0);
 await expect(page.getByText('Controlled UI fixture: 40% time saving is unsupported.')).toBeVisible();
 await page.screenshot({path:`${output}/needs-review-controlled.png`,fullPage:true});
});


test('source submission waits for the session cookie',async({page})=>{
 let release:()=>void=()=>{};
 const ready=new Promise<void>(resolve=>{release=resolve});
 await page.route('**/api/sessions',async route=>{await ready;await route.continue()});
 await page.goto('/');
 await page.getByText('Or paste resume text',{exact:true}).click();
 await page.getByLabel('Base resume text',{exact:true}).fill('SKILLS\nReact, TypeScript, Git.');
 await expect(page.getByRole('button',{name:'Save resume text',exact:true})).toBeDisabled();
 await expect(page.getByLabel('Upload base resume')).toBeDisabled();
 release();
 await page.getByRole('button',{name:'Save resume text',exact:true}).click();
 await expect(page.getByText('Base resume added',{exact:true})).toBeVisible();
 await expect(page.locator('.alert.error')).toHaveCount(0);
});
