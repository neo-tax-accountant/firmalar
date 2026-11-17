# в87 — QR ҳужжатлардан олиб ташланди; директор/бош бухгалтер тарихи ҳужжат санаси бўйича; штат: сони билан, такрорсиз
import os, json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
def chk(c,msg):
    if not c: errs.append(msg)
with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    # 1. QR
    chk(G('docQrBlock("contract",S.recs.find(r=>r.type==="contract"))')=="","docQrBlock ҳали QR қайтаряпти")
    chk(G('qrStampOn()')==False,"юкланган файлларга QR муҳри ҳали ёқиқ")
    old=G('firm("namuna01").director'); olda=G('firm("namuna01").chiefAccountant'); print("old",old,olda)
    for t,sel in [("contracts",'[data-ct]'),("orders",'[data-order]')]:
        G(f'go({{view:"firm",firmId:"namuna01",tab:"{t}"}})'); pg.wait_for_timeout(500)
        if G(f'!!document.querySelector(\'{sel}\')'): pg.click(sel); pg.wait_for_timeout(1500)
        chk(G('!document.querySelector(".docqr,.qrimg,.pubq")'),f"{t}: ҳужжатда QR блоки қолган")
    # 2. Директор алмашиши: санасиз — хато, санали — эскиси тарихга
    G('go({view:"firm",firmId:"namuna01",tab:"reqs"})'); pg.wait_for_timeout(400)
    pg.click('[data-act="editFirm"]'); pg.wait_for_timeout(500)
    chk(G('!!document.querySelector("#ff_dirFrom")&&!!document.querySelector("#ff_accFrom")'),"«Тайинланган сана» майдонлари йўқ")
    pg.fill('#ff_director',"Янгиев Бобур Акмалович"); pg.fill('#ff_chiefAccountant',"Ҳисобчиева Малика")
    pg.click('#firmForm [type=submit]'); pg.wait_for_timeout(700)
    chk("тайинланган санасини киритинг" in G('document.querySelector("#firmErr").textContent'),"санасиз директор алмашганда огоҳлантирилмади")
    pg.fill('#ff_dirFrom',"2026-06-01"); pg.fill('#ff_accFrom',"2026-09-15")
    pg.click('#firmForm [type=submit]'); pg.wait_for_timeout(1500)
    f=G('(()=>{const f=firm("namuna01"); return {d:f.director,df:f.dirFrom,h:f.dirHist,ah:f.accHist}})()'); print(json.dumps(f,ensure_ascii=False)[:500])
    chk(f["d"]=="Янгиев Бобур Акмалович" and f["df"]=="2026-06-01","янги директор сақланмади")
    chk(f["h"] and f["h"][-1]["director"]==old and f["h"][-1]["to"]=="2026-05-31","эски директор тарихга тўғри ўтмади")
    chk(f["ah"] and f["ah"][-1]["chiefAccountant"]==olda and f["ah"][-1]["to"]=="2026-09-14","эски бош бухгалтер тарихга ўтмади")
    chk("Раҳбарлар тарихи" in G('document.body.textContent'),"реквизитларда раҳбарлар тарихи кўринмади")
    # 3. Ҳужжат санасига қараб
    r=G('''(()=>{ const f=firm("namuna01"); const tpl=TEMPLATES.find(t=>t.signers==null)||TEMPLATES[0];
      const s1=ordSigners(tpl,{date:"2026-03-10"},f), s2=ordSigners(tpl,{date:"2026-07-10"},f);
      const c=S.recs.find(r=>r.type==="contract"&&r.dir==="out"); const h1=ctgSheet(f,{...c,date:"2026-02-01"},true), h2=ctgSheet(f,{...c,date:"2026-11-01"},true);
      const e=firmEmps("namuna01")[0]; const e1=empContractSheet(f,{...e,contractDate:"2026-01-05",hireDate:"2026-01-05"},"uz",true), e2=empContractSheet(f,{...e,contractDate:"2026-10-05",hireDate:"2026-10-05"},"uz",true);
      const a1=firmAt(f,"2026-08-01").chiefAccountant, a2=firmAt(f,"2026-10-01").chiefAccountant;
      return {s1:s1[0].n,s2:s2[0].n,c1:h1.includes(f.dirHist.at(-1).director),c1n:h1.includes(f.director),c2:h2.includes(f.director),e1:e1.includes(f.dirHist.at(-1).director),e2:e2.includes(f.director),a1,a2,cur:firm("namuna01").director}; })()''')
    print(json.dumps(r,ensure_ascii=False))
    chk(r["s1"]==old and r["s2"]=="Янгиев Бобур Акмалович","буйруқ имзосида санага мос директор чиқмади")
    chk(r["c1"] and not r["c1n"] and r["c2"],"шартномада санага мос директор чиқмади")
    chk(r["e1"] and r["e2"],"меҳнат шартномасида санага мос директор чиқмади")
    chk(r["a1"]==olda and r["a2"]=="Ҳисобчиева Малика","бош бухгалтер санага қараб алмашмади")
    chk(r["cur"]=="Янгиев Бобур Акмалович","фирма ёзувининг ўзи ўзгариб кетди")
    # Word экспорт (буйруқ): эски санали буйруқда эски директор
    w=G('''(()=>{ const o=S.orders.find(x=>x.firmId==="namuna01"); if(!o) return null; const o2=JSON.parse(JSON.stringify(o)); o2.values.date="2026-03-01"; const h=ordWordHTML(o2); return [h.includes(firm("namuna01").dirHist.at(-1).director), /qrimg|QR-код/.test(h)]; })()''')
    print("word",w); chk(w is None or (w[0] and not w[1]),"буйруқ Word файлида эски директор йўқ ёки QR қолган")
    # 4. Штат: сони билан, такрорсиз, бир йўла бир нечта
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"shtat",posEdit:null})'); pg.wait_for_timeout(500)
    n0=G('firmPos("namuna01").length')
    pg.click('[data-act="newPos"]'); pg.wait_for_timeout(400)
    pg.fill('[data-pr="0|position"]',"Сотувчи"); pg.fill('[data-pr="0|salary"]',"4500000")
    for _ in range(4): pg.click('[data-prstep="0|1"]')
    chk(G('document.querySelector("[data-pr=\\"0|units\\"]").value')=="5" and "22500000" in G('document.querySelector("#prf_0").innerText.replace(/\\s/g,"")'),"−/+ ва ойлик фонд ишламади")
    pg.click('[data-act="prAdd"]'); pg.wait_for_timeout(300)
    pg.fill('[data-pr="1|position"]',"Омборчи"); pg.fill('[data-pr="1|units"]',"2"); pg.fill('[data-pr="1|salary"]',"3000000")
    pg.click('[data-act="prAdd"]'); pg.wait_for_timeout(300)
    pg.fill('[data-pr="2|position"]',"Ҳайдовчи"); pg.fill('[data-pr="2|units"]',"0,5"); pg.fill('[data-pr="2|salary"]',"2000000")
    pg.click('#posForm [type=submit]'); pg.wait_for_timeout(1500)
    P=G('firmPos("namuna01").map(x=>[x.position,x.units,x.salary])'); print(P)
    chk(len(P)==n0+3 and ["Сотувчи","5","4500000"] in P and ["Омборчи","2","3000000"] in P and ["Ҳайдовчи","0.5","2000000"] in P,"бир йўла 3 лавозим сони билан сақланмади")
    # такрор: «сотувчи » 3 та, маош бир хил → бирлаштириш
    pg.click('[data-act="newPos"]'); pg.wait_for_timeout(300)
    pg.fill('[data-pr="0|position"]',"сотувчи "); pg.dispatch_event('[data-pr="0|position"]',"change"); pg.wait_for_timeout(300)
    pg.fill('[data-pr="0|units"]',"3"); pg.fill('[data-pr="0|salary"]',"4500000"); pg.wait_for_timeout(100)
    chk("штат жадвалида бор" in G('document.body.innerText'),"такрор лавозим ҳақида огоҳлантирилмади")
    pg.click('#posForm [type=submit]'); pg.wait_for_timeout(1200)
    P=G('firmPos("namuna01").filter(x=>x.position.toLowerCase().includes("сотувчи")&&x.salary==="4500000").map(x=>[x.position,x.units])'); print(P)
    chk(P==[["Сотувчи","8"]],"бир хил лавозим (маоши ҳам бир хил) бирлаштирилмади (5+3=8)")
    # маош бошқа → «алоҳида қатор» танланса
    pg.click('[data-act="newPos"]'); pg.wait_for_timeout(300)
    pg.fill('[data-pr="0|position"]',"Сотувчи"); pg.dispatch_event('[data-pr="0|position"]',"change"); pg.wait_for_timeout(300)
    pg.fill('[data-pr="0|units"]',"1"); pg.fill('[data-pr="0|salary"]',"6000000")
    pg.select_option('[data-pr="0|dupAct"]',"sep"); pg.click('#posForm [type=submit]'); pg.wait_for_timeout(1200)
    P=G('firmPos("namuna01").filter(x=>x.position==="Сотувчи").map(x=>[x.units,x.salary]).sort()'); print(P)
    chk(["1","6000000"] in P and ["8","4500000"] in P and len(P)==3,"бошқа маошли лавозим алоҳида қатор бўлмади")
    # эски такрорлар → бирлаштириш тугмаси
    G('''(async()=>{ for(const u of ["2","1"]) await putItem("emp",{id:uid(),firmId:"namuna01",type:"pos",dept:"",position:"Фаррош",units:u,salary:"1500000"},false); })()'''); pg.wait_for_timeout(600)
    G('render()'); pg.wait_for_timeout(300)
    chk(G('!!document.querySelector("[data-act=posDedupe]")'),"«Такрорларни бирлаштириш» тугмаси чиқмади")
    pg.click('[data-act="posDedupe"]'); pg.wait_for_timeout(1500)
    P=G('firmPos("namuna01").filter(x=>x.position==="Фаррош").map(x=>x.units)'); chk(P==["3"],"такрорлар бирлаштирилмади: "+str(P))
    # штат буйруғи жадвали
    t=G('staffTableHTML(posSnap("namuna01")).tu'); print("tu",t); chk(t>=14.5,"штат буйруғидаги жами бирлик нотўғри")
    # тахрирлаш (мавжуд лавозим) ишлайди
    pid=G('firmPos("namuna01").find(x=>x.position==="Омборчи").id'); G(f'go({{posEdit:JSON.parse(JSON.stringify(firmPos("namuna01").find(x=>x.id==="{pid}")))}})'); pg.wait_for_timeout(300)
    pg.click('[data-prstep="0|1"]'); pg.click('#posForm [type=submit]'); pg.wait_for_timeout(1000)
    chk(G(f'firmPos("namuna01").find(x=>x.id==="{pid}").units')=="3" and len(G('firmPos("namuna01").filter(x=>x.position==="Омборчи")'))==1,"мавжуд лавозимни таҳрирлаш ишламади")
    for t in ("contracts","overview","bank","staff"):
        G(f'go({{view:"firm",firmId:"namuna01",tab:"{t}",posEdit:null,hrSub:null}})'); pg.wait_for_timeout(500)
        chk(G('document.body.innerText.length')>400,f"«{t}» бўлими бўш")
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=87,f"версия в87 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
