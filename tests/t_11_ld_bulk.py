import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
T=FIX
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    G('localStorage.setItem(AI_LK,JSON.stringify({key:"sk-ant-test",mode:"manual"}))')
    G('''(()=>{ window.__n=0; aiDoc=async(file,f,spec)=>{ __n++; await new Promise(r=>setTimeout(r,150)); return {x:{number:"X"+__n,date:"2026-09-0"+(__n%9+1),contract_number:"15/2026",seller:{name:"ООО «Намуна Савдо»",inn:"300000001"},buyer:{name:"ООО «Бета Трейд»",inn:"305555555"},total:1000*__n},usd:0.01}; }; })()''')
    G('go({view:"firm",firmId:"namuna01",tab:"contracts",ctDir:"sf"})'); pg.wait_for_timeout(300)
    pg.set_input_files('#ldFiles',[FIX+'sf2.pdf',FIX+'sf2.pdf',FIX+'ttn1.pdf']); pg.wait_for_timeout(2500)
    print('staged', G('V.ldImp.items.map(i=>i.status)'), 'calls', G('__n'))
    pg.click('[data-lda="impsave|sf"]'); pg.wait_for_timeout(2500)
    print('saved', G('ldList("namuna01","sf").map(d=>[d.no,ldWeak(d)])'))
    pg.click('[data-lda="selweak|sf"]'); pg.wait_for_timeout(300); print('sel', G('V.ldSel'))
    pg.click('[data-lda="ai|sf"]'); pg.wait_for_timeout(2500)
    print('after', G('ldList("namuna01","sf").map(d=>[d.no,d.seller.inn,d.buyer.inn,num(d.sum),ldWeak(d),!!ldMatch("namuna01",d)])'), G('document.getElementById("toast").textContent'))
    # checkbox select-all
    pg.click('[data-lds="sf|*"]'); pg.wait_for_timeout(300); print('selall', len(G('V.ldSel.ids')))
    pg.screenshot(path=OUT+'b8.png',full_page=True)
    b.close(); ok()
