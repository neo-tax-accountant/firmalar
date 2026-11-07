# в76 — чап панелда фирма бўлимлари (компьютерда), телефонда эскиси
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p,1440,1000)
    fid=pg.evaluate('S.firms[0].id')
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(250)

    # 1. Бош саҳифада бўлимлар рўйхати бўлмайди, фирмалар кўринади
    pg.evaluate('go({view:"home"})'); pg.wait_for_timeout(600)
    chk(not pg.evaluate('!!document.getElementById("secList")'),"бош саҳифада бўлимлар рўйхати қолиб кетди")
    chk(not pg.evaluate('document.documentElement.classList.contains("firmopen")'),"firmopen синфи нотўғри")
    chk(pg.evaluate('getComputedStyle(document.getElementById("firmList")).display')!="none","бош саҳифада фирмалар рўйхати йўқолди")

    # 2. Фирма очилганда — бўлимлар
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"overview"}})'); pg.wait_for_timeout(900)
    n=pg.evaluate('document.querySelectorAll("#secList li").length')
    menus=pg.evaluate(f'firmMenus(firm("{fid}")).length')
    print("bolimlar",n,"/",menus)
    chk(n==menus,f"бўлимлар сони мос эмас: {n} ва {menus}")
    chk(pg.evaluate('getComputedStyle(document.getElementById("firmList")).display')=="none","фирмалар рўйхати яширилмади")
    chk(pg.evaluate('!!document.querySelector(".backfirms")'),"«← Фирмалар» тугмаси йўқ")
    chk(pg.evaluate('document.querySelector(".curfirm").textContent')==pg.evaluate(f'firm("{fid}").name'),"жорий фирма номи нотўғри")

    # иконка ва матн бир чизиқда, ном қирқилмайди
    al=pg.evaluate('(()=>{const r=[...document.querySelectorAll("#secList button")].map(c=>{const b=c.getBoundingClientRect();'
                   'return [Math.round(c.querySelector(".sn-i").getBoundingClientRect().x-b.x),Math.round(c.querySelector(".sn-t").getBoundingClientRect().x-b.x)];});'
                   'return [new Set(r.map(x=>x[0])).size,new Set(r.map(x=>x[1])).size];})()')
    print("tekislik",al)
    chk(al==[1,1],"иконка ёки ном бир чизиқда эмас: "+str(al))
    cut=pg.evaluate('[...document.querySelectorAll("#secList .sn-t")].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent)')
    chk(not cut,"бўлим номи қирқилган: "+str(cut))

    # рўйхат узун бўлса ҳам кўриб чиқиш мумкин
    ov=pg.evaluate('getComputedStyle(document.getElementById("secList")).overflowY')
    chk(ov in ("auto","scroll"),"узун рўйхат айлантирилмайди: "+ov)

    # 3. Сонлар
    cnt=pg.evaluate('Object.fromEntries([...document.querySelectorAll("#secList button")].map(x=>[x.dataset.tab,x.querySelector("i")?.textContent||""]))')
    print("sonlar",{k:v for k,v in cnt.items() if v})
    for k in ("reqs","bank","orders","taxrep","contracts","import","staff"):
        chk(cnt.get(k),f"«{k}» бўлимида сон йўқ")

    # 4. Босилганда бўлим очилади, юқоридаги тасма такрорланмайди
    pg.evaluate('document.querySelector("#secList [data-tab=contracts]").click()'); pg.wait_for_timeout(900)
    chk(pg.evaluate('V.tab')=="contracts","бўлим очилмади")
    chk(pg.evaluate('document.querySelector("#secList [data-tab=contracts]").getAttribute("aria-current")')=="true","очиқ бўлим белгиланмади")
    ds=pg.evaluate('(()=>{const d=document.querySelector(".dstrip");return d?getComputedStyle(d).display:"yoq"})()')
    print("dstrip",ds)
    chk(ds in ("none","yoq"),"компьютерда юқориги тасма ҳам, чап панель ҳам кўриняпти")
    chk(pg.evaluate('document.body.innerText.length')>500,"бўлим бўш")

    # 5. Орқага қайтиш
    pg.evaluate('document.querySelector(".backfirms").click()'); pg.wait_for_timeout(700)
    chk(pg.evaluate('V.view')=="home","«← Фирмалар» ишламади")
    chk(not pg.evaluate('!!document.getElementById("secList")'),"қайтгач бўлимлар рўйхати ўчмади")
    chk(pg.evaluate('getComputedStyle(document.getElementById("firmList")).display')!="none","қайтгач фирмалар рўйхати тикланмади")

    # 6. Телефонда — эскисича: фирмалар рўйхати ва юқориги тасма
    pg.set_viewport_size({"width":430,"height":900}); pg.wait_for_timeout(300)
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"contracts"}})'); pg.wait_for_timeout(900)
    print("tel secList", pg.evaluate('getComputedStyle(document.getElementById("secList")).display'),
          "| firmList", pg.evaluate('getComputedStyle(document.getElementById("firmList")).display'),
          "| dstrip", pg.evaluate('(()=>{const d=document.querySelector(".dstrip");return d?getComputedStyle(d).display:"yoq"})()'))
    chk(pg.evaluate('getComputedStyle(document.getElementById("secList")).display')=="none","телефонда бўлимлар рўйхати яширилмади")
    # телефонда панель менюси ёпиқ туради (эски хулқ) — очиб текширамиз
    pg.evaluate('uiNav(true)'); pg.wait_for_timeout(300)
    print("tel menyu ochiq: secList", pg.evaluate('getComputedStyle(document.getElementById("secList")).display'),
          "| firmList", pg.evaluate('getComputedStyle(document.getElementById("firmList")).display'))
    chk(pg.evaluate('getComputedStyle(document.getElementById("firmList")).display')!="none","телефонда меню очилганда фирмалар рўйхати чиқмади")
    chk(pg.evaluate('getComputedStyle(document.getElementById("secList")).display')=="none","телефонда меню очилганда бўлимлар рўйхати чиқиб кетди")
    pg.evaluate('uiNav(false)'); pg.wait_for_timeout(200)
    chk(pg.evaluate('(()=>{const d=document.querySelector(".dstrip");return d&&getComputedStyle(d).display!=="none"})()'),"телефонда юқориги тасма йўқолди")

    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v)
    chk(_n>=76,f"версия в76 ёки ундан юқори бўлиши керак, ҳозир: {_v}")
    b.close()
ok()
