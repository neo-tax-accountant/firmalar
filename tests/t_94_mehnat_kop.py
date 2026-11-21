# в94 — бир йўла 250 тагача меҳнат дафтарчаси кўчирмаси: ўқиш, текшириш жадвали, сақлаш, гуруҳли қабул буйруғи
# Бу муҳитда PDF кутубхонаси (CDN) юкланмаслиги мумкин, шунинг учун mbRead синов маълумоти қайтарадиган қилиб алмаштирилади.
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
def chk(c,msg):
    if not c: errs.append(msg)
with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"staff",hrSub:"list"})'); pg.wait_for_timeout(400); G('ensureEmp()'); pg.wait_for_timeout(500)
    chk(G('document.querySelector("#mbFile")?.multiple')==True,"юклаш тугмаси бир нечта файлни қабул қилмайди")
    # штатга лавозим
    G('(async()=>{ await putItem("emp",{id:"tpos1",firmId:"namuna01",type:"pos",branch:"",dept:"Савдо",position:"Сотувчи",units:"10",salary:"4000000"},"тест"); })()'); pg.wait_for_timeout(600)
    exist=G('(firmEmps("namuna01").find(e=>e.pinfl)||{}).pinfl')
    fname=G('firm("namuna01").name')
    # синов mbRead: файл номидан натижа
    G('''window.__MB_FAKE=(name)=>{ const n=+name.replace(/\\D/g,"")||0; const org=%r;
      if(name.startsWith("bad")) throw new Error("Бу файл my.mehnat.uz меҳнат дафтарчаси кўчирмасига ўхшамайди");
      const pin=name.startsWith("dup")?"30000000000001":name.startsWith("ex")?%r:String(30000000000000+n);
      const fired=name.startsWith("fired");
      return {fio:"Тестов Ходим "+n+" ўғли",pinfl:pin,passport:"AA"+String(1000000+n),birth:"1990-01-01",gender:"эркак",inn:"",docNo:String(n),docDate:"2026-11-01",
        hist:[{from:"2020-01-01",to:"2022-12-31",cur:false,pos:"Бухгалтер",dept:"",org:"Бошқа МЧЖ"},{from:"2025-03-01",to:fired?"2026-05-31":"",cur:!fired,pos:"Сотувчи",dept:"Савдо",org:org}],self:[]}; };
      mbRead=async f=>window.__MB_FAKE(f.name); 0;''' % (fname, exist or "39999999999999"))
    names=[f"x{i}.pdf" for i in range(1,8)]+["dup1.pdf","bad1.pdf","fired9.pdf"]+(["ex1.pdf"] if exist else [])
    G(f'(async()=>{{ const fs={names!r}.map(n=>new File([new Uint8Array([37,80,68,70])],n,{{type:"application/pdf"}})); await mbBulkImport(fs,false); }})()'); pg.wait_for_timeout(2500)
    chk(G('!!V.mbBulk'),"текшириш жадвали очилмади")
    st=G('V.mbBulk.rows.map(r=>r.name+":"+r.status+":"+r.sel)'); print(st)
    chk(any(s.startswith("x1.pdf:new:true") for s in st),"янги ходим белгиланган ҳолатда эмас")
    chk(any(s.startswith("dup1.pdf:dup:false") for s in st),"такрор файл аниқланмади")
    chk(any(s.startswith("bad1.pdf:err:false") for s in st),"хато файл аниқланмади")
    chk(any(s.startswith("fired9.pdf:fired:false") for s in st),"бўшаган ходим белгисиз эмас")
    if exist: chk(any(s.startswith("ex1.pdf:exist:true") for s in st),"бор ходим аниқланмади")
    r=G('V.mbBulk.rows.find(r=>r.name==="x1.pdf")'); print({k:r.get(k) for k in ("fio","pinfl","hireDate","posId","srcPos")})
    chk(r["fio"]=="TESTOV XODIM 1 O‘G‘LI","Ф.И.О. лотинчага ўгирилмади: "+str(r["fio"]))
    chk(r["hireDate"]=="2025-03-01" and G(f'(firmPos("namuna01").find(p=>p.id==="{r["posId"]}")||{{}}).position')=="Сотувчи","қабул санаси ёки штат лавозими топилмади")
    t=G('document.body.innerText')
    chk("Меҳнат дафтарчаларидан ходимлар" in t and "Сақлаш (" in t,"текшириш экрани матни йўқ")
    chk("бўш: " in t,"бўш ставка кўрсатилмади")
    pg.screenshot(path=OUT+'mehnat_kop.png', full_page=False)
    # таҳрир: Ф.И.О. ва ставка
    rid=G('V.mbBulk.rows.find(r=>r.name==="x2.pdf").id')
    pg.fill(f'[data-mbb="{rid}|fio"]',"Каримов Алишер"); pg.dispatch_event(f'[data-mbb="{rid}|fio"]','change'); pg.wait_for_timeout(300)
    chk(G(f'V.mbBulk.rows.find(r=>r.id==="{rid}").fio')=="KARIMOV ALISHER","жадвалдаги Ф.И.О. таҳрири лотинчага ўтмади")
    pg.select_option(f'[data-mbb="{rid}|rate"]',"0,5"); pg.wait_for_timeout(300)
    # сақлаш
    n0=G('S.emp.filter(e=>e.firmId==="namuna01"&&e.type==="emp").length'); o0=G('S.orders.length')
    nsel=G('V.mbBulk.rows.filter(r=>r.sel).length')
    pg.click('[data-act=mbbSave]'); pg.wait_for_timeout(5000)
    n1=G('S.emp.filter(e=>e.firmId==="namuna01"&&e.type==="emp").length')
    print("emp",n0,"->",n1,"sel",nsel)
    chk(n1-n0==7,f"7 та янги ходим қўшилиши керак эди, қўшилди: {n1-n0}")
    e=G('S.emp.find(e=>e.pinfl==="30000000000002")')
    chk(e and e["fio"]=="KARIMOV ALISHER" and e["inps"]=="30000000000002" and e["position"]=="Сотувчи" and e["dept"]=="Савдо" and e["salary"]=="4000000" and e["rate"]=="0,5" and e["hireDate"]=="2025-03-01","ходим маълумотлари нотўғри сақланди: "+str({k:(e or {}).get(k) for k in ("fio","inps","position","dept","salary","rate","hireDate")}))
    chk(e and len(e.get("workHist") or [])==2,"меҳнат фаолияти сақланмади")
    chk(not G('S.emp.some(e=>e.pinfl==="'+str(30000000000000)+'"&&e.status==="fired")'),"")
    chk(not G('S.emp.some(e=>e.fio&&/FIRED/.test(e.fio))'),"")
    o=G('S.orders.filter(o=>o.firmId==="namuna01"&&o.tplId==="k-hire-perm"&&o.values.group==="1").pop()')
    chk(o and o["status"]=="draft","гуруҳли қабул буйруғи черновиги тузилмади")
    if o: chk(len(G(f'grpRows(S.orders.find(x=>x.id==="{o["id"]}").values)'))==7,"буйруқдаги ходимлар сони 7 эмас")
    chk(not G('!!V.mbBulk'),"сақлангандан кейин жадвал ёпилмади")
    # хато файл бўлса огоҳлантириш (bad1 сақланмайди, хатолар рўйхати бўш бўлиши мумкин)
    # 250 чегараси
    G('(async()=>{ const fs=Array.from({length:255},(_,i)=>new File([new Uint8Array([1])],"y"+i+".pdf",{type:"application/pdf"})); await mbBulkImport(fs,false); })()'); pg.wait_for_timeout(9000)
    chk(G('V.mbBulk&&V.mbBulk.rows.length')==250,"250 чегараси ишламади: "+str(G('V.mbBulk&&V.mbBulk.rows.length')))
    G('go({mbBulk:null})')
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=94,f"версия в94 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
