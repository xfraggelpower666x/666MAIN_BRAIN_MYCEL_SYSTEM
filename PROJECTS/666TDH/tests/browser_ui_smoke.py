import json,sys,tempfile,os,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from runtime.ui.view_model import build_view_model
from runtime.ui.render_html import render_html
binding=json.loads((root/'runtime/facets/SUBFACET_BINDINGS.json').read_text())
children={k:{'name':k+' native','version':v['version'],'system_id':v['system_id'],'current_path':v['current_path']} for k,v in binding['child_profiles'].items()}
registry={'system_id':'666TRACKHUB-001','children':children}
routes={'root':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL','HOST RECOVERY','UPDATE'],'child':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL'],
        'daemon':['STATUS','NEXT','MENU','CONTINUE','BACK','HELP','STOP','WEITER','NEW CHAT']}
with tempfile.TemporaryDirectory() as d:
  d=Path(d)
  results=[]
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=(os.environ.get('TDH_CHROMIUM') or shutil.which('chromium') or None),args=['--no-sandbox'])
    for token in (None,*children):
      profile=binding['child_profiles'][token] if token else None
      data=build_view_model(registry=registry,routes=routes,token=token,release='v1.15.0',profile=profile,continuity=None,pointer_state='VERIFIED_R2',files_verified=281)
      path=d/((token or 'HUB')+'.html');path.write_text(render_html(data),encoding='utf-8')
      page=browser.new_page(viewport={'width':390,'height':844})
      errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
      requests=[];page.on('request',lambda r:requests.append(r.url) if r.url.startswith('http') else None)
      page.set_content(path.read_text(encoding="utf-8"),wait_until="load")
      assert page.locator('#view-title').inner_text()==data['sections'][0]['title']
      assert page.locator('#facts li').count()>0
      for i,section in enumerate(data['sections']):
        tab=page.get_by_role('tab',name=section['title'],exact=True)
        tab.click()
        assert page.locator('#view-title').inner_text()==section['title']
        assert page.locator('#view-source').inner_text().endswith(section['source'])
        assert tab.get_attribute('aria-selected')=='true'
      if token is None:
        assert page.locator('#daemon-menu button').count()==9
        page.locator('#daemon-menu button').first.click()
        assert page.locator('#copy-buffer').input_value()=='666TDH DAEMON STATUS'
      else:
        assert page.locator('#daemon-menu button').count()==0
      first=data['menu'][0]
      page.locator('#menu button').first.click()
      assert page.locator('#copy-buffer').input_value()==first['command']
      assert 'Kopiert:' in page.locator('#feedback').inner_text() or 'manuell kopieren' in page.locator('#feedback').inner_text()
      page.get_by_role('button',name='Begleiter lokal ausblenden').click()
      assert page.locator('#daemon').is_hidden()
      page.get_by_role('button',name='Begleiter lokal einblenden').click()
      assert page.locator('#daemon').is_visible()
      assert not errors,(token,errors)
      assert not requests,(token,requests)
      results.append({'target':token or 'HUB','tabs':len(data['sections']),'menu':len(data['menu']),'http_requests':len(requests),'errors':len(errors),'small_viewport':390})
      page.close()
    browser.close()
  print(json.dumps({'status':'PASS_LOCAL_BROWSER','browser':'Chromium','results':results},ensure_ascii=False,indent=2))
