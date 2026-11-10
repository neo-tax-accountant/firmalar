# в83 — Кредитлар: турлар, вкладкалар, қўлда график, PDF оммавий юклаш ва Claude ўқиши
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

AI_BODY = ('{"id":"m","model":"claude-x","usage":{"input_tokens":100,"output_tokens":50},"content":[{"type":"tool_use","name":"save_credit","input":'
  '{"kind":"auto","lender":"Ипотека-банк АТИБ","number":"AK-77/2026","date":"2026-03-10","amount":240000000,"currency":"UZS","rate":24,"term_months":3,'
  '"vehicle":{"mark":"Chevrolet Cobalt","plate":"01 A 777 AA","vin":"XWB123","year":2026},"down_payment":60000000,"insurance_no":"KS-1","insurance_exp":"2027-03-10",'
  '"schedule":[{"date":"2026-04-10","principal":80000000,"interest":4800000,"total":84800000},{"date":"10.05.2026","principal":80000000,"interest":3200000,"total":83200000},'
  '{"date":"2026-06-10","principal":80000000,"interest":1600000,"total":81600000}]}}]}')

with sync_playwright() as p:
    b,pg=page(p,1500,1000)
    fid=pg.evaluate('S.firms[0].id')
    go=lambda: (pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"loans",lnSub:"credits",crId:null,crEdit:null}})'), pg.wait_for_timeout(700))
    go()

    # 1. Реестр: 14 тур, икки йўналиш
    ks=pg.evaluate('CR_TK'); print("turlar",len(ks))
    chk(len(ks)==14,"14 та тур бўлиши керак")
    for k in ("auto","turn","micro","dep","empLoan","founder","goods","escrow"): chk(k in ks,f"«{k}» тури йўқ")
    chk(pg.evaluate('CR_TK.filter(k=>CR_T[k].side==="asset").join()')=="dep,empLoan,escrow","актив турлари нотўғри")
    chk(pg.evaluate('CR_TK.every(k=>CR_T[k].f.every(x=>CR_F[x]))'),"таърифланмаган қўшимча майдон бор")

    # 2. Эски ёзув (kind=матн, tkind йўқ) бузилмайди ва турга кўчади
    pg.evaluate(f'''(async()=>{{ const C={{...crNew(firm("{fid}")),kind:"Авто кредит",bank:"Эски банк",number:"OLD-1",date:"2026-01-15",amount:"120000000",rate:"24",term:"12"}}; delete C.tkind; window.__old=C.id; await putItem("recs",C,"тест"); }})()''')
    pg.wait_for_timeout(500)
    chk(pg.evaluate('crKind(S.recs.find(r=>r.id===window.__old))')=="auto","эски «Авто кредит» ёзуви auto турига кўчмади")
    same=pg.evaluate('(()=>{const C=S.recs.find(r=>r.id===window.__old);const a=crCalc(C),b=crCalcBase(C);return [a.rows.length,Math.round(a.totI),Math.round(b.totI),!!a.manual]})()')
    print("eski hisob",same); chk(same[0]==12 and same[1]==same[2] and not same[3],"эски ёзувнинг ҳисоб-китоби ўзгариб қолди")

    # 3. Шартнома ичида 3 вкладка; файллар маълумот остида
    pg.evaluate('go({crId:window.__old})'); pg.wait_for_timeout(700)
    tabs=pg.evaluate('[...document.querySelectorAll("[data-crtab]")].map(x=>x.textContent.trim().replace(/\\d+$/,""))'); print("vkladkalar",tabs)
    chk(tabs==["Асосий","Сўндириш графиги","Бошқа ҳужжатлар"],"вкладкалар нотўғри: "+str(tabs))
    pos=pg.evaluate('(()=>{const a=document.querySelector(".attbox"),r=document.querySelector(".reqs");return a&&r?a.getBoundingClientRect().top>r.getBoundingClientRect().bottom:null})()')
    chk(pos is True,"«Асосий»да бириктирилган ҳужжатлар маълумотлар остида эмас")
    pg.click('[data-crtab="sched"]'); pg.wait_for_timeout(500)
    chk(pg.evaluate('document.querySelectorAll(".crtab tbody tr").length')==12,"график вкладкасида 12 қатор йўқ")
    pos=pg.evaluate('(()=>{const a=document.querySelector(".attbox"),r=document.querySelector(".crtab");return a.getBoundingClientRect().top>r.getBoundingClientRect().bottom})()')
    chk(pos,"«График»да ҳужжатлар жадвал остида эмас")
    chk(pg.evaluate('document.querySelector(".attbox input[type=file]").dataset.attach').endswith("|sched"),"график вкладкасининг файл майдони белгиланмаган")
    pg.click('[data-crtab="docs"]'); pg.wait_for_timeout(400)
    chk(pg.evaluate('document.querySelector(".attbox input[type=file]").dataset.attach').endswith("|docs"),"ҳужжатлар вкладкасининг файл майдони белгиланмаган")

    # 4. Ҳар вкладкага ўз файли: индекс сақланади
    pg.evaluate('''attPut("recs",window.__old,o=>{o.files=[{file:{id:"a"},name:"shartnoma.pdf"},{file:{id:"b"},name:"garov.pdf",bkt:"docs"},{file:{id:"c"},name:"grafik.pdf",bkt:"sched"}];},"тест")''')
    pg.wait_for_timeout(500); pg.evaluate('render()'); pg.wait_for_timeout(300)
    d=pg.evaluate('[...document.querySelectorAll(".attbox [data-attdel]")].map(x=>x.dataset.attdel.split("|")[2])'); print("docs fayl indeks",d)
    chk(d==["1"],"«Бошқа ҳужжатлар»да фақат ўз файли (индекс 1) чиқиши керак: "+str(d))
    pg.click('[data-crtab="main"]'); pg.wait_for_timeout(400)
    chk(pg.evaluate('[...document.querySelectorAll(".attbox [data-attdel]")].map(x=>x.dataset.attdel.split("|")[2]).join()')=="0","«Асосий»да белгисиз эски файл чиқмади")

    # 5. Қўлда график: таҳрир, қатор қўшиш, сақлаш, формулага қайтиш
    pg.click('[data-crtab="sched"]'); pg.wait_for_timeout(400)
    pg.click('[data-cra="schedEdit"]'); pg.wait_for_timeout(400)
    chk(pg.evaluate('document.querySelectorAll("[data-crs$=\\"|date\\"]").length')==12,"таҳрирда 12 қатор очилмади")
    pg.fill('[data-crs="0|prin"]',"5000000"); pg.fill('[data-crs="0|int"]',"1000000"); pg.wait_for_timeout(200)
    chk(pg.evaluate('document.querySelector("[data-crs=\\"0|pay\\"]").value')=="6000000","жами устун ўзи ҳисобланмади")
    pg.click('[data-cra="schedAdd"]'); pg.wait_for_timeout(300)
    chk(pg.evaluate('V.crSchedEdit.length')==13,"қатор қўшилмади")
    pg.click('[data-cra="schedDel"][data-i="12"]'); pg.wait_for_timeout(300)
    pg.click('[data-cra="schedSave"]'); pg.wait_for_timeout(700)
    m=pg.evaluate('(()=>{const C=S.recs.find(r=>r.id===window.__old);const c=crCalc(C);return [C.schedMode,c.manual,c.rows.length,c.rows[0].prin,c.rows[0].I,c.rows[0].pay]})()'); print("qolda",m)
    chk(m==["manual",True,12,5000000,1000000,6000000],"қўлда график сақланмади: "+str(m))
    chk("қўлда" in pg.evaluate('document.querySelector(".lpill.act")?.textContent||""'),"қўлда режим белгиси йўқ")
    pg.click('[data-cra="schedCalc"]'); pg.wait_for_timeout(700)
    chk(pg.evaluate('(()=>{const C=S.recs.find(r=>r.id===window.__old);return !crCalc(C).manual&&C.sched.length===12})()'),"формулага қайтмади ёки қўлда график ўчиб кетди")

    # 6. Форма: турга мос майдонлар
    go(); pg.click('[data-act="crNew"]'); pg.wait_for_timeout(500)
    chk(pg.evaluate('document.querySelectorAll("#cr_tkind option").length')==14,"турлар рўйхатида 14 та йўқ")
    pg.select_option("#cr_tkind","auto"); pg.wait_for_timeout(400)
    chk(pg.evaluate('!!document.getElementById("cr_x_vhMark")&&!!document.getElementById("cr_x_kaskoExp")'),"авто кредит майдонлари чиқмади")
    pg.select_option("#cr_tkind","dep"); pg.wait_for_timeout(400)
    chk(pg.evaluate('!!document.getElementById("cr_x_depType")&&!document.getElementById("cr_x_vhMark")'),"омонат майдонлари нотўғри")
    chk("Жойлаштирилган" in pg.evaluate('document.querySelector("label[for=cr_amount]").textContent'),"омонатда сумма ёрлиғи ўзгармади")
    pg.fill("#cr_bank","Капиталбанк"); pg.fill("#cr_amount","500000000"); pg.fill("#cr_rate","22"); pg.fill("#cr_term","6")
    pg.select_option("#cr_x_depType","term"); pg.wait_for_timeout(200)
    pg.click('#crForm [type=submit]'); pg.wait_for_timeout(900)
    dep=pg.evaluate('(()=>{const C=S.recs.find(r=>r.type==="credit"&&r.bank==="Капиталбанк");return C?[C.tkind,C.kind,C.x_depType,crAsset(C)]:null})()'); print("omonat",dep)
    chk(dep==["dep","Омонат (депозит)","term",True],"омонат сақланмади: "+str(dep))
    chk("даромад" in pg.evaluate('document.body.innerText'),"омонатда фоиз даромад сифатида кўрсатилмади")
    go()
    st=pg.evaluate('[...document.querySelectorAll(".lstat .k")].map(x=>x.textContent)'); print("statlar",st)
    chk("Мажбурият қолдиғи" in st and "Актив қолдиғи" in st,"рўйхатда мажбурият/актив алоҳида эмас")
    pg.click('[data-cra="side"][data-v="asset"]'); pg.wait_for_timeout(400)
    chk(pg.evaluate('document.querySelectorAll("[data-credit]").length')==1,"«Активлар» фильтри ишламади")
    pg.click('[data-cra="side"][data-v=""]'); pg.wait_for_timeout(300)

    # 7. Claude жавобини майдонларга ўгириш
    pg.evaluate(f'window.__ai={AI_BODY!r}')
    x=pg.evaluate('crFromAi(JSON.parse(window.__ai).content[0].input)'); print("crFromAi",{k:x[k] for k in ("tkind","bank","amount","term","x_vhNo","x_kasko")}, len(x["sched"]))
    chk(x["tkind"]=="auto" and x["x_vhMark"]=="Chevrolet Cobalt" and x["x_kaskoExp"]=="2027-03-10","Claude майдонлари нотўғри ўгирилди")
    chk(len(x["sched"])==3 and x["sched"][1]["date"]=="2026-05-10","график саналари нотўғри (10.05.2026 → 2026-05-10 бўлиши керак)")

    # 8. Оммавий юклаш: чегара 250
    pg.evaluate('''(()=>{ window.__mk=n=>Array.from({length:n},(_,i)=>new File([new Uint8Array([37,80,68,70,45,49])],"kredit_"+(i+1)+".pdf",{type:"application/pdf"})); })()''')
    pg.evaluate('crReadFiles(window.__mk(251))'); pg.wait_for_timeout(400)
    chk(pg.evaluate('!V.crImport'),"251 та файл қабул қилиниб кетди")
    chk(pg.evaluate('LD_MAX')==250,"чегара 250 эмас")

    # 9. Claude'сиз: файллар қўлда тўлдириш учун қабул қилинади
    pg.evaluate('crReadFiles(window.__mk(2))'); pg.wait_for_timeout(600)
    chk(pg.evaluate('V.crImport&&V.crImport.items.every(x=>x.status==="manual")'),"калитсиз режимда файллар қабул қилинмади")
    pg.click('[data-cra="impCancel"]'); pg.wait_for_timeout(300)

    # 10. Claude билан: ўқиш → текшириш → сақлаш (график билан)
    pg.evaluate('''(()=>{ localStorage.setItem("fb-claude-v1",JSON.stringify({key:"sk-ant-test",model:aiCfg().model,limit:0}));
      const _f=window.fetch; window.__n=0; window.fetch=function(u,o){ if(String(u).includes("api.anthropic.com")){ window.__n++; return Promise.resolve({ok:true,status:200,headers:{get:()=>null},json:()=>Promise.resolve(JSON.parse(window.__ai))}); } return _f.apply(this,arguments); }; })()''')
    chk(pg.evaluate('aiOn()'),"тест калити уланмади")
    pg.evaluate('crReadFiles(window.__mk(3))'); pg.wait_for_timeout(2500)
    im=pg.evaluate('V.crImport?V.crImport.items.map(x=>[x.status,x.d.tkind,x.d.bank,(x.d.sched||[]).length,x.d.schedMode]):null'); print("import",im, "| chaqiruv",pg.evaluate('window.__n'))
    chk(im and len(im)==3 and all(r==["ok","auto","Ипотека-банк АТИБ",3,"manual"] for r in im),"Claude ўқиши рўйхатга тушмади")
    chk(pg.evaluate('document.querySelectorAll("[data-cri$=\\"|bank\\"]").length')==3,"текшириш жадвалида таҳрир майдонлари йўқ")
    pg.fill(f'[data-cri="{pg.evaluate("V.crImport.items[0].id")}|number"]',"QOLDA-1"); pg.wait_for_timeout(200)
    n0=pg.evaluate('S.recs.filter(r=>r.type==="credit").length')
    pg.click('[data-cra="impSave"]'); pg.wait_for_timeout(3500)
    sv=pg.evaluate('S.recs.filter(r=>r.type==="credit"&&r.bank==="Ипотека-банк АТИБ").map(C=>[C.number,C.tkind,C.schedMode,(C.files||[]).length,(C.files||[])[0]?.bkt,crCalc(C).rows.length,Math.round(crCalc(C).totI)])'); print("saqlandi",sv)
    chk(len(sv)==3,"3 та шартнома сақланмади: "+str(len(sv)))
    chk(any(r[0]=="QOLDA-1" for r in sv),"текширишда қўлда ўзгартирилган рақам сақланмади")
    chk(all(r[1:]==["auto","manual",1,"main",3,9600000] for r in sv),"сақланган шартномада график ёки файл нотўғри: "+str(sv))
    chk(pg.evaluate('!V.crImport'),"сақлангач импорт рўйхати ёпилмади")

    # 11. Бошқа бўлимлар ва займлар вкладкаси ишлаяпти
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"loans",lnSub:"loans",crId:null}})'); pg.wait_for_timeout(600)
    chk(pg.evaluate('document.body.innerText.length')>400,"Займлар вкладкаси бўш")
    for t in ("fx","overview","contracts"):
        pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"{t}"}})'); pg.wait_for_timeout(600)
        chk(pg.evaluate('document.body.innerText.length')>400,f"«{t}» бўлими бўш")
    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=83,f"версия в83 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
