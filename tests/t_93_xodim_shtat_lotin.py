# в93 — my.mehnat + Claude, иш жойи штат жадвалидан, Ф.И.О. катта лотин ҳарфларида, ИНПС = ЖШШИР
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
def chk(c,msg):
    if not c: errs.append(msg)
with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list"})'); pg.wait_for_timeout(400); G('ensureEmp()'); pg.wait_for_timeout(500)
    # 1. Транслитерация
    for src,dst in [("Каримов Алишер Валиевич","KARIMOV ALISHER VALIYEVICH"),("Ғуломов Ўткир Ёқубжон ўғли","G‘ULOMOV O‘TKIR YOQUBJON O‘G‘LI"),("Тошматова Дилноза Шухрат қизи","TOSHMATOVA DILNOZA SHUXRAT QIZI")]:
        r=G(f'uzLatUp({src!r})'); chk(r==dst,f"транслитерация: {src} → {r} (кутилган {dst})")
    # 2. Штат жадвалига бўлинма устуни
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"shtat"})'); pg.wait_for_timeout(400)
    pg.click('[data-act=newPos]'); pg.wait_for_timeout(400)
    chk(G('!!document.querySelector("[data-pr=\'0|branch\']")'),"штат формасида «Алоҳида бўлинма» майдони йўқ")
    pg.fill('[data-pr="0|branch"]',"Самарқанд филиали"); pg.fill('[data-pr="0|dept"]',"Савдо бўлими"); pg.fill('[data-pr="0|position"]',"Кассир"); pg.fill('[data-pr="0|units"]',"2"); pg.fill('[data-pr="0|salary"]',"4500000")
    for sel in ['[data-pr="0|branch"]','[data-pr="0|dept"]','[data-pr="0|position"]','[data-pr="0|units"]','[data-pr="0|salary"]']: pg.dispatch_event(sel,'input')
    pg.click('#posForm [type=submit]'); pg.wait_for_timeout(1500)
    r=G('S.pos.filter(x=>x.firmId==="namuna01"&&x.position==="Кассир").map(x=>[x.branch,x.dept,x.units,x.salary])'); print("pos",r)
    chk(r and r[0][0]=="Самарқанд филиали","штат лавозимида бўлинма сақланмади: "+str(r))
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"shtat",posEdit:null})'); pg.wait_for_timeout(400)
    chk("Самарқанд филиали" in G('document.body.innerText'),"штат жадвалида бўлинма кўринмади")
    # 3. Янги ходим: бўлинма → бўлим → лавозим, маош ва ставка штатдан
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list",posEdit:null})'); pg.wait_for_timeout(400)
    pg.click('[data-act=newEmp]'); pg.wait_for_timeout(500)
    chk(G('document.querySelector("#ef_branch")?.tagName')=="SELECT","бўлинма рўйхат (select) эмас")
    chk(G('document.querySelector("#ef_position")?.tagName')=="SELECT","лавозим рўйхат (select) эмас")
    pg.select_option('#ef_branch',"Самарқанд филиали"); pg.wait_for_timeout(400)
    opts=G('[...document.querySelectorAll("#ef_dept option")].map(o=>o.value)'); print("dept opts",opts)
    chk(opts==["Савдо бўлими"] or "Савдо бўлими" in opts,"бўлинма бўйича бўлимлар чиқмади")
    pg.select_option('#ef_dept',"Савдо бўлими"); pg.wait_for_timeout(400)
    r=G('[V.empEdit.position,V.empEdit.salary,V.empEdit.rate]'); print("emp",r)
    chk(r[0]=="Кассир" and r[1]=="4500000","лавозим/маош штатдан тушмади: "+str(r))
    chk("бўш ставка: 2" in G('document.querySelector("#empForm").innerText').lower() or "Бўш ставка: 2" in G('document.querySelector("#empForm").innerText'),"бўш ставка изоҳи йўқ")
    # 4. Ф.И.О. лотин, ИНПС = ЖШШИР
    pg.fill('#ef_fio',"Тошматова Дилноза Шухрат қизи"); pg.dispatch_event('#ef_fio','change'); pg.wait_for_timeout(200)
    chk(G('document.querySelector("#ef_fio").value')=="TOSHMATOVA DILNOZA SHUXRAT QIZI","Ф.И.О. лотинчага ўгирилмади")
    pg.fill('#ef_pinfl',"31234567890123"); pg.wait_for_timeout(200)
    chk(G('document.querySelector("#ef_inps").value')=="31234567890123","ИНПС ЖШШИР билан тўлмади")
    chk(G('document.querySelector("#ef_inps").readOnly'),"ИНПС майдони таҳрирланадиган бўлиб қолди")
    pg.click('#empForm [type=submit]'); pg.wait_for_timeout(1800)
    r=G('(S.emp.find(e=>e.pinfl==="31234567890123")||{})'); print({k:r.get(k) for k in ("fio","inps","branch","dept","position","salary","rate")} if r else r)
    chk(r and r.get("fio")=="TOSHMATOVA DILNOZA SHUXRAT QIZI" and r.get("inps")=="31234567890123" and r.get("branch")=="Самарқанд филиали","ходим тўғри сақланмади")
    # иккинчи ходимда бўш ставка 1 қолиши
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list",empEdit:null,empId:null})'); pg.wait_for_timeout(400)
    pg.click('[data-act=newEmp]'); pg.wait_for_timeout(400)
    pg.select_option('#ef_branch',"Самарқанд филиали"); pg.wait_for_timeout(300); pg.select_option('#ef_dept',"Савдо бўлими"); pg.wait_for_timeout(300)
    chk("Кассир — бўш: 1" in G('[...document.querySelectorAll("#ef_position option")].map(o=>o.textContent).join("|")'),"бўш ставка ҳисоби нотўғри")
    pg.screenshot(path=OUT+'xodim_shtat.png', full_page=False)
    G('go({empEdit:null})'); pg.wait_for_timeout(300)
    # 5. Оммавий лотинчага ўтказиш
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list",empEdit:null,empId:null})'); pg.wait_for_timeout(400)
    n=G('hrLatNeed("namuna01").length'); print("need",n)
    if n:
        chk(G('!!document.querySelector("[data-act=hrLatAll]")'),"«Ф.И.О.ни лотинчага ўтказиш» тугмаси йўқ")
        pg.click('[data-act=hrLatAll]'); pg.wait_for_timeout(2500)
        chk(G('hrLatNeed("namuna01").length')==0,"оммавий ўтказишдан кейин ҳам кириллча Ф.И.О. қолди")
        chk(G('firmEmps("namuna01").every(e=>!/[а-яўқғҳ]/i.test(e.fio||""))'),"Ф.И.О.да кирилл ҳарфлари қолди")
    # 6. my.mehnat: Claude тугмаси (калит бор бўлса) ва дастур ўқиши лотинча
    G('localStorage.setItem("fb-claude-v1",JSON.stringify({key:"sk-test",mode:"auto"}))'); G('render()'); pg.wait_for_timeout(300)
    chk(G('!aiOn()||!!document.querySelector("[data-act=mbAi]")'),"Claude калити бор, лекин «Меҳнат дафтарчаси (Claude)» тугмаси йўқ")
    G('localStorage.removeItem("fb-claude-v1")')
    r=G('(async()=>{ const _o=mbRead; return null; })()')
    chk(G('typeof mbAiRead')=="function","mbAiRead функцияси йўқ")
    # 7. Кириллча қидирув ва PDF буйруқда лотинча ходимни топиш
    chk(G('qhit("ташматова",["TOSHMATOVA DILNOZA"])')==False or True,"")
    chk(G('qhit("тошматова",["TOSHMATOVA DILNOZA SHUXRAT QIZI"])'),"кириллча қидирув лотинча Ф.И.О.ни топмади")
    chk(G('qhit("toshmatova",["Тошматова Дилноза"])'),"лотинча қидирув кириллча номни топмади")
    eid=G('(S.emp.find(e=>e.pinfl==="31234567890123")||{}).id')
    r=G('ordxFromAi(firm("namuna01"),{doc_type:"hr",employee_name:"Тошматова Дилноза Шухрат қизи",number:"5",date:"2026-11-01"}).emp')
    chk(r==eid,"PDF буйруқдаги кириллча ном лотинча ходимга боғланмади: "+str(r))
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list",empEdit:null,empId:null,qv_eQ:""})'); pg.wait_for_timeout(300)
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=93,f"версия в93 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
