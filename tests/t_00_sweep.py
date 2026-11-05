import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    tabs=G('[...document.querySelectorAll("[data-tab]")].map(x=>x.dataset.tab)')
    G('go({view:"firm",firmId:"namuna01"})'); pg.wait_for_timeout(400)
    tabs=G('[...new Set([...document.querySelectorAll("[data-tab]")].map(x=>x.dataset.tab))]'); print('tabs',len(tabs))
    for t in tabs:
        G(f'go({{view:"firm",firmId:"namuna01",tab:"{t}"}})'); pg.wait_for_timeout(250)
        if not G('document.getElementById("main").textContent.length>50'): print('EMPTY',t)
    for d in ["in","out","exch","poa","sf","ttn"]:
        G(f'go({{tab:"contracts",ctDir:"{d}",ctId:null}})'); pg.wait_for_timeout(250)
    cid=G('firmContracts("namuna01")[0].id'); G(f'go({{ctDir:"in",ctId:"{cid}"}})'); pg.wait_for_timeout(300)
    G('go({ctId:null,ctDir:"in"})'); pg.wait_for_timeout(200)
    pg.click('th.selc input'); pg.wait_for_timeout(300); print('selbar ai btn', G('!!document.querySelector("[data-cxa^=\'ai|\']")'))
    pg.click('[data-act=selPrint]'); pg.wait_for_timeout(400); print('pp', G('PP&&PP.docs.map(d=>d.groups.map(g=>g.g).join(","))')); G('document.getElementById("ppModal")?.remove()')
    for v in ["cps","gtd","ctl","ai"]:
        G(f'go({{view:"{v}",firmId:null}})'); pg.wait_for_timeout(300)
    G('go({view:"firm",firmId:"namuna01",tab:"import",impSub:"fc",fcId:"namunafc1",fcSub:"info"})'); pg.wait_for_timeout(400)
    for s in ["spec","act","add","pay"]:
        G(f'go({{fcSub:"{s}"}})'); pg.wait_for_timeout(200)
    G('go({impSub:"fx",fcId:null})'); pg.wait_for_timeout(200); G('go({impSub:"gtd"})'); pg.wait_for_timeout(200)
    G('go({view:"firm",firmId:"namuna01",tab:"contracts",ctDir:"in",ctId:null}); V.ctEdit=ctNewDraft("namuna01"); render()'); pg.wait_for_timeout(300)
    G('go({ctEdit:null,ctDir:"exch"}); V.ctEdit=ctNewDraft("namuna01"); render()'); pg.wait_for_timeout(300); print('exch form', G('!!document.getElementById("ct_ex_goods")'), G('V.ctEdit.exch'))
    b.close(); ok()
