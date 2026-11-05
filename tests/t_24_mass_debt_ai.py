import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"office",letDir:"out"})'); pg.wait_for_timeout(300)
    pg.click('[data-mm="open"]'); pg.wait_for_timeout(300)
    pg.set_input_files('#mmDebt',FIX+'debtors.xlsx'); pg.wait_for_timeout(1200)
    print('list', G('V.mm.rows.map(r=>[r.corr,r.corrInn,r.sum])'))
    pg.set_input_files('#mmDebt',FIX+'sample.pdf'); pg.wait_for_timeout(800)
    print('noai toast', G('document.querySelector(".toast")?.textContent'))
    G('localStorage.setItem(AI_LK,JSON.stringify({key:"sk-test"})); (()=>{ aiDocAny=async()=>({x:{period_end:"2026-09-30",items:[{name:"Альфа Савдо ООО",debt:2500000},{name:"Омега МЧЖ",inn:"309999999",debt:700000,contract_no:"5",contract_date:"2026-02-01"},{name:"Аванс МЧЖ",debt:-100}]},usd:0}); })()')
    pg.set_input_files('#mmDebt',FIX+'sample.pdf'); pg.wait_for_timeout(1200)
    print('ai', G('V.mm.rows.map(r=>[r.corr,r.sum,r.ctNo])'), G('JSON.stringify(V.mm.debtInfo)'))
    b.close(); ok()
