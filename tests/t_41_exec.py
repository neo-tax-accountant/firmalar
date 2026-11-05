import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"contracts",ctDir:"out"})'); pg.wait_for_timeout(300)
    G('''(async()=>{ const f=firm("namuna01"); const c=S.recs.find(x=>x.id==="namunact2"); await attPut("recs",c.id,o=>{ o.items=[{name:"Бухгалтерия хизмати (ойлик)",unit:"ой",qty:"12",price:"3000000",sum:"36000000"}]; },"t");
      const mk=async(id,no,date,qty,kind)=>{ const d={id,type:kind,firmId:"namuna01",no,date,contract:{no:"12",date:"2025-11-01"},sum:String(qty*3000000),items:[{name:"Бухгалтерия хизмати, ойлик",unit:"ой",qty:String(qty),price:"3000000",sum:String(qty*3000000)}]}; if(kind==="sf"){ d.seller={name:f.name,inn:f.inn}; d.buyer={name:c.cp.name,inn:c.cp.inn}; } else { d.shipper={name:f.name,inn:f.inn}; d.consignee={name:c.cp.name,inn:c.cp.inn}; } ldNorm(d,f); await putItem("recs",d,"t"); };
      await mk("x1","1","2025-12-01",5,"sf"); await mk("x2","2","2026-05-01",4,"sf"); await mk("t1","T1","2025-12-02",5,"ttn"); })()'''); pg.wait_for_timeout(600); G('render()'); pg.wait_for_timeout(300)
    print('cell', G('[...document.querySelectorAll("#ctTable tbody tr")].map(r=>r.innerText.replace(/\\s+/g," ").slice(-90))'))
    print('chips', G('[...document.querySelectorAll("[data-ctf=ctEx]")].map(x=>x.textContent).join("|")'))
    G('go({ctId:"namunact2"})'); pg.wait_for_timeout(300)
    print('card', G('document.querySelector(".excard").innerText.replace(/\\s+/g," ").slice(0,500)'))
    pg.screenshot(path=OUT+'e1.png',full_page=True)
    G('''(async()=>{ const f=firm("namuna01"); const c=S.recs.find(x=>x.id==="namunact2"); const d={id:"x3",type:"sf",firmId:"namuna01",no:"3",date:"2026-10-01",contract:{no:"12",date:"2025-11-01"},sum:"9000000",seller:{name:f.name,inn:f.inn},buyer:{name:c.cp.name,inn:c.cp.inn},items:[{name:"Бухгалтерия хизмати ойлик",unit:"ой",qty:"3",price:"3000000",sum:"9000000"}]}; ldNorm(d,f); await putItem("recs",d,"t"); })()'''); pg.wait_for_timeout(500); G('render()'); pg.wait_for_timeout(300)
    print('full', G('JSON.stringify(exState(S.recs.find(x=>x.id==="namunact2")))'), G('document.querySelector(".excard .ndok")?.textContent.slice(0,120)'))
    print('alerts', G('ctAlerts(firm("namuna01")).map(a=>a.t).filter(t=>/бажарилди|ошди/.test(t))'))
    pg.click('.excard [data-act="ctToggle"]'); pg.wait_for_timeout(500)
    print('closed', G('S.recs.find(x=>x.id==="namunact2").status'), G('exState(S.recs.find(x=>x.id==="namunact2")).t'))
    b.close(); ok()
