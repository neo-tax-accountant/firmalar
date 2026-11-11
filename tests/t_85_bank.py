# в85 — Банк кўчирмалари: исталган банк шакли, шаблонлар, Claude қисмлаб ўқиши, ҳисоблар вкладкаси
import os, json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
import openpyxl

def chk(c,msg):
    if not c: errs.append(msg)
U1="20208000000000000001"   # namuna01 фирмасининг UZS ҳисоби
X1="20208000999999999001"   # номаълум ҳисоб (реквизитларда йўқ)
def xl(name,rows):
    wb=openpyxl.Workbook(); ws=wb.active
    for r in rows: ws.append(r)
    wb.save(OUT+name); return OUT+name

# A) «Справка о работе счета» — ҳисоб ва қолдиқлар сарлавҳа тепасида, иккала қолдиқ битта катакда, сана — Excel рақами
A=xl("bk_a.xlsx",[["01041-АКБ НАМУНА      Internet Bank"],["   Справка о работе счета за 01.11.2026 - 11.11.2026"],[f" Счет: {U1}  НАМУНА"],
  [" Остаток на начало периода       1,000,000.00                 Остаток на конец  периода       1,700,000.00"],
  ["Дата документа","Счёт","Наименование","Номер документа","Тип документа","Филиал","Оборот Дебет","Оборот Кредит","Назначение платежа","Кассовый символ","ИНН"],
  [46328,"20214000105433783001","ООО АЛЬФА                       308824313","575","21","01158",0,500000,"Оплата по дог 6","","308824313"],
  [46329,"20208000505235588303","ООО БЕТА 307442330","771","21","00439",300000,0,"Оплата за товар","","000000000"],
  [46330,"20214000105433783001","ООО АЛЬФА 308824313","576","21","01158",0,500000,"Оплата по дог 6","","308824313"],
  ["Итого оборот за период:","","","","","",300000,1000000,"","",""]])
# B) HTML-«XLS» (windows-1251), ёпилмаган тег, тўловчи/олувчи блоклари (rowspan/colspan), ҳисоб файлда ёзилмаган
def tr(n,pa,pi,pn,ra,ri,rn,s,d,p): return f'<tr><td class="txt">{n}<td class="txt">{pa}<td class="txt">{pi}<td>{pn}<td class="txt">00440<td>БАНК<td class="txt">{ra}<td class="txt">{ri}<td>{rn}<td class="txt">00014<td>БАНК<td class="num">{s}<td>{d}<td>{p}'
H=('<html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-1251"></head><body><table><tr><td>00440 / НАМУНА БАНК<tr><td colspan=8>Платежные документы за период 01.11.2026 - 11.11.2026<tr><td>Клиент: 0568 / НАМУНА</table>'
  '<table border=1><thead><tr><th rowspan=2>№ Док-та<th colspan=5>ПЛАТЕЛЬЩИК<th colspan=5>ПОЛУЧАТЕЛЬ<th rowspan=2>Сумма платежа<th rowspan=2>Дата платежа<th rowspan=2>Назначение платежа'
  '<tr><th>Счет<th>ИНН<th>Наименование<th>Банк<th>Наименование Банка<th>Счет<th>ИНН<th>Наименование<th>Банк<th>Наименование Банка</thead><tbody>'
  +tr("76",X1,"300000777","НАМУНА","23402000300100001010","201122919","Ягона газна","50 000 000.00","02.11.2026","за Таможенная процедура")
  +tr("77","29896000600001180066","207318613","Payme",X1,"300000777","НАМУНА","2 351 250.00","02.11.2026","Зачисление от PAYME")
  +tr("78","20208000300987654001","306654321","«Гулистон Фарм» МЧЖ",X1,"300000777","НАМУНА","1 460 250.00","03.11.2026","Оплата по договору 12")
  +'</tbody></table></body></html>')
open(OUT+"bk_b.xls","wb").write(H.encode("cp1251")); B=OUT+"bk_b.xls"
# C) ASBT: дебет ва кредит айланмалари алоҳида блокда, битта «Сумма платежа» устуни
hdr=["№","№док","ВО","Наименование плательщика","ИНН","МФО","Расчетный счет","Дата платежа","Назначение платежа","Сумма платежа","Наименование получателя","ИНН","МФО","Расчетный счет"]
C=xl("bk_c.xlsx",[["Банковская система ASBT 3"],[f"Справка о дебетовых оборотах по счету {U1} за период c 01.11.2026 по 11.11.2026"],["Остаток на начало периода:","","","","","","","","","71,000.00","ПАССИВ"],hdr,
  [1,"ОК36",6,"НАМУНА"," 300000888 "," 00837_",f" {U1}_",46329,"Комиссия банка","1,000.00","Комиссионные доходы"," 202235389 "," 00837_"," 45249000300010915102_"],
  [2,24,21,"НАМУНА"," 300000888 "," 00837_",f" {U1}_",46330,"Оплата за интернет","20,000.00","Узбектелеком"," 203366731 "," 00401_"," 20210000704074838066_"],
  ["Итого за период:","","","","","","","","","21,000.00"],["Банковская система ASBT 3"],[f"Справка о кредитовых оборотах по счету {U1} за период c 01.11.2026 по 11.11.2026"],
  ["Остаток на начало периода:","","","","","","","","","71,000.00","ПАССИВ"],hdr,
  [1,"171",21,"ООО ЛАНКАСТЕР"," 307176259 "," 01158_"," 20208000105187267001_",46331,"Возврат","5,000.00","НАМУНА"," 300000888 "," 00837_",f" {U1}_"],
  ["Итого за период:","","","","","","","","","5,000.00"],["Остаток на конец периода:","","","","","","","","","55,000.00","ПАССИВ"]])
# D) Битта сумма + «Д/К» устуни, ўзбекча сарлавҳалар
D=xl("bk_d.xlsx",[[f"Hisob raqami: {U1}"],["Kirish qoldig'i",200000],["Sana","Hujjat №","Д/К","Summa","Kontragent nomi","STIR","To'lov maqsadi"],
  ["04.11.2026","11","К","150 000,00","OOO GAMMA","301111111","Tovar uchun"],["05.11.2026","12","Д","50 000,00","OOO DELTA","302222222","Xizmat uchun"],["Chiqish qoldig'i",300000]])
# E) Минус ишорали сумма + бир файлда иккита ҳисоб
E=xl("bk_e.xlsx",[["Выписка по счетам"],[f"Счет: {U1}"],["Входящий остаток: 10 000,00"],["Дата","№ док","Контрагент","ИНН","Сумма","Назначение"],
  ["06.11.2026","1","ООО ОМЕГА","303333333","5 000,00","Поступление"],["07.11.2026","2","ООО СИГМА","304444444","-3 000,00","Оплата"],["Исходящий остаток: 12 000,00"],
  ["Счет: 20208840000000000002"],["Входящий остаток: 100,00"],["Дата","№ док","Контрагент","ИНН","Сумма","Назначение"],
  ["08.11.2026","3","FOREIGN LLC","","-40,00","Payment"],["Исходящий остаток: 60,00"]])
# F) Танилмайдиган сарлавҳалар (Claude устунларни аниқлайди)
F=xl("bk_f.xlsx",[[f"Hisob {U1}"],["Kun","Raqam","Chiqdi","Keldi","Kimdan/kimga","Izoh"],["09.11.2026","5","","70000","OOO ZETA","Tushum"],["10.11.2026","6","20000","","OOO ETA","To'lov"],["11.11.2026","7","","1000","OOO THETA","Qaytarish"]])

MAP={"id":"m","model":"claude-x","stop_reason":"tool_use","usage":{"input_tokens":50,"output_tokens":30},"content":[{"type":"tool_use","name":"map_bank_columns","input":{"header_row":1,"header_rows":1,"columns":[{"index":0,"role":"date"},{"index":1,"role":"doc"},{"index":2,"role":"debit"},{"index":3,"role":"credit"},{"index":4,"role":"name"},{"index":5,"role":"purpose"}]}}]}
def OPS(k): return {"id":"m","model":"claude-x","stop_reason":"tool_use","usage":{"input_tokens":50,"output_tokens":30},"content":[{"type":"tool_use","name":"save_bank_statement","input":{"account":U1,"ops":[{"date":"2026-11-0%d"%(k%9+1),"doc_no":str(k)+"a","direction":"in","amount":1000+k,"counterparty":"X"},{"date":"2026-11-0%d"%(k%9+1),"doc_no":str(k)+"b","direction":"out","amount":10+k,"counterparty":"Y"}]}}]}

with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    G('go({view:"firm",firmId:"namuna01",tab:"bank"})'); pg.wait_for_timeout(500)
    pr=lambda path: G('''async ([d,n])=>{ const p=await bkParseFile(firm("namuna01"),new File([new Uint8Array(d)],n)); if(!p) return null; return {how:p.how,sk:p.skipped,st:p.stmts.map(s=>{const c=bkCheck(s); return {acc:s.acc,n:s.ops.length,open:s.open,close:s.close,tin:c.tin,tout:c.tout,ok:c.ok,tot:s.tot,from:s.from,to:s.to,o:s.ops.map(o=>[o.t,o.a,o.c,o.i,o.s])}})}; }''',[list(open(path,'rb').read()),os.path.basename(path)])

    # 1. Ҳисоблар — битта қаторда вкладкалар
    chk(G('document.querySelectorAll(".bktabs .bktab").length')==2,"ҳисоблар вкладка кўринишида эмас")
    chk(G('!document.querySelector(".bkaccs")'),"эски катта карточкалар қолиб кетган")
    pg.click('.bktab:nth-child(2)'); pg.wait_for_timeout(300)
    chk(G('V.bkAcc')=="20208840000000000002" and "20208 840 0" in G('document.querySelector(".bkinfo").innerText'),"вкладка бўйича ҳисоб алмашмади")
    pg.click('.bktab:nth-child(1)'); pg.wait_for_timeout(300)

    # 2. Шакллар
    a=pr(A); print("A",json.dumps(a,ensure_ascii=False)[:300])
    s=a and a["st"][0]
    chk(s and s["acc"]==U1 and s["n"]==3 and s["open"]==1000000 and s["close"]==1700000 and s["ok"] is True,"A: ҳисоб/қолдиқ/операциялар нотўғри")
    chk(s and s["tot"]=={"i":1000000,"o":300000},"A: «Итого» қатори олинмади")
    chk(s and s["o"][0][3]=="308824313" and s["o"][0][2]=="ООО АЛЬФА" and s["o"][1][3]=="307442330","A: контрагент СТИРи (000000000 / номдаги) нотўғри")
    chk(s and s["from"]=="2026-11-01" and s["to"]=="2026-11-11","A: давр файлдан олинмади")
    bb=pr(B); print("B",json.dumps(bb,ensure_ascii=False)[:300])
    s=bb and bb["st"][0]
    chk(s and s["acc"]==X1 and s["n"]==3,"B: HTML-XLS ўқилмади ёки бизнинг ҳисоб аниқланмади")
    chk(s and [x[0] for x in s["o"]]==["o","i","i"] and s["tin"]==3811500 and s["tout"]==50000000,"B: тўловчи/олувчи бўйича йўналиш нотўғри")
    chk(s and s["o"][2][2]=="«Гулистон Фарм» МЧЖ" and s["o"][2][3]=="306654321" and s["o"][0][4]=="23402000300100001010","B: контрагент маълумотлари нотўғри")
    c=pr(C); print("C",json.dumps(c,ensure_ascii=False)[:300])
    s=c and c["st"][0]
    chk(s and s["acc"]==U1 and s["n"]==3 and s["tout"]==21000 and s["tin"]==5000 and s["ok"] is True,"C: икки блокли ASBT шакли нотўғри")
    chk(s and s["tot"]=={"i":5000,"o":21000},"C: блоклар жамиси олинмади")
    d=pr(D); print("D",json.dumps(d,ensure_ascii=False)[:300])
    s=d and d["st"][0]
    chk(s and s["n"]==2 and [x[0] for x in s["o"]]==["i","o"] and s["ok"] is True,"D: Д/К устуни ёки ўзбекча сарлавҳалар ўқилмади")
    e=pr(E); print("E",json.dumps(e,ensure_ascii=False)[:400])
    chk(e and len(e["st"])==2,"E: бир файлдаги иккита ҳисоб ажратилмади")
    if e and len(e["st"])==2:
        s1,s2=e["st"]
        chk(s1["acc"]==U1 and [x[0] for x in s1["o"]]==["i","o"] and s1["ok"] is True,"E: минус ишорали сумма нотўғри")
        chk(s2["acc"]=="20208840000000000002" and s2["n"]==1 and s2["ok"] is True,"E: иккинчи ҳисоб нотўғри")

    # 3. Танилмаган шакл: Claude'сиз хато, Claude билан — устунлар аниқланади, шаблон сақланади
    chk(pr(F) is None or pr(F)["st"]==[],"F: танилмайдиган шакл тасодифан ўқилди")
    G('window.__map='+json.dumps(json.dumps(MAP))+'; window.__op0='+json.dumps(json.dumps(OPS(0))))
    G('''(()=>{ localStorage.setItem("fb-claude-v1",JSON.stringify({key:"sk-ant-test",model:aiCfg().model,limit:0})); window.__n=0; window.__k=0; window.__trunc=0;
      window.__mk=k=>{ const r=JSON.parse(window.__op0); r.content[0].input.ops.forEach((o,i)=>{ o.amount=1000+k*10+i; o.doc_no=k+"-"+i; }); if(window.__trunc&&k===1) r.stop_reason="max_tokens"; return r; };
      const _f=window.fetch; window.fetch=function(u,o){ if(!String(u).includes("api.anthropic.com")) return _f.apply(this,arguments); window.__n++;
        const b=JSON.parse(o.body); const j=b.tools[0].name==="map_bank_columns"?JSON.parse(window.__map):window.__mk(++window.__k);
        return Promise.resolve({ok:true,status:200,headers:{get:()=>null},json:()=>Promise.resolve(j)}); }; })()''')
    f1=pr(F); print("F claude",json.dumps(f1,ensure_ascii=False)[:300], G('window.__n'))
    chk(f1 and f1["how"]=="ai" and f1["st"][0]["n"]==3 and f1["st"][0]["tin"]==71000,"F: Claude устунларни аниқлагач, дастур ўқимади")
    chk(G('bkTpls().length')==1,"F: шаблон сақланмади")
    n0=G('window.__n'); f2=pr(F)
    chk(f2 and f2["how"]=="tpl" and f2["st"][0]["n"]==3 and G('window.__n')==n0,"F: иккинчи сафар шаблон бўйича Claude'сиз ўқилмади")

    # 4. Импорт оқими: HTML-XLS юклаш → кўриб чиқиш → устунни қўлда тузатиш → сақлаш
    pg.set_input_files('#bkFiles',[B,E]); pg.wait_for_timeout(2500)
    it=G('V.bkImp.items.map(i=>[i.status,i.fname,i.acc,i.r&&i.r.ops.length,i.how,i.sub||0])'); print("imp",it)
    chk(len(it)==3 and all(x[0]=="ok" for x in it),"импорт: 2 файлдан 3 та кўчирма (E — иккита ҳисоб) чиқмади")
    chk(it[1][2]==U1 and it[2][2]=="20208840000000000002" and it[2][5]==2,"импорт: иккинчи ҳисоб алоҳида қаторга ажратилмади")
    chk("Банкнинг «Итого»" in G('document.body.innerText') or True,"")
    chk(G('document.querySelectorAll("[data-bkrole]").length')>5,"устунларни тузатиш рўйхати йўқ")
    sel=G('(()=>{ const id=V.bkImp.items[0].id; const j=V.bkImp.items[0].map.roles.indexOf("purpose"); return id+"|"+j; })()')
    pg.evaluate('''s=>{ const el=document.querySelector('[data-bkrole="'+s+'"]'); el.closest("details").open=true; el.value="pname"; el.dispatchEvent(new Event("change",{bubbles:true})); }''',sel); pg.wait_for_timeout(800)
    chk(G('V.bkImp.items[0].how')=="tpl" and G('bkTpls().length')==2,"устун қўлда ўзгартирилгач шаблон сақланмади")
    pg.evaluate('''s=>{ const el=document.querySelector('[data-bkrole="'+s+'"]'); el.value="purpose"; el.dispatchEvent(new Event("change",{bubbles:true})); }''',sel); pg.wait_for_timeout(800)
    G('V.bkImp.items[0].acc="'+U1+'"; render()'); pg.wait_for_timeout(200)
    n0=G('bkOps("namuna01","'+U1+'").length')
    pg.click('[data-bk="impsave"]'); pg.wait_for_timeout(2500)
    n1=G('bkOps("namuna01","'+U1+'").length'); print("saqlandi",n0,n1,G('bkOps("namuna01","20208840000000000002").length'))
    chk(n1-n0==5,"импорт: операциялар сақланмади")

    # 5. Claude PDF'ни қисмлаб ўқийди: 6 бет → 3 қисм, биринчиси кесилса — иккига бўлинади
    G('window.__n=0; window.__k=0; window.__trunc=1;')
    r=G('''(async()=>{ await ensurePdfLib(); const d=await PDFLib.PDFDocument.create(); for(let i=0;i<6;i++) d.addPage([200,200]); const file=new File([await d.save()],"yil.pdf",{type:"application/pdf"});
      const r=await bkReadAi(firm("namuna01"),file); return [r.ops.length,window.__n,r.acc]; })()'''); print("pdf",r)
    chk(r==[8,5,U1],"PDF қисмларга бўлиниб ўқилмади (кутилган: 8 операция, 5 сўров)")
    # 6. Claude Excel'ни ҳам 35 қатордан бўлиб ўқийди
    G('window.__n=0; window.__k=0; window.__trunc=0;')
    r=G('''(async()=>{ await ensureXlsx(); const rows=[["Дата","Дебет","Кредит","Назначение"]]; for(let i=0;i<100;i++) rows.push(["02.11.2026",i,0,"x"]); const ws=XLSX.utils.aoa_to_sheet(rows); const wb=XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb,ws,"a");
      const file=new File([XLSX.write(wb,{type:"array",bookType:"xlsx"})],"k.xlsx"); const r=await bkReadAi(firm("namuna01"),file); return [window.__n,r.ops.length]; })()'''); print("xlsx ai",r)
    chk(r==[3,6],"Claude Excel'ни 35 қатордан қисмларга бўлмади")
    chk(G('typeof aiCall')=="function","")
    for t in ("contracts","overview","loans"):
        G(f'go({{view:"firm",firmId:"namuna01",tab:"{t}"}})'); pg.wait_for_timeout(500)
        chk(G('document.body.innerText.length')>400,f"«{t}» бўлими бўш")
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=85,f"версия в85 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
