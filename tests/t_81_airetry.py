# в81 — aiCall: вақтинчалик хатоларда қайта уриниш, таймаут, 4xx да уринмаслик
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

def chk(c,msg):
    if not c: errs.append(msg)

OK_BODY = '{"id":"msg_1","model":"claude-x","usage":{"input_tokens":10,"output_tokens":5},' \
          '"content":[{"type":"tool_use","name":"t","input":{"ok":true}}]}'

SETUP = """(()=>{
  window.__calls=[]; window.__plan=PLAN;
  window.fetch=function(url,opt){
    if(String(url).indexOf('api.anthropic.com')<0) return Promise.reject(new Error('blocked'));
    const i=window.__calls.length; window.__calls.push(Date.now());
    const p=window.__plan[Math.min(i,window.__plan.length-1)];
    if(p.hang) return new Promise((res,rej)=>{ if(opt&&opt.signal) opt.signal.addEventListener('abort',()=>{const e=new Error('aborted');e.name='AbortError';rej(e);}); });
    return Promise.resolve({ok:p.s===200,status:p.s,headers:{get:k=>p.ra&&k==='retry-after'?p.ra:null},
      json:()=>Promise.resolve(p.s===200?JSON.parse(BODY):{error:{message:'overloaded'}})});
  };
  try{ localStorage.setItem('fb-claude-v1', JSON.stringify({key:'sk-ant-test',model:Object.keys(AI_MODELS||{})[0]||'claude-sonnet-4-5',limit:0})); }catch(e){}
})()"""

def arm(pg, plan):
    pg.evaluate(SETUP.replace("PLAN", plan).replace("BODY", repr(OK_BODY).replace("'", '"', 2) if False else "window.__ok"))

with sync_playwright() as p:
    b,pg=page(p)
    pg.evaluate(f'window.__ok={OK_BODY!r}')
    print("AI_TRIES", pg.evaluate('AI_TRIES'), "| timeout", pg.evaluate('AI_TMO'))
    chk(pg.evaluate('AI_TRIES')>=3,"қайта уриниш сони камида 3 бўлиши керак")
    chk(pg.evaluate('AI_TMO')>=60000,"таймаут жуда қисқа")

    # 1. Қайси статуслар қайтариладиган
    rt=pg.evaluate('[429,500,502,503,529,408].map(s=>aiRetriable(s))')
    nrt=pg.evaluate('[400,401,403,404,422].map(s=>aiRetriable(s))')
    print("retriable",rt,"| no-retry",nrt)
    chk(all(rt),"вақтинчалик хатолар рўйхати тўлиқ эмас")
    chk(not any(nrt),"4xx хатоларда қайта уринилмаслиги керак")

    # 2. backoff ўсиб боради ва retry-after га бўйсунади
    bo=pg.evaluate('[aiBackoff(0),aiBackoff(1),aiBackoff(2)]')
    print("backoff",bo)
    chk(bo[0]<bo[1]<bo[2],"кутиш вақти экспоненциал ўсмаяпти: "+str(bo))
    chk(pg.evaluate('aiBackoff(0,"5")')==5000,"retry-after сарлавҳасига бўйсунмади")
    chk(pg.evaluate('aiBackoff(0,"9999")')>0,"нотўғри retry-after қиймати backoff'ни бузди")

    # 3. 529 → 529 → 200: иккита қайта уринишдан кейин ишлаши керак
    arm(pg,'[{s:529},{s:529},{s:200}]')
    res=pg.evaluate('''(async()=>{ const t0=Date.now();
      try{ const r=await aiCall([{type:"text",text:"x"}],{name:"t",input_schema:{type:"object"}},{sec:"test",quiet:1});
        return {ok:!!r.input,n:window.__calls.length,ms:Date.now()-t0};
      }catch(e){ return {err:String(e.message||e),n:window.__calls.length}; } })()''')
    print("529→529→200",res)
    chk(res.get("ok"),"иккита 529 дан кейин муваффақият бўлмади: "+str(res))
    chk(res.get("n")==3,f'3 та сўров кутилган эди, {res.get("n")} бўлди')
    chk(res.get("ms",0)>=1500,"кутмасдан дарҳол қайта урингани — backoff ишламаяпти")

    # 4. 401 → дарҳол тўхтайди, қайта уринилмайди
    arm(pg,'[{s:401},{s:200},{s:200}]')
    res=pg.evaluate('''(async()=>{ try{ await aiCall([{type:"text",text:"x"}],null,{sec:"test",quiet:1}); return {ok:1,n:window.__calls.length}; }
      catch(e){ return {err:String(e.message||e),n:window.__calls.length}; } })()''')
    print("401",res)
    chk(res.get("n")==1,f'401 да 1 та сўров бўлиши керак эди, {res.get("n")} бўлди')
    chk("калит" in res.get("err",""),"401 хабари тушунарли эмас: "+str(res.get("err")))

    # 5. Ҳаммаси 529 → тушунарли хато, уриниш сони чекланган
    arm(pg,'[{s:529},{s:529},{s:529},{s:529},{s:529}]')
    res=pg.evaluate('''(async()=>{ try{ await aiCall([{type:"text",text:"x"}],null,{sec:"test",quiet:1}); return {ok:1}; }
      catch(e){ return {err:String(e.message||e),n:window.__calls.length}; } })()''')
    print("529 x5",res)
    chk(res.get("n")==pg.evaluate('AI_TRIES'),f'уриниш сони AI_TRIES дан фарқ қиляпти: {res.get("n")}')
    chk("band" in res.get("err","") or "банд" in res.get("err",""),"529 хабари тушунарли эмас: "+str(res.get("err")))

    # 6. Осилиб қолган сўров — таймаут ишлайди (қисқартирилган AI_TMO билан)
    pg.evaluate('window.__TMO=AI_TMO; AI_TMO=600;')
    arm(pg,'[{hang:1},{hang:1},{s:200}]')
    res=pg.evaluate('''(async()=>{ const t0=Date.now();
      try{ const r=await aiCall([{type:"text",text:"x"}],{name:"t",input_schema:{type:"object"}},{sec:"test",quiet:1});
        return {ok:!!r.input,n:window.__calls.length,ms:Date.now()-t0};
      }catch(e){ return {err:String(e.message||e),n:window.__calls.length,ms:Date.now()-t0}; } })()''')
    print("hang→hang→200",res)
    chk(res.get("ok"),"осилган сўровдан кейин тикланмади: "+str(res))
    chk(res.get("n")==3,f'таймаутдан кейин қайта уринмади: {res.get("n")}')
    chk(res.get("ms",99999)<20000,"таймаут ишламади — сўров осилиб қолди")

    # 7. Фақат таймаут бўлса — хабарда сония кўрсатилади
    arm(pg,'[{hang:1},{hang:1},{hang:1}]')
    res=pg.evaluate('''(async()=>{ try{ await aiCall([{type:"text",text:"x"}],null,{sec:"test",quiet:1}); return {ok:1}; }
      catch(e){ return {err:String(e.message||e)}; } })()''')
    print("timeout err",res)
    chk("сония" in res.get("err",""),"таймаут хабари тушунарли эмас: "+str(res.get("err")))
    pg.evaluate('AI_TMO=window.__TMO;')

    _v=pg.evaluate('APP_VER'); _n=int("".join(ch for ch in _v.split("в")[-1] if ch.isdigit()) or 0)
    print("VER",_v); chk(_n>=81,f"версия в81 ёки юқори бўлиши керак: {_v}")
    b.close()
ok()
