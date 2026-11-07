# в73–в74 — фирма «Умумий кўриниш»: 4 та стат карточка ва ихчам плиткалар
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p,1440,1100)
    fid=pg.evaluate('S.firms[0].id')
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(250)
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"overview"}})'); pg.wait_for_timeout(800)

    # 1. Тўрт карточка
    n=pg.evaluate('document.querySelectorAll(".fsum4 .fsc").length')
    print("fsc",n)
    chk(n==4,f"4 та карточка кутилган эди, {n} чиқди")
    chk(pg.evaluate('!!document.querySelector(".fsc-rate .rscore")'),"рейтинг балли кўринмаяпти")
    fs=pg.evaluate('getComputedStyle(document.querySelector(".fsc-rate .rscore")).fontFamily')
    chk("Unbounded" in fs,"рейтинг балли Unbounded эмас: "+fs)

    # 2. Солиқ муддати — яқинлашаётгани, муддати ўтгани эмас
    nt=pg.evaluate(f'firmNextTax(firm("{fid}"))')
    print("nextTax",nt)
    chk(isinstance(nt,dict) and "next" in nt and "over" in nt,"firmNextTax тузилмаси нотўғри")
    if nt and nt.get("next"):
        td=pg.evaluate('localToday()')
        chk(nt["next"]["dl"]>=td,"навбатдаги муддат ўтган кун чиқди: "+str(nt["next"]["dl"]))
        chk(pg.evaluate('!!document.querySelector(".fsbar i")'),"муддат прогресси йўқ")
        w=pg.evaluate('document.querySelector(".fsbar i").style.width')
        chk(w.endswith("%") and 0<=float(w[:-1])<=100,"прогресс фоизи нотўғри: "+w)
    if nt and nt.get("over"):
        chk(pg.evaluate('!!document.querySelector(".fsc .linkbtn.r")'),"муддати ўтганлар ҳақида огоҳлантириш йўқ")

    # 3. Плиткалар — ихчам, иконка чапда, матн ўнгда
    t=pg.evaluate('document.querySelectorAll(".dcard").length')
    print("plitkalar",t)
    chk(t>=15,f"плиткалар кам: {t}")
    g=pg.evaluate('(()=>{const c=document.querySelector(".dcard");const s=getComputedStyle(c);'
                  'const i=c.querySelector(".dc-i").getBoundingClientRect(), x=c.querySelector(".dc-t").getBoundingClientRect();'
                  'return {disp:s.display,cols:s.gridTemplateColumns,icw:Math.round(i.width),ix:Math.round(i.x),tx:Math.round(x.x)};})()')
    print("dcard",g)
    chk(g["disp"]=="grid","плитка grid эмас")
    chk(g["icw"]<=48,"иконка жуда катта: "+str(g["icw"]))
    chk(g["tx"]>g["ix"],"матн иконканинг ўнгида эмас")

    # иконка ва матн барча плиткаларда бир чизиқда
    al=pg.evaluate('(()=>{const r=[...document.querySelectorAll(".dcard")].map(c=>{'
                   'const b=c.getBoundingClientRect();return [Math.round(c.querySelector(".dc-i").getBoundingClientRect().x-b.x),'
                   'Math.round(c.querySelector(".dc-t").getBoundingClientRect().x-b.x)];});'
                   'return [new Set(r.map(x=>x[0])).size,new Set(r.map(x=>x[1])).size];})()')
    print("tekislik",al)
    chk(al==[1,1],"иконка ёки матн бир чизиқда эмас: "+str(al))

    # 4. Панель мавзуга мослашади (қаттиқ кўк фон йўқ)
    dp=pg.evaluate('getComputedStyle(document.querySelector(".dpanel")).backgroundColor')
    dc=pg.evaluate('getComputedStyle(document.querySelector(".dcard")).backgroundColor')
    print("panel",dp,"card",dc)
    chk(dc=="rgb(255, 255, 255)","кундузгида плитка оқ эмас: "+dc)
    pg.evaluate('uiSet({theme:"dark"})'); pg.wait_for_timeout(300)
    dc2=pg.evaluate('getComputedStyle(document.querySelector(".dcard")).backgroundColor')
    print("tunda card",dc2)
    chk(dc2=="rgb(17, 19, 31)","тунгида плитка қорамтир эмас: "+dc2)

    # 5. Плитка босилганда бўлим очилади
    pg.evaluate('uiSet({theme:"light"})'); pg.wait_for_timeout(250)
    pg.evaluate('[...document.querySelectorAll(".dcard")].find(c=>c.dataset.tab==="reqs").click()'); pg.wait_for_timeout(700)
    print("tab",pg.evaluate('V.tab'))
    chk(pg.evaluate('V.tab')=="reqs","плитка босилганда бўлим очилмади")
    chk(pg.evaluate('document.body.innerText.length')>500,"бўлим бўш")

    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v)
    chk(_n>=74,f"версия в74 ёки ундан юқори бўлиши керак, ҳозир: {_v}")
    b.close()
ok()
