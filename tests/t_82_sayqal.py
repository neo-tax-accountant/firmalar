# в82 — easing, ::selection, айлантиргич, радиус шкаласи
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p,1440,900)
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(300)
    g=lambda n:pg.evaluate(f'getComputedStyle(document.documentElement).getPropertyValue("{n}").trim()')

    # 1. Радиус шкаласи — 3 поғона, иккала зичликда ҳам тартибли
    for dense,lbl in ((True,"ихчам"),(False,"кенг")):
        pg.evaluate(f'uiSet({{dense:{str(dense).lower()}}})'); pg.wait_for_timeout(250)
        v=[int(g(x)[:-2]) for x in ("--r-s","--r","--r-l")]
        print(lbl,v)
        chk(v[0]<v[1]<v[2],f"{lbl}: радиус шкаласи ўсиб бормаяпти: {v}")
    pg.evaluate('uiSet({dense:true})'); pg.wait_for_timeout(250)

    # қаттиq ёзилган радиуслар деярли қолмаган
    hard=pg.evaluate('''(()=>{let n=0;for(const sh of document.styleSheets){let rs;try{rs=sh.cssRules}catch(e){continue}
      for(const r of rs){const m=(r.cssText||"").match(/border-radius:\\s*\\d+px/g); if(m) n+=m.filter(x=>!/:\\s*(0|2|3|4|99|999)px/.test(x)).length;}}
      return n})()''')
    print("қаттиқ радиуслар",hard)
    chk(hard==0,f"ҳали {hard} та қаттиқ ёзилган border-radius бор")

    # 2. Easing — стандарт emas
    tf=pg.evaluate('getComputedStyle(document.querySelector(".btn")).transitionTimingFunction')
    print("btn easing",tf)
    chk("cubic-bezier" in tf,"тугмада аниқ easing йўқ")
    chk(g("--e-soft") and g("--e-eleg") and g("--e-snap"),"easing ўзгарувчилари тўлиқ эмас")

    # 3. ::selection ва айлантиргич
    sel=pg.evaluate('''(()=>{for(const sh of document.styleSheets){let rs;try{rs=sh.cssRules}catch(e){continue}
      for(const r of rs){const t=r.cssText||""; if(/::selection/.test(t)) return t.slice(0,90);}}return null})()''')
    print("selection",sel)
    chk(sel and "accent" in sel,"::selection урғу рангида эмас")
    sb=pg.evaluate('''(()=>{let n=0;for(const sh of document.styleSheets){let rs;try{rs=sh.cssRules}catch(e){continue}
      for(const r of rs){if(/::-webkit-scrollbar/.test(r.cssText||"")) n++;}}return n})()''')
    print("scrollbar qoidalari",sb)
    chk(sb>=3,"айлантиргич услуби тўлиқ эмас")
    chk(pg.evaluate('getComputedStyle(document.documentElement).scrollbarWidth')=="thin","scrollbar-width:thin қўйилмаган")

    # 4. Кўриниш бузилмаган — ҳар бир асосий блок ўлчами жойида
    fid=pg.evaluate('S.firms[0].id')
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"overview"}})'); pg.wait_for_timeout(900)
    r=pg.evaluate('(()=>{const c=document.querySelector(".fsc"),d=document.querySelector(".dcard");'
                  'return [getComputedStyle(c).borderRadius,getComputedStyle(d).borderRadius]})()')
    print("radiuslar",r)
    chk(all(x.endswith("px") and int(float(x.replace("px",""))) >= 6 for x in r),"карточка радиуслари йўқолди: "+str(r))
    chk(pg.evaluate('document.body.innerText.length')>500,"саҳифа бўш")

    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=82,f"версия в82 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
