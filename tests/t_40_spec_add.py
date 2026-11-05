import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"contracts",ctDir:"out"})'); pg.wait_for_timeout(400)
    print('cts', G('firmContracts("namuna01").map(c=>[c.id,c.dir,c.number,c.cp?.name,c.cp?.inn,c.amount,c.endDate,c.exch?1:0])'))
    print('heads', G('[...document.querySelectorAll("#ctTable th")].map(x=>x.textContent).join("|")'))
    print('tabs', G('[...document.querySelectorAll(".cttab b")].map(x=>x.textContent).join("|")'))
    c=G('firmContracts("namuna01").find(c=>c.dir==="out"&&!c.exch)')
    G('''(async()=>{ const f=firm("namuna01"); const c=firmContracts("namuna01").find(c=>c.dir==="out"&&!c.exch);
      await putItem("recs",{id:"sfo1",type:"sf",firmId:"namuna01",no:"101",date:"2026-05-01",seller:{name:f.name,inn:f.inn},buyer:{name:c.cp.name,inn:c.cp.inn},contract:{no:c.number,date:c.date},sum:"5000000",items:[]},"t");
      await putItem("recs",{id:"sfo2",type:"sf",firmId:"namuna01",no:"101",date:"2026-05-01",seller:{name:f.name,inn:f.inn},buyer:{name:c.cp.name,inn:c.cp.inn},contract:{no:c.number,date:c.date},sum:"5000000",items:[]},"t");
      await putItem("recs",{id:"sfi1",type:"sf",firmId:"namuna01",no:"77",date:"2026-05-03",seller:{name:"«Етказувчи» МЧЖ",inn:"309999991"},buyer:{name:f.name,inn:f.inn},contract:{no:"9",date:"2026-01-01"},sum:"1200000",items:[]},"t");
      ["sfo1","sfo2","sfi1"].forEach(id=>{ const r=S.recs.find(x=>x.id===id); ldNorm(r,f); });
      const d={...JSON.parse(JSON.stringify(c)),id:"ctdup1",createdAt:Date.now()+5}; delete d.specs; await putItem("recs",d,"t"); })()'''); pg.wait_for_timeout(500)
    G('render()'); pg.wait_for_timeout(300)
    print('dupbtn', G('document.querySelector(".dupbtn")?.textContent'), G('document.querySelector(".dupwarn")?.textContent.slice(0,90)'))
    print('row sf cell', G('[...document.querySelectorAll("#ctTable tbody tr")].map(r=>r.innerText.replace(/\\s+/g," ").slice(0,200)).slice(0,3)'))
    pg.click('[data-ctf="ctSf"][data-v="has"]'); pg.wait_for_timeout(300)
    print('filter sf has', G('document.querySelectorAll("#ctTable tbody tr[data-ct]").length'))
    pg.click('[data-ctf="ctSf"][data-v="no"]'); pg.wait_for_timeout(300)
    print('filter sf no', G('document.querySelectorAll("#ctTable tbody tr[data-ct]").length'))
    pg.click('[data-ctclr68]'); pg.wait_for_timeout(200)
    pg.screenshot(path=OUT+'c1.png',full_page=False)
    pg.click('[data-ctdir="sfin"]'); pg.wait_for_timeout(300)
    print('sfin rows', G('[...document.querySelectorAll("tr[data-ldo]")].map(r=>r.dataset.ldo)'), G('document.querySelector("h1,.lstat .k")?.textContent'))
    pg.click('[data-ctdir="sf"]'); pg.wait_for_timeout(300)
    print('sf rows', G('[...document.querySelectorAll("tr[data-ldo]")].map(r=>r.dataset.ldo)'), G('document.querySelector(".dupwarn")?.textContent.slice(0,80)'))
    pg.click('[data-dup^="selld"]'); pg.wait_for_timeout(300); print('ldsel', G('JSON.stringify(V.ldSel)'))
    # addendum
    G('go({ctDir:"out",ctId:"%s"})'%c['id']); pg.wait_for_timeout(300)
    pg.click('[data-sa="new|add"]'); pg.wait_for_timeout(300)
    pg.fill('#sa_no','1'); pg.select_option('#sa_amountMode','set'); pg.wait_for_timeout(200); pg.fill('#sa_amount','999000'); pg.fill('#sa_newEnd','2027-12-31')
    pg.select_option('#sa_itemsMode','replace'); pg.wait_for_timeout(200)
    if G('!!document.querySelector(\'[data-sa="copyitems"]\')'): pg.click('[data-sa="copyitems"]'); pg.wait_for_timeout(200)
    pg.click('[data-sa="addrow"]'); pg.wait_for_timeout(200)
    n=G('document.querySelectorAll("[data-sai$=\'|name\']").length')
    pg.fill(f'[data-sai="{n-1}|name"]','Янги товар'); pg.fill(f'[data-sai="{n-1}|qty"]','10'); pg.fill(f'[data-sai="{n-1}|price"]','500')
    print('prev', G('document.querySelector("#saPrev").textContent'))
    pg.click('[data-sa="save"]'); pg.wait_for_timeout(600)
    print('eff', G('JSON.stringify(ctEff(S.recs.find(x=>x.id==="%s")))'%c['id'])[:300])
    print('info', G('[...document.querySelectorAll(".reqs")][0].innerText.replace(/\\s+/g," ").slice(0,400)'))
    pg.screenshot(path=OUT+'c2.png',full_page=True)
    # bulk with mocked AI
    G('''(()=>{ localStorage.setItem(AI_LK,JSON.stringify({key:"sk-t"})); const _a=aiDoc; aiDoc=async(fl,f,spec,n)=>{ if(spec.tool!=="save_contract_document") return _a(fl,f,spec,n); return {x:{doc_type:n.includes("spec")?"specification":"addendum",number:n.includes("spec")?"S-2":"2",date:"2026-06-01",summary:"Муддат узайтирилди",amount_mode:"add",amount:1000,new_end_date:"2028-01-01",items_mode:"none",items:n.includes("spec")?[{name:"Плитка",unit:"м2",qty:5,price:100,sum:500}]:[],spec_total:500,adds_to_contract_amount:true},usd:0.01}; }; })()''')
    pg.set_input_files('#saFiles',[FIX+'sample.pdf',FIX+'spec.pdf']); pg.wait_for_timeout(2500)
    print('after bulk', G('JSON.stringify(ctEff(S.recs.find(x=>x.id==="%s")))'%c['id'])[:200], G('S.recs.find(x=>x.id==="%s").addenda.length+"/"+(S.recs.find(x=>x.id==="%s").specs||[]).length'%(c['id'],c['id'])))
    # dup panel
    pg.click('.dupbtn'); pg.wait_for_timeout(300)
    print('panel', G('document.querySelector(".duppanel").innerText.replace(/\\s+/g," ").slice(0,500)'))
    pg.screenshot(path=OUT+'c3.png')
    pg.click('[data-dup="del"]'); pg.wait_for_timeout(1500)
    print('after del', G('[!!S.recs.find(x=>x.id==="ctdup1"),!!S.recs.find(x=>x.id==="sfo2"),!!S.recs.find(x=>x.id==="sfo1"),dupInfo("namuna01").extra.size]'))
    b.close(); ok()
