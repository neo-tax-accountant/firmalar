import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"office",letDir:"out"})'); pg.wait_for_timeout(300)
    pg.click('[data-mm="open"]'); pg.wait_for_timeout(300)
    pg.click('[data-mm="cp"]'); pg.wait_for_timeout(200); pg.click('[data-mm="cpall"]'); pg.wait_for_timeout(200); pg.click('[data-mm="cpadd"]'); pg.wait_for_timeout(300)
    pg.set_input_files('#mmDebt',FIX+'osv.xlsx'); pg.wait_for_timeout(1500)
    print('rows', G('V.mm.rows.map(r=>[r.corr,r.sum,r.ctNo,r.ctDate,!!r.debtSrc])'))
    print('info', G('JSON.stringify(V.mm.debtInfo)'))
    print('h2', G('document.querySelector(".lform h2").textContent'))
    pg.screenshot(path=OUT+'m2.png')
    pg.click('[data-mm="nodebt"]'); pg.wait_for_timeout(300)
    print('after', G('V.mm.rows.map(r=>r.corr+":"+r.sum)'))
    print('same', G('[mmSame({corr:"«Альфа Савдо» МЧЖ"},{corr:"Альфа Савдо ООО"}),mmSame({corr:"Альфа Трейд"},{corr:"Альфа Савдо"}),mmSame({corr:"Бета"},{corr:"Бета Савдо"})]'))
    b.close(); ok()
