import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())
import base64
with sync_playwright() as p:
    b,pg=page(p); G=pg.evaluate
    G('''(()=>{window.__calls=[]; window.__rej=0; aiCall=async(blocks,tool,o)=>{ const k=blocks.map(x=>x.type).join(","); const hd=blocks[0].source?atob(blocks[0].source.data.slice(0,12)).slice(0,5):""; __calls.push(k+"|"+hd+"|"+blocks.length); if(blocks[0].type==="document"&&__rej-->0) throw new AiErr("Claude хатоси: messages.0.content.0.pdf.source.base64.data: The PDF specified was not valid."); return {input:{number:"X1"},usd:0}; }})()''')
    def run(path,rej):
        data=base64.b64encode(open(FIX+path,'rb').read()).decode()
        return G('''async([d,n,rej])=>{ __calls=[]; __rej=rej; const u=Uint8Array.from(atob(d),c=>c.charCodeAt(0)); const f=new File([u],n,{type:"application/pdf"}); try{ const r=await aiDoc(f,firm("namuna01"),AI_SPEC.sf,n); return JSON.stringify([r.x,!!r.viaImg,__calls]); }catch(e){ return "ERR "+e.message+" "+JSON.stringify(__calls); } }''',[data,path,rej])
    print('ok    ', run('sample.pdf',0))
    print('p7    ', run('signed_p7s.pdf',0))
    print('rej1  ', run('sample.pdf',1))
    print('rej2  ', run('sample.pdf',2))
    print('zip   ', run('zip_named_pdf.pdf',0))
    b.close(); ok()
