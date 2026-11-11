# в86 — Тушумларни шартномага тез боғлаш: кенгайтирилган автомат, гуруҳлаб танлаш, эслаб қолиш, Claude таклифи
import os, json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
def chk(c,msg):
    if not c: errs.append(msg)
U1="20208000000000000001"
with sync_playwright() as p:
    b,pg=page(p,1500,1000); G=pg.evaluate
    pg.on('dialog', lambda d: d.accept())
    own=G('firm("namuna01").inn')
    # шартномалар: бир контрагентда иккита амалдаги шартнома (A-1, A-2), бошқасида ҳам иккита (B-1, B-2); ҳ/ф № 77 → «12» шартномага
    G('''(async()=>{ const mk=(id,no,inn,nm)=>({id,firmId:"namuna01",type:"contract",dir:"out",number:no,date:"2026-01-10",endDate:"2026-12-31",status:"open",subject:"хизмат",cp:{name:nm,inn}});
      for(const c of [mk("tA1","A-1","309999999","«Альфа» МЧЖ"),mk("tA2","A-2","309999999","«Альфа» МЧЖ"),mk("tB1","B-1","307777777","«Бета» МЧЖ"),mk("tB2","B-2","307777777","«Бета» МЧЖ")]) await putItem("recs",c,false);
      const k2=S.recs.find(x=>x.id==="namunact2"); await putItem("recs",{id:"tsf77",type:"sf",firmId:"namuna01",dir:"out",no:"77",date:"2026-10-20",contract:{no:k2.number,date:k2.date},sum:"1000000",buyer:k2.cp,seller:{name:firm("namuna01").name,inn:firm("namuna01").inn}},false); })()''')
    pg.wait_for_timeout(600)
    ops=[["2026-11-02","1","«Гамма» МЧЖ","301010101","20208000100000000011","Оплата по договору № 12 от 01.11.2025 за услуги"],
         ["2026-11-03","2","","","20208000100000000012","Оплата по с/ф № 77 от 20.10.2026"],
         ["2026-11-03","3","НАМУНА",own,"23120000000000000001","Пополнение счета собственными средствами"],
         ["2026-11-04","4","Транзитный счёт для рассчёта с коммерсантами (Payme)","207318613","29896000600001180066","Зачисление от PAYME"],
         ["2026-11-05","5","«Альфа» МЧЖ","309999999","20208000100000000013","Оплата за услуги"],
         ["2026-11-06","6","«Альфа» МЧЖ","309999999","20208000100000000013","Оплата за услуги октябрь"],
         ["2026-11-07","7","«Бета» МЧЖ","307777777","20208000100000000014","Оплата"]]
    G('''(async O=>{ const L=O.map(([d,n,c,i,s,p],j)=>{ const o={d,n,t:"i",a:1000000*(j+1),c,i,s,m:"00444",p}; o.k=bkKey(o); return o; });
      await putItem("recs",{id:"tbst1",type:"bankst",firmId:"namuna01",acc:"'''+U1+'''",cur:"UZS",batch:"tbst1",part:1,parts:1,from:"2026-11-01",to:"2026-11-30",ops:L,createdAt:Date.now()},false); })('''+json.dumps(ops,ensure_ascii=False)+')')
    pg.wait_for_timeout(500)
    ct=lambda n: G(f'(()=>{{ const o=bkAllIn("namuna01").find(x=>x.n==="{n}"); const r=bkCt("namuna01",o); return r?[r.c?r.c.number:"none",r.how]:null; }})()')
    r={n:ct(n) for n in "1234567"}; print(json.dumps(r,ensure_ascii=False))
    chk(r["1"] and r["1"][0]=="12" and r["1"][1]=="рақам бўйича","1: шартнома рақами бўйича боғланмади")
    chk(r["2"] and r["2"][0]=="12" and "ҳ/ф" in r["2"][1],"2: ҳ/ф рақами бўйича боғланмади")
    chk(r["3"] and r["3"][0]=="none" and "ўз" in r["3"][1],"3: ўз маблағи «тегишли эмас» бўлмади")
    chk(r["4"] and r["4"][0]=="none" and "эквайринг" in r["4"][1],"4: Payme «тегишли эмас» бўлмади")
    chk(r["5"] is None and r["6"] is None and r["7"] is None,"5–7: иккита шартномали контрагент тахмин билан боғланиб кетди")

    # Асосий жадвал: тугма ва «тегишли эмас» автомат белгиси
    G('go({view:"firm",firmId:"namuna01",tab:"bank",bkAcc:"'+U1+'",bkGrp:false})'); pg.wait_for_timeout(600)
    chk("⚡ Тез боғлаш (3)" in G('document.body.innerText'),"«⚡ Тез боғлаш (3)» тугмаси йўқ")
    chk("✕ Автомат: тегишли эмас" in G('document.body.innerHTML'),"асосий жадвалда «тегишли эмас» автомат белгиси йўқ")

    # Гуруҳ: «Альфа» — битта танлов иккала тушумга, эслаб қолинади
    pg.click('[data-bk="grp"]'); pg.wait_for_timeout(500)
    gs=G('[...document.querySelectorAll("[data-bkgrp]")].map(x=>x.dataset.bkgrp)'); print("guruh",gs)
    chk(gs==["309999999","307777777"],"гуруҳлар нотўғри: "+str(gs))
    pg.select_option('[data-bkgrp="309999999"]',"tA2"); pg.wait_for_timeout(800)
    chk(ct("5")==["A-2","қўлда"] and ct("6")==["A-2","қўлда"],"гуруҳ танлови иккала тушумга қўлланмади")
    chk(G('bkLinkRec("namuna01").rules["309999999"]')=="tA2","контрагент эслаб қолинмади")
    G('''(async()=>{ const o={d:"2026-11-20",n:"8",t:"i",a:500,c:"«Альфа» МЧЖ",i:"309999999",s:"x",m:"",p:"Оплата"}; o.k=bkKey(o); await putItem("recs",{id:"tbst2",type:"bankst",firmId:"namuna01",acc:"'''+U1+'''",cur:"UZS",batch:"tbst2",part:1,parts:1,from:"2026-11-20",to:"2026-11-20",ops:[o],createdAt:Date.now()},false); })()'''); pg.wait_for_timeout(500)
    chk(ct("8")==["A-2","эслаб қолинган"],"янги тушум эслаб қолинган шартномага ўзи боғланмади: "+str(ct("8")))
    chk(G('document.querySelectorAll("[data-bkgrp]").length')==1,"боғланган гуруҳ рўйхатдан чиқмади")

    # Claude таклифи (сохта жавоб): «Бета» тушуми → B-2, юқори ишонч
    code=G('(()=>{ const cs=firmContracts("namuna01").filter(c=>c.dir==="out"&&c.sign!=="cancelled"); return "C"+(cs.findIndex(c=>c.id==="tB2")+1); })()')
    resp={"id":"m","model":"claude-x","stop_reason":"tool_use","usage":{"input_tokens":100,"output_tokens":40},"content":[{"type":"tool_use","name":"link_payments","input":{"items":[{"idx":0,"contract":code,"confidence":"high","reason":"Б-2 шартнома бўйича ойлик тўлов"}]}}]}
    G('''(r=>{ localStorage.setItem("fb-claude-v1",JSON.stringify({key:"sk-ant-test",model:aiCfg().model,limit:0})); window.__n=0; window.__body="";
      const _f=window.fetch; window.fetch=function(u,o){ if(!String(u).includes("api.anthropic.com")) return _f.apply(this,arguments); window.__n++; window.__body=o.body; return Promise.resolve({ok:true,status:200,headers:{get:()=>null},json:()=>Promise.resolve(JSON.parse(r))}); }; })('''+json.dumps(json.dumps(resp))+')')
    G('render()'); pg.wait_for_timeout(300)
    pg.click('[data-bk="aiLink"]'); pg.wait_for_timeout(1500)
    body=G('window.__body'); chk("B-2" in body and "307777777" in body and code in body,"Claude'га шартномалар ва тушумлар юборилмади")
    chk(G('V.bkAiRes&&V.bkAiRes.items.length')==1 and G('V.bkAiRes.items[0].on')==True,"Claude таклифи текшириш жадвалига тушмади")
    pg.click('[data-bk="aiOk"]'); pg.wait_for_timeout(800)
    chk(ct("7")==["B-2","қўлда"],"Claude таклифи тасдиқлангач боғланмади")
    chk("Барча тушумлар боғланган" in G('document.body.innerText'),"ҳаммаси боғлангач бўш ҳолат кўрсатилмади")

    # Қўлда «тегишли эмас» — боғланмаганлар ҳисобига кирмайди; ўзгартириш
    pg.click('[data-bk="grpx"]'); pg.wait_for_timeout(400)
    k3=G('bkAllIn("namuna01").find(x=>x.n==="1").k')
    pg.evaluate('''k=>{ const el=document.querySelector('[data-bklink="'+k+'"]'); el.value="none"; el.dispatchEvent(new Event("change",{bubbles:true})); }''',k3); pg.wait_for_timeout(800)
    chk(ct("1")==["none","қўлда"] and G('bkUnlinked(firm("namuna01")).length')==0,"қўлда «тегишли эмас» боғланмаганлар ҳисобида қолди")
    # Шартнома ижро карточкаси: тўловлар
    pays=G('ctPays(S.recs.find(x=>x.id==="tA2")).length'); chk(pays==3,"A-2 шартномага 3 та тўлов боғланмади: "+str(pays))
    for t in ("contracts","overview","loans"):
        G(f'go({{view:"firm",firmId:"namuna01",tab:"{t}",bkGrp:false}})'); pg.wait_for_timeout(500)
        chk(G('document.body.innerText.length')>400,f"«{t}» бўлими бўш")
    _v=G('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=86,f"версия в86 ёки юқори бўлиши керак: {_v}")
    G('go({view:"firm",firmId:"namuna01",tab:"bank",bkGrp:true})'); pg.wait_for_timeout(400)
    b.close()
ok()
