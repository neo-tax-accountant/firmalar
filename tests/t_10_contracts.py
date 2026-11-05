import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
T=FIX
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    print('ver', G('document.getElementById("syncLine").textContent'))
    G('localStorage.setItem(AI_LK,JSON.stringify({key:"sk-ant-test",mode:"weak"}))')
    G('''(()=>{ window.__calls=[]; const _call=aiCall; aiDoc=async(file,f,spec,fn)=>{ __calls.push(spec.tool+":"+fn); await new Promise(r=>setTimeout(r,300));
      if(spec.tool==="save_invoice") return {x:{number:"102",date:"2026-09-12",contract_number:"15/2026",contract_date:"2026-02-01",seller:{name:"ООО «Намуна Савдо»",inn:"300000001"},buyer:{name:"ООО «Бета Трейд»",inn:"305555555"},total:5000000,vat:535714.29,items:[{name:"Ун",unit:"кг",qty:1000,price:5000,sum:5000000}]},usd:0.01};
      if(spec.tool==="save_exchange_contract") return {x:{exchange:"УзРТСБ",deal_no:"2600123",lot_no:"77",date:"2026-09-01",end_date:"2026-10-01",seller:{name:"ООО «Цемент Завод»",inn:"301111111",bank:"Агробанк",account:"20208000000000000001"},buyer:{name:"Намуна",inn:"300000001"},goods:"Цемент М400",qty:100,unit:"тонна",price:900000,amount:90000000,currency:"UZS",delivery_term:"10 кун",payment_term:"100% олдиндан"},usd:0.02};
      if(spec.tool==="save_power_of_attorney") return {x:{number:"45",holder:{name:"Алиев Б.К.",position:"экспедитор"}},usd:0.01};
      return {x:{},usd:0.01}; }; })()''')
    # contracts: upload contract (out)
    G('go({view:"firm",firmId:"namuna01",tab:"contracts",ctDir:"out"})'); pg.wait_for_timeout(400)
    print('tabs', G('[...document.querySelectorAll(".cttab b")].map(x=>x.textContent)'))
    pg.set_input_files('#ctFiles',[FIX+'ct1.pdf',FIX+'sf1.pdf',FIX+'ttn1.pdf']); pg.wait_for_timeout(6000)
    print('ctImport', G('V.ctImport&&V.ctImport.items.map(i=>[i.fname,i.status,i.d&&i.d.number])'), 'sf/ttn', G('[ldList("namuna01","sf").length,ldList("namuna01","ttn").length]'))
    pg.screenshot(path=OUT+'b1.png')
    pg.click('[data-cia="weak"]'); pg.wait_for_timeout(300)
    pg.click('[data-cia="ai"]'); pg.wait_for_timeout(1500)
    print('panel', G('document.getElementById("tpPanel")?.textContent'))
    pg.wait_for_timeout(1500)
    if G('!!V.ctImport'): pg.click('[data-act=ctImpSave]'); pg.wait_for_timeout(2500)
    cid=G('(firmContracts("namuna01").find(c=>c.number==="15/2026")||{}).id'); print('contract', cid)
    G('go({ctImport:null,ctDir:"out"})'); pg.wait_for_timeout(400)
    print('badges', G('[...document.querySelectorAll("#ctTable .ldbadges")].map(x=>x.textContent)'))
    # sf tab bulk import
    G('go({ctDir:"sf"})'); pg.wait_for_timeout(300)
    pg.set_input_files('#ldFiles',[FIX+'sf2.pdf']); pg.wait_for_timeout(3000)
    print('ldImp', G('V.ldImp&&V.ldImp.items.map(i=>[i.fname,i.status,i.d.no,i.d.cp.name,i.d.dir])'))
    pg.screenshot(path=OUT+'b2.png',full_page=True)
    pg.click('[data-lda="impsave|sf"]'); pg.wait_for_timeout(2000)
    print('sf saved', G('ldList("namuna01","sf").map(d=>[d.no,d.dir,d.cp.inn,!!ldMatch("namuna01",d)])'))
    pg.screenshot(path=OUT+'b3.png',full_page=True)
    # poa: upload weak, then bulk ai on saved
    G('go({ctDir:"poa"})'); pg.wait_for_timeout(300)
    pg.set_input_files('#ldFiles',[FIX+'poa1.pdf']); pg.wait_for_timeout(2500)
    pg.click('[data-lda="impsave|poa"]'); pg.wait_for_timeout(2000)
    print('poa', G('ldList("namuna01","poa").map(d=>[d.no,d.holder&&d.holder.name,ldWeak(d)])'))
    if G('!!document.querySelector(\'[data-lda="selweak|poa"]\')'):
        pg.click('[data-lda="selweak|poa"]'); pg.wait_for_timeout(300); pg.click('[data-lda="ai|poa"]'); pg.wait_for_timeout(2500)
    print('poa after', G('ldList("namuna01","poa").map(d=>[d.no,d.holder&&d.holder.name,d.holder&&d.holder.position])'))
    # exch
    G('go({ctDir:"exch"})'); pg.wait_for_timeout(300)
    pg.set_input_files('#ctFiles',[FIX+'ex1.pdf']); pg.wait_for_timeout(3500)
    print('exImp', G('V.ctImport&&V.ctImport.items.map(i=>[i.status,i.d.exch,i.d.number,i.d.dir,i.d.cp&&i.d.cp.name,i.d.ex&&i.d.ex.goods])'))
    pg.click('[data-act=ctImpSave]'); pg.wait_for_timeout(2000)
    G('go({ctImport:null})'); pg.wait_for_timeout(400)
    print('ex rows', G('[...document.querySelectorAll("#ctTable tbody tr")].map(r=>r.textContent.replace(/\\s+/g," ").slice(0,160))'))
    pg.screenshot(path=OUT+'b4.png',full_page=True)
    print('in/out counts excl exch', G('[...document.querySelectorAll(".cttab i")].map(x=>x.textContent)'))
    # detail
    G(f'go({{ctDir:"out",ctId:"{cid}"}})'); pg.wait_for_timeout(500); pg.screenshot(path=OUT+'b5.png',full_page=True)
    print('detail card', G('document.body.textContent.includes("Шартномага боғланган ҳужжатлар")'))
    print('calls', G('__calls'))
    b.close(); ok()
