"""
Умумий тест асоси (harness).
Ҳар бир тест файли биринчи қаторида шуни бажаради:

    import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness.py")).read())

Шундан кейин қуйидагилар тайёр бўлади:
    page(p)  — браузер ва саҳифани очади (демо режимда)
    errs     — JavaScript хатолари рўйхати (охирида бўш бўлиши шарт)
    FIX      — fixtures/ папкаси йўли
    OUT      — out/ папкаси йўли (скриншотлар)
"""
import os, sys, subprocess
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIX  = os.path.join(HERE, "fixtures") + os.sep
OUT  = os.path.join(HERE, "out") + os.sep
NM   = os.path.join(HERE, "node_modules") + os.sep
DEMO = os.path.join(OUT, "demo.html")
os.makedirs(OUT, exist_ok=True)

errs = []

# --- демо файлни тайёрлаш: CLIENT_ID олиб ташланади -> дастур демо режимда ишлайди
def build_demo():
    src = os.path.join(ROOT, "index.html")
    if not os.path.exists(src):
        sys.exit("index.html топилмади: " + src)
    html = open(src, encoding="utf-8").read()
    import re
    html = re.sub(r'CLIENT_ID: "[^"]*",', 'CLIENT_ID: "",', html, count=1)
    html = html.replace('demo:"fb-demo"', 'demo:"fb-demo-test"', 1)
    open(DEMO, "w", encoding="utf-8").write(html)

# --- CDN кутубхоналарини локал nusxadan бериш (интернетсиз ишлаши учун)
LIBS = [
    ("xlsx.full.min.js",     "xlsx/dist/xlsx.full.min.js"),
    ("pdf-lib",              "pdf-lib/dist/pdf-lib.min.js"),
    ("pdf.worker.min.js",    "pdfjs-dist/build/pdf.worker.min.js"),
    ("pdf.min.js",           "pdfjs-dist/build/pdf.min.js"),
    ("html2canvas",          "html2canvas/dist/html2canvas.min.js"),
    ("jspdf",                "jspdf/dist/jspdf.umd.min.js"),
    ("pako",                 "pako/dist/pako.min.js"),
    ("qrcode-generator",     "qrcode-generator/qrcode.js"),
]

def route(r):
    u = r.request.url
    H = {"Access-Control-Allow-Origin": "*"}
    for key, rel in LIBS:
        if key in u:
            p = NM + rel
            if os.path.exists(p):
                return r.fulfill(path=p, content_type="application/javascript", headers=H)
            return r.continue_()      # локал нусха йўқ -> CDN'дан олишга урин
    return r.abort()

def page(p, w=1440, h=900):
    build_demo()
    b = p.chromium.launch()
    ctx = b.new_context(accept_downloads=True, viewport={"width": w, "height": h})
    pg = ctx.new_page()
    pg.route("**/cdnjs.cloudflare.com/**", route)
    pg.route("**/cdn.jsdelivr.net/**", route)
    pg.route("**/fonts.g*/**", lambda r: r.abort())
    pg.route("**/api.anthropic.com/**", lambda r: r.abort())   # Claude'га ҳақиқий сўров юборилмайди
    pg.route("**/cbu.uz/**", lambda r: r.abort())
    pg.route("**/chamber.uz/**", lambda r: r.abort())
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + DEMO)
    pg.wait_for_timeout(1500)
    return b, pg

def ok():
    """Тест охирида чақирилади. Хато бўлса, чиқиш коди 1 бўлади."""
    print("ERR", errs)
    if errs:
        sys.exit(1)
