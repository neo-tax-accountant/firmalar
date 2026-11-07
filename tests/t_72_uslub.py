# в72 — Аврора «чақнаши»: тугма градиенти, карточка кўтарилиши, фильтр ранги
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p)
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(250)
    pg.evaluate('go({view:"firms"})'); pg.wait_for_timeout(700)

    # 1. Асосий тугма — Аврора градиенти
    st=pg.evaluate('(()=>{const b=document.querySelector(".btn.primary");if(!b)return null;'
                   'const c=getComputedStyle(b);return {bi:c.backgroundImage,bc:c.backgroundColor,sh:c.boxShadow};})()')
    print("btn.primary",st and st["bi"][:60], "|", st and st["bc"])
    chk(st is not None,".btn.primary топилмади")
    chk("gradient" in (st or {}).get("bi",""),"Аврора градиенти қўлланмади")
    chk("rgb" in (st or {}).get("sh",""),"тугма сояси йўқ")

    # 2. Бошқа ранг танланса — градиент бўлмайди (эски кўриниш сақланади)
    pg.evaluate('uiSet({accent:"teal"})'); pg.wait_for_timeout(250)
    bi2=pg.evaluate('getComputedStyle(document.querySelector(".btn.primary")).backgroundImage')
    print("teal btn",bi2)
    chk(bi2=="none","Зумрад танланганда градиент бўлмаслиги керак")
    pg.evaluate('uiSet({accent:""})'); pg.wait_for_timeout(250)

    # 3. Фирма карточкаси — ўтиш эффекти ва hover
    fc=pg.evaluate('(()=>{const f=document.querySelector(".fcard");if(!f)return null;'
                   'const c=getComputedStyle(f);return {tr:c.transitionProperty};})()')
    print("fcard",fc)
    chk(fc is not None,".fcard топилмади")
    chk("transform" in (fc or {}).get("tr",""),"карточкада transform ўтиши йўқ")

    # 4. Танланган фильтр — урғу ранги
    ch=pg.evaluate('(()=>{const c=document.querySelector(\'.chip[aria-pressed="true"]\');if(!c)return null;'
                   'const s=getComputedStyle(c);return {bg:s.backgroundColor,col:s.color,sh:s.boxShadow};})()')
    print("chip on",ch)
    chk(ch is not None,"танланган chip топилмади")
    chk((ch or {}).get("bg")=="rgb(124, 58, 237)","фильтр ранги Аврора урғуси эмас: "+str(ch))
    chk((ch or {}).get("col")=="rgb(255, 255, 255)","фильтр матни оқ эмас")

    # 5. Рақамли панель (Контрагентлар бўлими) — Аврора оҳанги
    pg.evaluate('go({view:"cps"})'); pg.wait_for_timeout(700)
    ls=pg.evaluate('(()=>{const e=document.querySelector(".lstats");if(!e)return "yoq";'
                   'const c=getComputedStyle(e);return c.backgroundColor+" | "+c.backgroundImage.split("radial").length;})()')
    print("lstats",ls)
    chk(ls!="yoq",".lstats панели топилмади")
    # в78: панель шаффоф, карточкаларнинг ўзи шиша (мавзуга мослашади)
    chk(ls.startswith("rgba(0, 0, 0, 0)"),"панель шаффоф бўлиши керак: "+ls)
    lb=pg.evaluate('(()=>{const e=document.querySelector(".lstat");const c=getComputedStyle(e);'
                   'return {bg:c.backgroundColor,bf:c.backdropFilter||c.webkitBackdropFilter,col:getComputedStyle(e.querySelector(".v")).color};})()')
    print("lstat",lb)
    chk("blur" in (lb["bf"] or ""),"рақамли карточкада шиша эффекти йўқ")
    chk(lb["bg"].startswith("rgba(255, 255, 255"),"кундузгида карточка оқ шиша эмас: "+lb["bg"])
    lv=pg.evaluate('(()=>{const e=document.querySelector(".lstat .v");return e?getComputedStyle(e).fontFamily:"yoq"})()')
    print("lstat .v shrift",lv)
    chk("Unbounded" in lv,"катта рақамлар Unbounded шрифтида эмас")

    # 6. Тунги режимда ҳам ишлайди, ҳужжат варағи оқ
    pg.evaluate('uiSet({theme:"dark"})'); pg.wait_for_timeout(250)
    chk(pg.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--paper").trim()')=="#f7f4ec","тунгида варақ оқ эмас")
    chk("gradient" in pg.evaluate('getComputedStyle(document.querySelector(".btn.primary")).backgroundImage'),"тунгида градиент йўқ")

    # 7. Дастур ишлаяпти
    pg.evaluate('uiSet({theme:""})'); pg.wait_for_timeout(200)
    for v in ("home","firms"):
        pg.evaluate(f'go({{view:"{v}"}})'); pg.wait_for_timeout(350)
    chk(pg.evaluate('document.body.innerText.length')>500,"саҳифа бўш")
    print("VER",pg.evaluate('APP_VER'))
    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    chk(_n>=72,f"версия в72 ёки ундан юқори бўлиши керак, ҳозир: {_v}")
    b.close()
ok()
