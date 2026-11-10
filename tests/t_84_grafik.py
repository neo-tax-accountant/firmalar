# в84 — Кредит графиги: Excel/PDF файлдан ўқиш, ҳужжатларни очиқ кўрсатиш, иш кунига ўтказиш
import os, datetime as dt, json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
import openpyxl

def chk(c,msg):
    if not c: errs.append(msg)

# --- синтетик банк графиги (ҳақиқий фирма маълумоти эмас): 300 млн, 12 ой, 24%, пул берилган куни 100 млн тўлов
def bank_rows():
    P0=400_000_000; P=300_000_000; r=.24; i=r/12; n=12; A=P*i/(1-(1+i)**-n); bal=P; prev=dt.date(2025,3,3)
    out=[(prev,P0-P,0.0)]
    for k in range(1,n+1):
        y,m=2025+(3+k-1)//12,(3+k-1)%12+1; d=dt.date(y,m,2)
        while d.weekday()>=5: d+=dt.timedelta(1)
        I=round(bal*r*(d-prev).days/365,2); pr=round(bal if k==n else A-I,2); bal=round(bal-pr,2); out.append((d,pr,I)); prev=d
    return out,round(A,2)
ROWS,ANN=bank_rows()
TP=sum(x[1] for x in ROWS); TI=sum(x[2] for x in ROWS)

# A) ўзбекча сарлавҳали Excel (Date ячейкалар, жами қатори йўқ)
xa=OUT+"grafik_uz.xlsx"; wb=openpyxl.Workbook(); ws=wb.active; ws.title="Тулов_графиги"
ws.append(["№","Фирма","Шартнома №","Тўлов санаси","Асосий қарз қолдиғи","Кредит олинди (ўзлаштириш)","Асосий қарз тўлови","Фоиз тўлови","Жами тўлов"])
bal=400_000_000
for k,(d,pr,it) in enumerate(ROWS):
    bal-=pr; ws.append([k+1,"НАМУНА","1/К",dt.datetime(d.year,d.month,d.day),round(bal,2),400_000_000 if k==0 else 0,pr,it,round(pr+it,2)])
ws2=wb.create_sheet("Шартнома"); ws2.append(["Кўрсаткич","Қиймат"]); ws2.append(["Сумма",400000000])
wb.save(xa)
# B) банк шаклидаги Excel: тепада реквизитлар, икки қаторли сарлавҳа, матн кўринишидаги сана ва сумма, пастда жами
xb=OUT+"grafik_bank.xlsx"; wb=openpyxl.Workbook(); ws=wb.active
ws.append(["Наименование: НАМУНА"]); ws.append(["Сумма договора: 400 000 000,00"]); ws.append([])
ws.append(["","Прогнозный остаток ссудной","График освоения -","График погашения -","График погашения %% - Проценты по","Итого по"])
ws.append(["","задолженности","Основной долг","Основной долг","срочной задолженности","кредиту"])
fm=lambda v:f"{v:,.2f}".replace(","," ").replace(".",",")
bal=400_000_000
for k,(d,pr,it) in enumerate(ROWS):
    bal-=pr; ws.append([d.strftime("%d.%m.%Y"),fm(bal),fm(400_000_000 if k==0 else 0),fm(pr),fm(it),fm(pr+it)])
ws.append(["","","400 000 000,00",fm(TP),fm(TI),fm(TP+TI)])
wb.save(xb)

AI = {"id":"m","model":"claude-x","usage":{"input_tokens":100,"output_tokens":50},"content":[{"type":"tool_use","name":"save_credit","input":
  {"kind":"auto","lender":"Банк","schedule":[{"date":d.strftime("%d.%m.%Y"),"principal":pr,"interest":it,"total":round(pr+it,2)} for d,pr,it in ROWS],
   "schedule_totals":{"principal":TP,"interest":round(TI,2),"total":round(TP+TI,2)}}}]}

with sync_playwright() as p:
    b,pg=page(p,1500,1000)
    fid=pg.evaluate('S.firms[0].id')

    # 1. Иш кунига ўтказиш
    chk(pg.evaluate('crBizShift("2023-04-02")')=="2023-04-03","якшанба → душанба ўтмади")
    chk(pg.evaluate('crBizShift("2023-09-02")')=="2023-09-04","шанба → душанба ўтмади")
    chk(pg.evaluate('crBizShift("2023-03-02")')=="2023-03-02","иш куни ўзгариб кетди")
    chk(pg.evaluate(f'crNew(firm("{fid}")).bizDay')=="1","янги шартномада иш кунига ўтказиш ёқилмаган")

    # 2. Формула: пул берилган кундаги тўлов + иш кунлари → банк саналари ва ойлик тўлови
    C0=json.dumps({"bank":"Формула","number":"F-1","date":"2025-03-03","amount":"400000000","rate":"24","term":"12","firstPay":"2025-04-02","bizDay":"1",
        "prepays":[{"date":"2025-03-03","sum":"100000000","mode":"pay"}]})
    pg.evaluate(f'(async()=>{{ const C={{...crNew(firm("{fid}")),...{C0}}}; window.__f=C.id; await putItem("recs",C,"тест"); }})()'); pg.wait_for_timeout(500)
    r=pg.evaluate('(()=>{const c=crCalc(S.recs.find(x=>x.id===window.__f)); return {pay0:c.pay0,dates:c.rows.filter(x=>!x.pre).map(x=>x.date),pre:c.rows.filter(x=>x.pre).length}})()')
    print("formula",round(r["pay0"],2),ANN,r["pre"])
    chk(abs(r["pay0"]-ANN)<0.01,f"ойлик тўлов банкдагидан фарқ қилди: {r['pay0']} ≠ {ANN}")
    chk(r["pre"]==1,"пул берилган кундаги тўлов ҳисобга олинмади")
    chk(r["dates"]==[x[0].isoformat() for x in ROWS[1:]],"тўлов саналари банк графигига мос эмас: "+str(r["dates"][:4]))
    old=pg.evaluate(f'(()=>{{const C={{...crNew(firm("{fid}")),date:"2025-03-03",amount:"1000000",rate:"20",term:"6",firstPay:"2025-04-02"}}; delete C.bizDay; return crCalc(C).rows.map(x=>x.date)}})()')
    chk("2025-08-02" in old,"эски ёзувда (bizDay йўқ) саналар ўзгариб қолди")

    # 3. Форма: белги бор
    pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"loans",lnSub:"credits",crId:null,crEdit:crNew(firm("{fid}"))}})'); pg.wait_for_timeout(600)
    chk(pg.evaluate('!!document.querySelector("#cr_bizDay")&&document.querySelector("#cr_bizDay").value==="1"'),"формада «дам олиш куни» танлови йўқ")
    pg.evaluate('go({crEdit:null,crId:window.__f})'); pg.wait_for_timeout(600)

    # 4. Excel (ўзбекча) — график вкладкасига юклаш → ўзи ўқийди → текшириш → сақлаш
    pg.click('[data-crtab="sched"]'); pg.wait_for_timeout(400)
    pg.set_input_files('.attbox input[data-attach$="|sched"]',xa); pg.wait_for_timeout(3500)
    ed=pg.evaluate('V.crSchedEdit?[V.crSchedEdit.length,V.crSchedAi,V.crSchedEdit.reduce((s,x)=>s+numL(x.prin),0),V.crSchedEdit.reduce((s,x)=>s+numL(x.int),0)]:null'); print("excel uz",ed)
    chk(ed and ed[0]==13 and ed[1]=="excel","Excel юклангач график ўзи ўқилмади")
    chk(ed and abs(ed[2]-TP)<0.05 and abs(ed[3]-TI)<0.05,"Excel'дан ўқилган суммалар нотўғри")
    chk(pg.evaluate('document.querySelectorAll("[data-crs$=\\"|date\\"]").length')==13,"текшириш жадвалида 13 қатор йўқ")
    pg.click('[data-cra="schedSave"]'); pg.wait_for_timeout(800)
    c=pg.evaluate('(()=>{const C=S.recs.find(x=>x.id===window.__f), c=crCalc(C); return [C.schedMode,c.rows.length,c.totPrin,c.totI,c.rows[c.rows.length-1].bal]})()'); print("saqlandi",c)
    chk(c[0]=="manual" and c[1]==13 and abs(c[2]-TP)<0.05 and abs(c[3]-TI)<0.05 and c[4]<0.05,"сақланган график банк графигига тенг эмас")

    # 5. Ҳужжат очиқ кўринади: Excel жадвал бўлиб, маълумотлар остида
    pg.wait_for_timeout(1500)
    pv=pg.evaluate('(()=>{const v=document.querySelector(".attbox .pdfview"), t=document.querySelector(".crtab"); return v?[!!v.querySelector(".xlsprev table"), v.getBoundingClientRect().top>t.getBoundingClientRect().bottom, v.innerText.includes("Тўлов санаси")]:null})()')
    print("prevyu",pv); chk(pv==[True,True,True],"Excel файл дастур ичида очиқ кўринмади ёки маълумотлар остида эмас")

    # 6. Банк шаклидаги Excel (икки қаторли сарлавҳа, матн сана/сумма, жами қатори) — тугма орқали
    pg.evaluate('attPut("recs",window.__f,o=>{o.files=[];o.schedMode="calc";},"тест")'); pg.wait_for_timeout(500)
    pg.set_input_files('.attbox input[data-attach$="|sched"]',xb); pg.wait_for_timeout(3500)
    ed=pg.evaluate('V.crSchedEdit?[V.crSchedEdit.length,V.crSchedEdit[0].date,V.crSchedEdit[1].date,numL(V.crSchedEdit[1].pay),V.crSchedChk]:null'); print("excel bank",ed)
    chk(ed and ed[0]==13 and ed[1]=="2025-03-03" and ed[2]==ROWS[1][0].isoformat(),"банк шаклидаги Excel тўғри ўқилмади")
    chk(ed and abs(ed[3]-round(ROWS[1][1]+ROWS[1][2],2))<0.01,"биринчи тўлов суммаси нотўғри")
    chk(ed and ed[4] and abs(ed[4]["prin"]-TP)<0.05,"файлдаги жами қатор топилмади")
    chk("Барча қаторлар файлдаги жами билан тенг" in pg.evaluate('document.body.innerText'),"жами билан солиштириш кўрсатилмади")
    pg.click('[data-cra="schedCancel"]'); pg.wait_for_timeout(300)
    pg.click('[data-cra="schedAi"]'); pg.wait_for_timeout(2500)
    chk(pg.evaluate('V.crSchedEdit&&V.crSchedEdit.length')==13,"«Файлдан ўқиш» тугмаси Excel'ни ўқимади (калитсиз)")
    pg.click('[data-cra="schedCancel"]'); pg.wait_for_timeout(300)

    # 7. PDF — Claude (сохта жавоб), жами билан солиштириш
    pg.evaluate('window.__ai='+json.dumps(json.dumps(AI)))
    pg.evaluate('''(()=>{ localStorage.setItem("fb-claude-v1",JSON.stringify({key:"sk-ant-test",model:aiCfg().model,limit:0}));
      const _f=window.fetch; window.__n=0; window.fetch=function(u,o){ if(String(u).includes("api.anthropic.com")){ window.__n++; return Promise.resolve({ok:true,status:200,headers:{get:()=>null},json:()=>Promise.resolve(JSON.parse(window.__ai))}); } return _f.apply(this,arguments); }; })()''')
    pg.evaluate('attPut("recs",window.__f,o=>{o.files=[];},"тест")'); pg.wait_for_timeout(500)
    pg.set_input_files('.attbox input[data-attach$="|sched"]',FIX+"sample.pdf"); pg.wait_for_timeout(4000)
    ed=pg.evaluate('V.crSchedEdit?[V.crSchedEdit.length,V.crSchedAi,!!V.crSchedChk,window.__n]:null'); print("pdf claude",ed)
    chk(ed and ed[0]==13 and ed[1]=="claude" and ed[2] and ed[3]>=1,"PDF юклангач Claude графикни ўқимади")
    chk("Claude PDF'дан 13 та қатор ўқилди" in pg.evaluate('document.body.innerText'),"Claude манбаси кўрсатилмади")
    pg.click('[data-cra="schedCancel"]'); pg.wait_for_timeout(1500)
    chk(pg.evaluate('!!document.querySelector(".attbox .pdfview canvas.pvpage")'),"PDF дастур ичида очиқ кўринмади")

    # 8. Бошқа вкладкаларда ҳам очиқ кўриниш
    pg.evaluate('attPut("recs",window.__f,o=>{o.files.push({file:o.files[0].file,name:"garov.pdf",bkt:"docs"});},"тест")'); pg.wait_for_timeout(500)
    pg.click('[data-crtab="docs"]'); pg.wait_for_timeout(1500)
    chk(pg.evaluate('document.querySelectorAll(".attbox .pdfview").length')==1,"«Бошқа ҳужжатлар»да файл очиқ кўринмади")

    # 9. Шартномалар бўлими ва бошқалар бузилмади
    for t in ("contracts","overview","fx"):
        pg.evaluate(f'go({{view:"firm",firmId:"{fid}",tab:"{t}",crId:null}})'); pg.wait_for_timeout(600)
        chk(pg.evaluate('document.body.innerText.length')>400,f"«{t}» бўлими бўш")
    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=84,f"версия в84 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
