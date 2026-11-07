# в80 — қулайлик тузатишлари: клавиатура, aria, touch-action, Intl, reduced-motion
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p,1440,900)
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(250)
    pg.evaluate('ensureGtd&&ensureGtd()'); pg.wait_for_timeout(1400)
    pg.evaluate('render()'); pg.wait_for_timeout(400)

    # 1. Combobox семантикаси
    a=pg.evaluate('(()=>{const i=document.getElementById("gsq");return {role:i.getAttribute("role"),ex:i.getAttribute("aria-expanded"),'
                  'ctr:i.getAttribute("aria-controls"),aa:i.getAttribute("aria-autocomplete")};})()')
    print("combobox",a)
    chk(a["role"]=="combobox" and a["ctr"]=="gsRes" and a["aa"]=="list","combobox семантикаси тўлиқ эмас")
    chk(a["ex"]=="false","ёпиқ ҳолатда aria-expanded false бўлиши керак")
    chk(pg.evaluate('document.querySelector(".gskbd").getAttribute("aria-hidden")')=="true","«/» белгиси aria-hidden эмас")

    # 2. Клавиатура: ↓ ↑ Enter
    pg.click("#gsq"); pg.fill("#gsq","26013"); pg.wait_for_timeout(450)
    chk(pg.evaluate('document.getElementById("gsq").getAttribute("aria-expanded")')=="true","очилганда aria-expanded true бўлмади")
    chk(pg.evaluate('(document.getElementById("gsLive").textContent||"").includes("натижа")'),"натижа сони эълон қилинмади: "+pg.evaluate('document.getElementById("gsLive").textContent'))
    pg.keyboard.press("ArrowDown"); pg.wait_for_timeout(200)
    st=pg.evaluate('(()=>{const i=document.getElementById("gsq");const s=document.querySelector(".gsr[aria-selected=true]");'
                   'return {ad:i.getAttribute("aria-activedescendant"),sel:s?s.id:null};})()')
    print("ArrowDown",st)
    chk(st["sel"] and st["ad"]==st["sel"],"↓ босилганда натижа танланмади")
    n=pg.evaluate('document.querySelectorAll(".gsr").length')
    print("natijalar",n)
    chk(n>=2,"клавиатура текшируви учун камида 2 та натижа керак эди")
    pg.keyboard.press("ArrowUp"); pg.wait_for_timeout(150)
    up=pg.evaluate('[...document.querySelectorAll(".gsr")].findIndex(x=>x.getAttribute("aria-selected")==="true")')
    print("ArrowUp index",up,"/",n)
    chk(up==n-1,"↑ рўйхат охирига ўтмади")
    pg.keyboard.press("Home"); pg.wait_for_timeout(150)
    chk(pg.evaluate('[...document.querySelectorAll(".gsr")].findIndex(x=>x.getAttribute("aria-selected")==="true")')==0,"Home бошига олиб бормади")
    pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
    print("Enter -> ",pg.evaluate('[V.view,V.tab]'))
    chk(pg.evaluate('V.view')=="firm","Enter натижани очмади")
    chk(pg.evaluate('document.getElementById("gsRes").hidden'),"Enter'дан кейин рўйхат ёпилмади")
    chk(pg.evaluate('document.getElementById("gsq").getAttribute("aria-expanded")')=="false","ёпилгач aria-expanded false бўлмади")
    chk(not pg.evaluate('document.getElementById("gsq").hasAttribute("aria-activedescendant")'),"aria-activedescendant тозаланмади")

    # 3. Escape қидирувга фокусни қайтаради
    pg.fill("#gsq","намуна"); pg.wait_for_timeout(450)
    pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
    chk(pg.evaluate('document.getElementById("gsRes").hidden'),"Escape ёпмади")
    chk(pg.evaluate('document.activeElement.id')=="gsq","Escape'дан кейин фокус қидирувда қолмади")

    # 4. Қўнғироқ сони aria-label ичида
    al=pg.evaluate('document.getElementById("abBell").getAttribute("aria-label")')
    print("qongiroq",al)
    chk("муддати ўтган" in al,"қўнғироқ aria-label'ида сон йўқ: "+str(al))
    chk(pg.evaluate('document.getElementById("abBellN").getAttribute("aria-hidden")')=="true","қўнғироқ рақами икки марта ўқилади")

    # 5. touch-action ва tap-highlight
    ta=pg.evaluate('getComputedStyle(document.querySelector(".btn")).touchAction')
    print("touch-action",ta)
    chk(ta=="manipulation","тугмаларда touch-action:manipulation йўқ")
    chk(pg.evaluate('getComputedStyle(document.body).webkitTapHighlightColor')!="","tap-highlight белгиланмаган")

    # 6. Қидирув рўйхати саҳифани суриб юбормайди
    chk(pg.evaluate('getComputedStyle(document.getElementById("gsRes")).overscrollBehavior').startswith("contain"),
        "qidiruv ro'yxatida overscroll-behavior:contain yo'q")

    # 7. Сана Intl орқали
    chk(pg.evaluate('typeof AB_FMT==="function"'),"AB_FMT йўқ")
    chk(not pg.evaluate('typeof AB_M!=="undefined"'),"эски AB_M массиви қолиб кетди")
    d=pg.evaluate('document.getElementById("abDate").textContent')
    print("sana",d)
    chk("·" in d and any(ch.isdigit() for ch in d),"сана нотўғри: "+d)

    # 8. transition:all ва outline:none қолмади
    bad=pg.evaluate('''(()=>{const out=[];for(const sh of document.styleSheets){let rs;try{rs=sh.cssRules}catch(e){continue}
      for(const r of rs){const t=r.cssText||"";
        if(/transition:\\s*all/.test(t)) out.push("transition:all → "+t.slice(0,40));
        if(/outline:\\s*none/.test(t)&&!/focus-visible/.test(t)) out.push("outline:none → "+t.slice(0,40));}}
      return out})()''')
    print("qolgan",bad)
    chk(not bad,"антипаттерн қолди: "+str(bad))

    # 9. Ҳаракатни камайтириш режими
    pg2=pg.context.browser.new_context(reduced_motion="reduce",viewport={"width":1200,"height":800}).new_page()
    pg2.route("**/cdnjs.cloudflare.com/**",route); pg2.route("**/cdn.jsdelivr.net/**",route)
    pg2.route("**/fonts.g*/**",lambda r:r.abort()); pg2.route("**/chamber.uz/**",lambda r:r.abort())
    pg2.goto("file://"+DEMO); pg2.wait_for_timeout(1600)
    pg2.evaluate('go({view:"home"})'); pg2.wait_for_timeout(700)
    tr=pg2.evaluate('(()=>{const f=document.querySelector(".fcard");return f?getComputedStyle(f).transitionDuration:null})()')
    print("reduced fcard",tr)
    if tr is not None: chk(tr in ("0s","0s, 0s, 0s"),"reduced-motion'да .fcard ўтиши ўчмади: "+str(tr))
    pg2.close()

    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v)
    chk(_n>=80,f"версия в80 ёки ундан юқори бўлиши керак, ҳозир: {_v}")
    b.close()
ok()
