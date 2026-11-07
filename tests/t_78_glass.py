# в78 — шиша кўриниш, чизиқли вкладкалар, ихчам фильтрлар; ҳужжатлар оқ қолиши
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)
def css(pg,sel,prop):
    return pg.evaluate(f'(()=>{{const e=document.querySelector({sel!r});return e?getComputedStyle(e)[{prop!r}]:null}})()')

with sync_playwright() as p:
    b,pg=page(p,1560,1000)
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(250)
    pg.evaluate('ensureGtd&&ensureGtd()'); pg.wait_for_timeout(1500)
    fid=pg.evaluate('S.firms[0].id')
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"import"}})'); pg.wait_for_timeout(1100)

    # 1. Шиша — карточкалар
    bf=css(pg,".card","backdropFilter") or css(pg,".card","webkitBackdropFilter")
    print("card blur",bf,"|",css(pg,".card","backgroundColor"))
    chk("blur" in (bf or ""),"карточкада шиша эффекти йўқ")

    # 2. Вкладкалар — остига чизиқ, юмалоқ chip эмас
    t=pg.evaluate('(()=>{const t=document.querySelector(".hrtabs .chip[aria-pressed=true]");if(!t)return null;'
                  'const c=getComputedStyle(t);const h=getComputedStyle(document.querySelector(".hrtabs"));'
                  'return {r:c.borderRadius,bb:c.borderBottomWidth,bg:c.backgroundColor,hb:h.borderBottomWidth};})()')
    print("vkladka",t)
    chk(t is not None,"вкладкалар топилмади")
    chk(t["r"]=="0px","вкладка ҳали юмалоқ chip кўринишида")
    chk(t["bb"]=="2px","танланган вкладка остида чизиқ йўқ")
    chk(t["bg"]=="rgba(0, 0, 0, 0)","вкладка фони тўлдирилган — чизиқли бўлиши керак")
    chk(t["hb"]=="1px","вкладкалар қатори остида ажратувчи чизиқ йўқ")

    # 3. Фильтрлар — бир қаторда, ихчам
    fl=pg.evaluate('(()=>{const f=document.querySelector(".ctfilters");if(!f)return null;const c=getComputedStyle(f);'
                   'const ch=f.querySelector(".chip"),se=f.querySelector(".gsel");'
                   'return {disp:c.display,al:c.alignItems,bf:c.backdropFilter||c.webkitBackdropFilter,'
                   'chh:ch?Math.round(ch.getBoundingClientRect().height):0,seh:se?Math.round(se.getBoundingClientRect().height):0,'
                   'rows:new Set([...f.children].map(x=>Math.round(x.getBoundingClientRect().y))).size};})()')
    print("filtrlar",fl)
    chk(fl is not None,"фильтрлар қатори топилмади")
    chk(fl["disp"]=="flex" and fl["al"]=="center","фильтрлар бир қаторга тизилмаган")
    chk(fl["rows"]==1,f'фильтрлар {fl["rows"]} қаторга бўлиниб кетди')
    chk(fl["chh"]<=30,f'фильтр тугмаси ихчам эмас: {fl["chh"]}px')
    chk("blur" in (fl["bf"] or ""),"фильтрлар қаторида шиша эффекти йўқ")

    # 4. Рақамли карточкалар — шиша, ўқилади
    for th,want in (("light","rgba(255, 255, 255"),("dark","rgba(13, 15, 26")):
        pg.evaluate(f'uiSet({{theme:"{th}"}})'); pg.wait_for_timeout(300)
        bg=css(pg,".lstat","backgroundColor"); blur=css(pg,".lstat","backdropFilter") or css(pg,".lstat","webkitBackdropFilter")
        print(th,"lstat",bg,blur)
        chk(bg.startswith(want),f"{th}: рақамли карточка фони нотўғри: {bg}")
        chk("blur" in (blur or ""),f"{th}: рақамли карточкада шиша йўқ")
    chk(css(pg,".lstats","backgroundColor")=="rgba(0, 0, 0, 0)","панель фони шаффоф эмас")

    # 5. Ҳужжат варағи — шиша эмас, оқ қолади (PDF учун муҳим)
    pg.evaluate('uiSet({theme:"dark"})'); pg.wait_for_timeout(250)
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"orders"}})'); pg.wait_for_timeout(900)
    oid=pg.evaluate('(S.orders.find(o=>o.firmId==="%s")||{}).id||""'%fid)
    if oid:
        pg.evaluate(f'document.querySelector(\'[data-order="{oid}"]\')?.click()'); pg.wait_for_timeout(1400)
        sh=pg.evaluate('(()=>{const e=document.querySelector(".sheet");if(!e)return null;const c=getComputedStyle(e);'
                       'return {bg:c.backgroundColor,bf:c.backdropFilter||c.webkitBackdropFilter};})()')
        print("hujjat varagi",sh)
        if sh:
            chk("blur" not in (sh["bf"] or "none"),"ҳужжат варағига шиша қўлланиб қолди — PDF бузилади")
            chk(sh["bg"] not in ("rgba(0, 0, 0, 0)",),"ҳужжат варағи шаффоф бўлиб қолди")

    # 6. Бошқа бўлимлар очилаверадими
    pg.evaluate('uiSet({theme:"light"})'); pg.wait_for_timeout(200)
    for tab in ("contracts","taxrep","staff","office","orders","overview"):
        pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"{tab}"}})'); pg.wait_for_timeout(600)
        chk(pg.evaluate('document.body.innerText.length')>400,f"«{tab}» бўлими бўш қолди")
    for v in ("cps","gtd","ctl","home"):
        pg.evaluate(f'go({{view:"{v}"}})'); pg.wait_for_timeout(700)
        chk(pg.evaluate('document.body.innerText.length')>400,f"«{v}» саҳифаси бўш қолди")

    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v)
    chk(_n>=78,f"версия в78 ёки ундан юқори бўлиши керак, ҳозир: {_v}")
    b.close()
ok()
