# в90 — «Кадрлар низоми» (Меҳнат кодекси асосида, ҳисоб сиёсати андозасида)
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
def chk(c,msg):
    if not c: errs.append(msg)
with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    # 1. Кадрлар бўлимида янги бўлимча
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list",empId:null,polId:null,polEdit:null})'); pg.wait_for_timeout(600)
    chk(G('!!document.querySelector("[data-hrsub=nizom]")'),"«Кадрлар низоми» бўлимчаси йўқ")
    pg.click('[data-hrsub=nizom]'); pg.wait_for_timeout(500)
    chk("Кадрлар низоми ҳали тузилмаган" in G('document.body.innerText'),"бўш ҳолат матни чиқмади")
    # 2. Янги низом формаси
    pg.click('[data-act=hrPolNew]'); pg.wait_for_timeout(600)
    chk(G('V.polEdit&&V.polEdit.kind')=="hr","низом черновиги очилмади")
    chk(G('!!document.querySelector("[data-pv=micro]")&&!!document.querySelector("[data-pv=probation]")&&!!document.querySelector("[data-pv=vacDays]")'),"параметр майдонлари йўқ")
    t=G('document.querySelector("#polSheet").innerText'); print(t[:400])
    for w in ("КАДРЛАР НИЗОМИ","МК 217-моддаси","МК 129–130-моддалари","МК 312-моддаси","МК 170-моддаси","ўн тўрт календарь кун","МК 173-моддаси","Ишга кираётган шахсни таништириш варақаси"):
        chk(w in t,f"низом матнида йўқ: {w}")
    chk("Иш вақтидан ташқари иш раҳбар буйруғи" not in t,"белгиланмаган банд (иш вақтидан ташқари) матнга тушди")
    chk("undefined" not in t and "[киритинг]" not in t,"матнда undefined ёки бўш майдон")
    # 3. Белгилаш → матн дарҳол ўзгаради
    pg.check('[data-pv=micro]'); pg.check('[data-pv=overtime]'); pg.check('[data-pv=union]'); pg.wait_for_timeout(500)
    t=G('document.querySelector("#polSheet").innerText')
    chk("етти календарь кун" in t and "МК 506-моддаси" in t,"микрофирма белгиланганда огоҳлантириш 7 кунга ўзгармади")
    chk("сурункасига икки кунда тўрт соатдан" in t,"иш вақтидан ташқари иш банди қўшилмади")
    chk("касаба уюшмаси қўмитаси билан келишилган ҳолда раҳбар" in t,"касаба уюшмаси шарти таътил графигига тушмади")
    pg.select_option('[data-pv=probation]',"белгиланмайди"); pg.wait_for_timeout(400)
    chk("дастлабки синовсиз ишга қабул" in G('document.querySelector("#polSheet").innerText'),"синов «белгиланмайди» матнга тушмади")
    # 4. Сақлаш → тасдиқлаш буйруғи
    pg.click('#polForm [type=submit]'); pg.wait_for_timeout(2500)
    r=G('(()=>{ const p=S.recs.find(x=>x.type==="policy"&&x.kind==="hr"&&x.firmId==="namuna01"); const o=p&&S.orders.find(x=>x.id===p.orderId); return p?[p.values.micro,p.values.overtime,o?.tplId,o?.status,o?.values?.responsible]:null; })()'); print(r)
    chk(r and r[0]=="1" and r[1]=="1","белгиланган параметрлар сақланмади")
    chk(r and r[2]=="kadr-nizomi" and r[3]=="draft","тасдиқлаш буйруғи тузилмади")
    chk(r and (r[4] or "")!="","буйруқда масъул шахс бўш")
    chk(G('V.tab')=="staff","сақлангандан кейин кадрлар бўлимидан чиқиб кетди")
    chk("КАДРЛАР НИЗОМИ" in G('document.body.innerText'),"сақлангандан кейин низом кўриниши очилмади")
    oid=G('S.recs.find(x=>x.type==="policy"&&x.kind==="hr").orderId')
    G(f'go({{view:"order",editSigned:null,draft:JSON.parse(JSON.stringify(S.orders.find(x=>x.id==="{oid}")))}})'); pg.wait_for_timeout(500)
    chk("Кадрлар низоми (илова қилинади) тасдиқлансин" in G('document.body.innerText'),"тасдиқлаш буйруғи матни чиқмади")
    # 5. Орқага → рўйхат ва параметрлар
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"nizom",polId:null,polEdit:null})'); pg.wait_for_timeout(500)
    t=G('document.body.innerText')
    chk("БЕЛГИЛАНГАН ПАРАМЕТРЛАР" in t.upper() and "АМАЛДАГИ НИЗОМ" in t.upper(),"низом хулосаси кўринмади")
    # 6. Ҳисоб сиёсати бўлимида ҳам
    G('go({view:"firm",firmId:"namuna01",tab:"policy",polK:"hr",polId:null,polEdit:null})'); pg.wait_for_timeout(500)
    chk(G('!!document.querySelector("[data-polk=hr]")'),"Ҳисоб сиёсати бўлимида «Кадрлар низоми» йўқ")
    chk(G('document.querySelectorAll("[data-pol]").length')>=1,"Ҳисоб сиёсати бўлимида низом рўйхатда йўқ")
    pg.screenshot(path=OUT+'kadr_nizomi_policy.png', full_page=False)
    # 7. Word/PDF кўриниши ва имзо
    h=G('polSheet(firm("namuna01"),S.recs.find(x=>x.type==="policy"&&x.kind==="hr"),true)')
    chk("Кадрлар иши бўйича масъул" in h and "1-илова" in h and "3-илова" in h,"тоза нусхада имзо ёки иловалар йўқ")
    # 8. Бошқа бўлимлар бузилмаган
    G('go({view:"firm",firmId:"namuna01",tab:"policy",polK:"acc",polId:null,polEdit:null})'); pg.wait_for_timeout(400)
    G('go({polEdit:polNew(firm("namuna01"),"acc"),polId:null})'); pg.wait_for_timeout(500)
    chk("БУХГАЛТЕРИЯ ҲИСОБИ СИЁСАТИ" in G('document.querySelector("#polSheet").innerText').upper(),"бухгалтерия ҳисоб сиёсати бузилди")
    G('go({polEdit:null,polId:null})')
    for sub in ("list","shtat","vac","plan","orders"):
        G(f'go({{view:"firm",firmId:"namuna01",tab:"staff",hrSub:"{sub}",polId:null,polEdit:null}})'); pg.wait_for_timeout(400)
        chk(G('document.body.innerText.length')>400,f"кадрлар «{sub}» бўлимчаси бўш")
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"nizom"})'); pg.wait_for_timeout(400)
    pg.screenshot(path=OUT+'kadr_nizomi.png', full_page=True)
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=90,f"версия в90 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
