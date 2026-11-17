# в88 — Буйруқ, қарор ва баённомаларни PDF'дан ўқиш; PDF очиқ ойнада
import os, json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
def chk(c,msg):
    if not c: errs.append(msg)
with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    efio=G('firmEmps("namuna01")[0].fio'); print("emp",efio)
    G('go({view:"firm",firmId:"namuna01",tab:"orders"})'); pg.wait_for_timeout(500)
    chk(G('!!document.querySelector("#ordxFiles")'),"«PDF'дан юклаш» тугмаси йўқ")
    # 1. Калитсиз — қўлда тўлдириш
    pg.set_input_files('#ordxFiles',FIX+"sample.pdf"); pg.wait_for_timeout(800)
    chk(G('V.ordImp&&V.ordImp.items.length===1&&V.ordImp.items[0].status==="manual"'),"калитсиз ҳолатда файл қўлда тўлдириш учун очилмади")
    pg.click('[data-oxa="save"]'); pg.wait_for_timeout(300)
    chk(G('V.ordImp!==null'),"рақам/санасиз ҳужжат сақланиб кетди")
    pg.click('[data-oxa="cancel"]'); pg.wait_for_timeout(300)
    # 2. Claude (сохта жавоб): битта PDF'да 2 та ҳужжат
    resp={"id":"m","model":"claude-x","stop_reason":"tool_use","usage":{"input_tokens":300,"output_tokens":200},"content":[{"type":"tool_use","name":"save_corporate_documents","input":{"documents":[
      {"doc_type":"order","number":"15","date":"2026-03-10","subject":"Инвентаризация ўтказиш тўғрисида","summary":"Йиллик инвентаризация ўтказилади.","items":["Комиссия тузилсин","Натижалар 25.03.2026 гача топширилсин"],"signer":"Директор Каримов А.Б.","pages":"1"},
      {"doc_type":"hr_order","number":"7-к","date":"2026-04-01","subject":"Ишга қабул қилиш тўғрисида","employee_name":efio,"employee_position":"Сотувчи","summary":"Ходим ишга қабул қилинди.","items":["01.04.2026 дан ишга қабул қилинсин"],"signer":"Директор","pages":"2"}]}}]}
    G('''(r=>{ localStorage.setItem("fb-claude-v1",JSON.stringify({key:"sk-ant-test",model:aiCfg().model,limit:0})); window.__n=0;
      const _f=window.fetch; window.fetch=function(u,o){ if(!String(u).includes("api.anthropic.com")) return _f.apply(this,arguments); window.__n++; return Promise.resolve({ok:true,status:200,headers:{get:()=>null},json:()=>Promise.resolve(JSON.parse(r))}); }; })('''+json.dumps(json.dumps(resp))+')')
    G('render()'); pg.wait_for_timeout(300)
    pg.set_input_files('#ordxFiles',FIX+"sample.pdf"); pg.wait_for_timeout(2500)
    it=G('V.ordImp.items.map(x=>[x.status,x.sub||0,x.d.dtype,x.d.number,x.d.date,x.d.emp?1:0,x.d.fio])'); print(it)
    chk(len(it)==2 and it[0][:5]==["ok",0,"БУЙРУҚ","Б-15","2026-03-10"],"биринчи ҳужжат нотўғри ўқилди")
    chk(len(it)==2 and it[1][:6]==["ok",2,"КАДР БУЙРУҒИ","КБ-7","2026-04-01",1],"иккинчи (кадр) ҳужжат ёки ходим боғланиши нотўғри")
    # 3. Таҳрирлаш: мавзу ва тур
    pg.fill(f'[data-oxi="{G("V.ordImp.items[0].id")}|subject"]',"Йиллик инвентаризация ўтказиш тўғрисида")
    pg.select_option(f'[data-oxi="{G("V.ordImp.items[0].id")}|dtype"]',"ФАРМОЙИШ"); pg.wait_for_timeout(300)
    chk(G('V.ordImp.items[0].d.subject')=="Йиллик инвентаризация ўтказиш тўғрисида" and G('V.ordImp.items[0].d.number')=="Б-15","таҳрир ёки рақам сериясини янгилаш ишламади")
    pg.click(f'[data-oxa="view"][data-id="{G("V.ordImp.items[0].id")}"]'); pg.wait_for_timeout(1500)
    chk(G('!!document.querySelector(".oxpv canvas.pvpage")'),"текширишда PDF бетлари чизилмади")
    chk(G('!!document.querySelector(".oxpv .pdfview")'),"текширишда PDF кўриниши очилмади")
    n0=G('S.orders.filter(o=>o.firmId==="namuna01").length')
    pg.click('[data-oxa="save"]'); pg.wait_for_timeout(2000)
    U=G('S.orders.filter(o=>o.firmId==="namuna01"&&o.tplId==="upl").map(o=>[o.status,o.values.number,o.values.dtype,o.title,(o.files||[]).length,o.files[0].file.id,ordSeries(o)])'); print(U)
    chk(G('S.orders.filter(o=>o.firmId==="namuna01").length')==n0+2 and G('V.ordImp')==None,"ҳужжатлар сақланмади")
    chk(len(U)==2 and all(x[0]=="signed" and x[4]==1 for x in U) and U[0][5]==U[1][5],"имзоланган ҳолат ёки PDF (битта файл) бириктирилмади")
    chk(sorted(x[6] for x in U)==["Б","КБ"],"серия (Б/КБ) нотўғри")
    # 4. Рақамлаш давом этади
    nx=G('ordNextNo({firmId:"namuna01",tplId:"free",values:{dtype:"БУЙРУҚ",date:"2026-05-01"}})'); print("next",nx)
    chk(nx.startswith("Б-") and int(nx.split("-")[1].split("/")[0])>=16,"янги буйруқ рақами юкланган буйруқдан кейин давом этмади")
    # 5. Рўйхат ва очиш: PDF ўнгда, чоп тугмалари йўқ
    G('go({view:"firm",firmId:"namuna01",tab:"orders"})'); pg.wait_for_timeout(500)
    chk("Йиллик инвентаризация ўтказиш тўғрисида" in G('document.body.innerText') and "Юкланган (PDF)" in G('document.body.innerText'),"рўйхатда юкланган ҳужжат кўринмади")
    oid=G('S.orders.find(o=>o.tplId==="upl"&&o.values.dtype==="ФАРМОЙИШ").id')
    pg.click(f'[data-order="{oid}"]'); pg.wait_for_timeout(1500)
    chk(G('!!document.querySelector(".ordpdf .pdfview")') and G('document.querySelector("#sheetWrap").hidden'),"юкланган ҳужжатда PDF ўнгда очилмади")
    chk(G('!document.querySelector("[data-act=ordWord]")'),"юкланган ҳужжатда Word/чоп тугмалари қолган")
    chk("PDF'дан юкланган ҳужжат" in G('document.body.textContent'),"юкланган ҳужжат белгиси йўқ")
    pg.wait_for_timeout(1500); chk(G('!!document.querySelector(".ordpdf canvas.pvpage")'),"PDF бетлари чизилмади")
    # 6. Қайта ўқиш
    pg.click('[data-oxa="reread"]'); pg.wait_for_timeout(1500)
    chk(G('V.editSigned===V.draft.id&&V.draft.values.number==="Б-15"'),"«PDF'дан қайта ўқиш» ишламади")
    # 7. Шаблон буйруғига скан бириктирилса — вкладкалар
    tid=G('S.orders.find(o=>o.firmId==="namuna01"&&o.tplId!=="upl").id'); ref=G(f'S.orders.find(o=>o.id==="{oid}").files[0].file')
    G(f'attPut("orders","{tid}",o=>{{o.files=(o.files||[]).concat([{{file:{json.dumps(ref)},name:"imzolangan.pdf",at:Date.now()}}]);}},"тест")'); pg.wait_for_timeout(500)
    G(f'go({{view:"order",editSigned:null,draft:JSON.parse(JSON.stringify(S.orders.find(x=>x.id==="{tid}")))}})'); pg.wait_for_timeout(600)
    chk(G('document.querySelectorAll(".ordpane .cttab").length')==2 and not G('document.querySelector("#sheetWrap").hidden'),"шаблон буйруғида «Чоп шакли | Имзоланган нусха» вкладкалари йўқ")
    pg.click('[data-ordpane="pdf"]'); pg.wait_for_timeout(1200)
    chk(G('document.querySelector("#sheetWrap").hidden&&!!document.querySelector(".ordpdf .pdfview")'),"«Имзоланган нусха» вкладкаси PDF'ни очмади")
    pg.click('[data-ordpane="sheet"]'); pg.wait_for_timeout(300)
    chk(not G('document.querySelector("#sheetWrap").hidden'),"«Чоп шакли»га қайтмади")
    # 8. Шаблонлар рўйхатида «Юкланган» йўқ
    G('go({view:"tpl",firmId:"namuna01"})'); pg.wait_for_timeout(400)
    chk(G('!document.querySelector("[data-tpl=upl]")'),"«Юкланган ҳужжат» шаблонлар рўйхатида чиқиб қолган")
    for t in ("contracts","overview","staff","orders"):
        G(f'go({{view:"firm",firmId:"namuna01",tab:"{t}"}})'); pg.wait_for_timeout(500)
        chk(G('document.body.innerText.length')>400,f"«{t}» бўлими бўш")
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=88,f"версия в88 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
