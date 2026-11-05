import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"bank"})'); pg.wait_for_timeout(300)
    print('menu', G('!!document.querySelector(\'[data-tab="bank"]\')'), G('bkAccounts(firm("namuna01")).map(a=>a.num+" "+a.cur)'))
    pg.click('#bkAi') if G('!!document.querySelector("#bkAi")') else None
    pg.set_input_files('#bkFiles',FIX+'bank.xlsx'); pg.wait_for_timeout(1500)
    print('imp', G('JSON.stringify(V.bkImp.items.map(i=>[i.status,i.msg,i.acc,i.r&&[i.r.from,i.r.to,i.r.open,i.r.close,i.r.ops.length],i.chk]))'))
    print('chk', G('document.querySelector(".bkimp").innerText.replace(/\\s+/g," ").slice(0,400)'))
    pg.click('[data-bk="impsave"]'); pg.wait_for_timeout(1200)
    print('ledger', G('[...document.querySelectorAll(".bktable tbody tr")].map(r=>r.innerText.replace(/\\s+/g," ").slice(0,160))'))
    # add SFs for contract 12
    G('''(async()=>{ const f=firm("namuna01"); const c=S.recs.find(x=>x.id==="namunact2"); for(const [id,no,date,s] of [["y1","1","2026-09-01",9000000],["y2","2","2026-10-01",9000000]]){ const d={id,type:"sf",firmId:"namuna01",no,date,contract:{no:"12",date:"2025-11-01"},sum:String(s),seller:{name:f.name,inn:f.inn},buyer:{name:c.cp.name,inn:c.cp.inn},items:[]}; ldNorm(d,f); await putItem("recs",d,"t"); } })()'''); pg.wait_for_timeout(600)
    print('alloc', G('JSON.stringify((()=>{ const A=sfAlloc(S.recs.find(x=>x.id==="namunact2")); return [A.paid,A.adv,A.res]; })())'))
    G('go({tab:"contracts",ctDir:"out",ctId:"namunact2"})'); pg.wait_for_timeout(300)
    print('pay', G('document.querySelector(".bkpay")?.innerText.replace(/\\s+/g," ").slice(0,200)'))
    G('go({ctId:null,ctDir:"sf"})'); pg.wait_for_timeout(300)
    print('sf', G('[...document.querySelectorAll("tr[data-ldo]")].map(r=>r.innerText.replace(/\\s+/g," ").slice(0,140))'))
    # act
    G('go({ctDir:"act"})'); pg.wait_for_timeout(300)
    pg.click('[data-act2="new|out"]'); pg.wait_for_timeout(300)
    k=G('actCps(firm("namuna01")).find(c=>c.inn==="306654321").key')
    pg.select_option('#ac_cp',k); pg.wait_for_timeout(300)
    pg.fill('#ac_from','2026-10-01'); G('document.querySelector("#ac_from").dispatchEvent(new Event("change",{bubbles:true}))'); pg.wait_for_timeout(300)
    print('act', G('document.querySelector(".actsheet").innerText.replace(/\\s+/g," ").slice(0,900)'))
    pg.screenshot(path=OUT+'a1.png',full_page=True)
    G('(()=>{ fxFetch=async(c,d)=>c==="USD"?12500:null; })()')
    pg.select_option('#ac_cur','USD'); pg.wait_for_timeout(300)
    print('miss', G('actCalc(firm("namuna01"),V.actEdit).miss'))
    pg.click('[data-act2="rates"]'); pg.wait_for_timeout(1000)
    print('usd', G('document.querySelector(".actsheet").innerText.replace(/\\s+/g," ").slice(-400)'))
    pg.click('[data-act2="save"]'); pg.wait_for_timeout(600)
    print('list', G('document.querySelector("#main table")?.innerText.replace(/\\s+/g," ").slice(0,300)'))
    # fc act
    print('fc cps', G('actCps(firm("namuna01")).filter(c=>c.list.some(x=>x.kind==="fc")).map(c=>c.name+":"+c.list.length)'))
    G('go({tab:"overview"})'); pg.wait_for_timeout(300)
    b.close(); ok()
