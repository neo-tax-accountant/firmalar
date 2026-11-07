# в77 — юқори қатор: глобал қидирув, сана-соат, назорат маркази қўнғироғи
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

with sync_playwright() as p:
    b,pg=page(p,1440,900)
    pg.evaluate('uiSet({theme:"light",accent:""})'); pg.wait_for_timeout(250)
    pg.evaluate('ensureGtd&&ensureGtd()'); pg.wait_for_timeout(1400)
    pg.evaluate('render()'); pg.wait_for_timeout(500)

    # 1. Юқори қатор бор ва асосий қисм билан бир сатрда эмас
    chk(pg.evaluate('!!document.getElementById("appBar")'),"юқори қатор йўқ")
    d=pg.evaluate('document.getElementById("abDate").textContent')
    print("sana",d)
    chk("·" in d,"сана-соат кўрсатилмади: "+d)
    bell=pg.evaluate('[document.getElementById("abBellN").textContent,document.getElementById("abBellN").hidden]')
    print("qongiroq",bell)
    chk(bell[0] and not bell[1],"назорат маркази сони қўнғироқда чиқмади")
    chk(bell[0]==pg.evaluate('document.querySelector(\'[data-ca="ctl"] i\').textContent'),"қўнғироқ сони чап панелдагидан фарқ қиляпти")

    # 2. Икки ҳарфдан кам — рўйхат чиқмайди
    pg.fill("#gsq","н"); pg.wait_for_timeout(400)
    chk(pg.evaluate('document.getElementById("gsRes").hidden'),"1 ҳарфда ҳам қидирув очилди")

    # 3. Фирма номи бўйича
    pg.fill("#gsq","намуна"); pg.wait_for_timeout(450)
    chk(not pg.evaluate('document.getElementById("gsRes").hidden'),"қидирув рўйхати очилмади")
    chk(pg.evaluate('document.querySelectorAll(".gsr").length')>0,"фирма топилмади")

    # 4. ГТД рақами бўйича
    pg.fill("#gsq","1712345"); pg.wait_for_timeout(450)
    g=pg.evaluate('[...document.querySelectorAll(".gsg")].map(x=>x.textContent)')
    print("gtd guruh",g, pg.evaluate('[...document.querySelectorAll(".gsr b")].map(x=>x.textContent)'))
    chk(any("ГТД" in x for x in g),"ГТД рақами бўйича топилмади")

    # 5. Контрагент номи бўйича шартнома
    cp=pg.evaluate('(S.recs.find(r=>r.type==="contract"&&r.cp&&r.cp.name)||{}).cp?.name||""')
    if cp:
        pg.fill("#gsq",cp[:7]); pg.wait_for_timeout(450)
        gg=pg.evaluate('[...document.querySelectorAll(".gsg")].map(x=>x.textContent)')
        print("kontragent",cp[:7],gg)
        chk(any("Шартнома" in x for x in gg),"контрагент бўйича шартнома топилмади")

    # 6. Босилганда керакли фирма ва бўлим очилади, рўйхат ёпилади
    pg.fill("#gsq","1712345"); pg.wait_for_timeout(450)
    pg.evaluate('document.querySelector(".gsr").click()'); pg.wait_for_timeout(800)
    print("otdi",pg.evaluate('[V.view,V.tab]'))
    chk(pg.evaluate('V.view')=="firm" and pg.evaluate('V.tab')=="import","ГТД натижаси нотўғри бўлимга олиб борди")
    chk(pg.evaluate('document.getElementById("gsRes").hidden'),"танлагандан кейин рўйхат ёпилмади")
    chk(pg.evaluate('document.getElementById("gsq").value')=="","қидирув майдони тозаланмади")

    # 7. Саҳифа қайта чизилганда қидирув қатори йўқолмайди
    pg.evaluate('render()'); pg.wait_for_timeout(400)
    chk(pg.evaluate('!!document.getElementById("gsq")'),"қайта чизишда қидирув майдони йўқолди")

    # 8. Топилмаса — тушунарли хабар; Escape ёпади
    pg.fill("#gsq","zzzqqqxxx"); pg.wait_for_timeout(450)
    chk(pg.evaluate('!!document.querySelector(".gsempty")'),"топилмаганда хабар чиқмади")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
    chk(pg.evaluate('document.getElementById("gsRes").hidden'),"Escape рўйхатни ёпмади")

    # 9. «/» тугмаси қидирувга олиб боради
    pg.evaluate('document.getElementById("gsq").blur()'); pg.wait_for_timeout(150)
    pg.keyboard.press("/"); pg.wait_for_timeout(250)
    chk(pg.evaluate('document.activeElement.id')=="gsq","«/» тугмаси қидирувни фокусламади")
    chk(pg.evaluate('document.getElementById("gsq").value')!="/","«/» белгиси майдонга ёзилиб қолди")

    # 10. Дастур ишлаяпти
    pg.evaluate('go({view:"home"})'); pg.wait_for_timeout(500)
    chk(pg.evaluate('document.body.innerText.length')>500,"саҳифа бўш")
    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v)
    chk(_n>=77,f"версия в77 ёки ундан юқори бўлиши керак, ҳозир: {_v}")
    b.close()
ok()
