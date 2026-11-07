# в71 — Аврора палитраси, «Соат бўйича» авто режим, «Зумрад» ранги сақланганми
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def V(pg,n): return pg.evaluate(f'getComputedStyle(document.documentElement).getPropertyValue("{n}").trim()')
def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p)

    # 1. Стандарт (созламасиз) — Аврора кундузги
    th=pg.evaluate('document.documentElement.getAttribute("data-theme")')
    ac=pg.evaluate('document.documentElement.getAttribute("data-accent")')
    print("standart", th, ac, V(pg,"--accent"), V(pg,"--bg"), V(pg,"--ink"))
    chk(th is None,"стандартда data-theme бўлмаслиги керак")
    chk(ac is None,"стандартда data-accent бўлмаслиги керак")
    chk(V(pg,"--accent")=="#7c3aed","кундузги урғу ранги Аврора эмас")
    chk(V(pg,"--bg")=="#f3f4fb","кундузги фон нотўғри")
    chk(V(pg,"--grad")!="" and V(pg,"--glow")!="","--grad/--glow йўқ")

    # 2. Аврора фони — 4 та доғ, босишга халақит бермайди
    bgi=pg.evaluate('getComputedStyle(document.body).backgroundImage')
    print("bg dogʻlar:",bgi.count("radial-gradient"))
    chk(bgi.count("radial-gradient")==4,"фонда 4 та доғ бўлиши керак")
    pg.evaluate('document.querySelector("#gearBtn").click()')
    pg.wait_for_timeout(300)
    chk(pg.evaluate('!!document.getElementById("uiPanel")'),"фон босишни тўсиб қўйди — панель очилмади")

    # 3. Панелда «Соат бўйича» тугмаси бор
    seg=pg.evaluate('[...document.querySelectorAll("#uiPanel [data-ui^=\'theme:\']")].map(b=>b.dataset.ui)')
    print("rejim tugmalari",seg)
    chk("theme:time" in seg,"«Соат бўйича» тугмаси йўқ")
    chk(len(seg)==4,"режим тугмалари 4 та бўлиши керак")

    # 4. Тунги режим
    pg.evaluate('uiSet({theme:"dark"})'); pg.wait_for_timeout(200)
    print("tun", pg.evaluate('document.documentElement.getAttribute("data-theme")'), V(pg,"--accent"), V(pg,"--bg"), V(pg,"--ink"))
    chk(pg.evaluate('document.documentElement.getAttribute("data-theme")')=="dark","тунги ўрнатилмади")
    chk(V(pg,"--accent")=="#a78bfa","тунги урғу ранги нотўғри")
    chk(V(pg,"--bg")=="#06070c","тунги фон нотўғри")
    chk(V(pg,"--paper")=="#f7f4ec","тунгида ҳужжат варағи оқ қолмади (PDF бузилади)")
    chk(pg.evaluate('uiDark()') is True,"uiDark() тунгини танимади")

    # 5. Соат бўйича авто
    pg.evaluate('uiSet({theme:"time"})'); pg.wait_for_timeout(200)
    h=pg.evaluate('new Date().getHours()')
    want="light" if 7<=h<19 else "dark"
    got=pg.evaluate('document.documentElement.getAttribute("data-theme")')
    print("soat",h,"kutilgan",want,"natija",got)
    chk(got==want,f"соат {h} да {want} бўлиши керак эди, {got} чиқди")
    chk(pg.evaluate('uiGet().theme')=="time","созлама сақланмади")
    chk(pg.evaluate('UI_TMR!==null'),"авто режим таймери ишга тушмади")
    # соатнинг иккала тармоғи
    both=pg.evaluate('(()=>{const g=Date.prototype.getHours;'
        'Date.prototype.getHours=()=>3;const a=uiTimeTheme();'
        'Date.prototype.getHours=()=>12;const b=uiTimeTheme();'
        'Date.prototype.getHours=()=>19;const c=uiTimeTheme();'
        'Date.prototype.getHours=()=>7;const d=uiTimeTheme();'
        'Date.prototype.getHours=g;return [a,b,c,d]})()')
    print("soat 3/12/19/7 ->",both)
    chk(both==["dark","light","dark","light"],"соат чегаралари нотўғри: "+str(both))

    # 6. Эски «Зумрад» ранги сақланган
    pg.evaluate('uiSet({theme:"light",accent:"teal"})'); pg.wait_for_timeout(200)
    print("zumrad", pg.evaluate('document.documentElement.getAttribute("data-accent")'), V(pg,"--accent"))
    chk(pg.evaluate('document.documentElement.getAttribute("data-accent")')=="teal","Зумрад ранги ўрнатилмади")
    chk(V(pg,"--accent")=="#0f6e5c","Зумрад яшили йўқолган")
    pg.evaluate('uiSet({theme:"dark",accent:"teal"})'); pg.wait_for_timeout(200)
    chk(V(pg,"--accent")=="#3cc3a4","тунги Зумрад нотўғри")

    # 7. Ранглар рўйхатида 7 та вариант, биринчиси Аврора
    accs=pg.evaluate('UI_ACC.map(a=>a[0])')
    print("ranglar",accs)
    chk(accs[0]=="aurora" and "teal" in accs and len(accs)==7,"ранглар рўйхати нотўғри")

    # 8. Дастур ишлаб турибдими — бўлимлар очиладими
    pg.evaluate('uiSet({theme:"",accent:""})'); pg.wait_for_timeout(200)
    for v in ("firms","home"):
        pg.evaluate(f'go({{view:"{v}"}})'); pg.wait_for_timeout(350)
    txt=pg.evaluate('document.body.innerText.length')
    print("sahifa uzunligi",txt)
    chk(txt>500,"саҳифа бўш қолди")
    print("VER", pg.evaluate('APP_VER'))
    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    chk(_n>=71,f"версия в71 ёки ундан юқори бўлиши керак, ҳозир: {_v}")

    b.close()
ok()
