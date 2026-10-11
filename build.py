#!/usr/bin/env python3
"""Builds index.html from recipes.json. Run: python3 build.py"""
import json, html
R = json.load(open('recipes.json'))
e = html.escape
RATINGS_URL = "https://api.restful-api.dev/objects/ff808181a09d98f701a12cb4455140ad"  # shared ratings store (not in recipes.json)
RATE_ROWS = "".join(f'<div class="rrow" data-who="{w}"><span class="who">{lbl}</span><span class="stars">' + "".join(f'<button type="button" class="star" data-v="{v}" aria-label="{lbl} {v} star">&#9733;</button>' for v in range(1, 6)) + f'</span><button type="button" class="clr" hidden aria-label="Clear {lbl} rating">Clear</button></div>' for w, lbl in (("mom", "Mom"), ("dad", "Dad"), ("kids", "Kids")))
RATE_CSS = """.card,.imgwrap{position:relative}.badge{position:absolute;top:.6rem;right:.6rem;background:#b5542dee;color:#fff8ef;font:700 .95rem Georgia,serif;padding:.3rem .65rem;border-radius:20px;box-shadow:0 2px 8px #0003;z-index:2}
.badge[hidden]{display:none}.ratings{background:#fbf5ec;border-radius:12px;padding:.4rem 1rem .6rem;margin:1rem 0}.ratings h4{margin:.6rem 0}
.rrow{display:flex;align-items:center;gap:.6rem;margin:.3rem 0}.who{width:3.2rem;font-weight:600;color:#6b4a35}
.star{background:none;border:0;font-size:1.9rem;line-height:1;padding:.1rem .15rem;color:#e2c9ad;cursor:pointer;-webkit-tap-highlight-color:transparent}
.star.on{color:#d9822b}.clr{margin-left:auto;background:#f3e3cf;color:#8a3a1c;border:0;border-radius:14px;padding:.3rem .7rem;font:600 .8rem Georgia,serif;cursor:pointer}.clr[hidden]{display:none}.rmsg{font-size:.85rem;color:#8a6a55;min-height:1.1em;margin:.2rem 0 0}"""
RATE_JS = """<script>
(function(){
var URL_=%s,data={},busy=false;
function avg(r){var v=['mom','dad','kids'].map(function(k){return r&&r[k]}).filter(function(x){return x>=1&&x<=5});return v.length?(v.reduce(function(a,b){return a+b},0)/v.length):null;}
function render(){document.querySelectorAll('.badge').forEach(function(b){var a=avg(data[b.dataset.rid]);if(a){b.textContent='\\u2605 '+a.toFixed(1);b.hidden=false}else b.hidden=true;});
document.querySelectorAll('.ratings').forEach(function(box){var r=data[box.dataset.rid]||{};box.querySelectorAll('.rrow').forEach(function(row){var v=r[row.dataset.who]||0;
row.querySelectorAll('.star').forEach(function(s){s.classList.toggle('on',+s.dataset.v<=v)});row.querySelector('.clr').hidden=!v;});});}
function load(){return fetch(URL_+'?t='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw r.status;return r.json()}).then(function(j){data=(j.data&&j.data.ratings)||{};render();return data;});}
function setv(rid,who,v){data[rid]=data[rid]||{};if(v)data[rid][who]=v;else{delete data[rid][who];if(!Object.keys(data[rid]).length)delete data[rid];}}
function msg(box,t){var m=box.querySelector('.rmsg');if(m)m.textContent=t;}
document.addEventListener('click',function(e){var s=e.target.closest('.star,.clr');if(!s)return;e.preventDefault();var box=s.closest('.ratings'),rid=box.dataset.rid,who=s.closest('.rrow').dataset.who,
cur=(data[rid]||{})[who]||0,v=s.classList.contains('clr')?0:+s.dataset.v;if(v&&v===cur)v=0;
if(busy)return;busy=true;var prev=JSON.parse(JSON.stringify(data));setv(rid,who,v);render();msg(box,'Saving\\u2026');
load().catch(function(){return data}).then(function(fresh){data=fresh||{};setv(rid,who,v);render();
return fetch(URL_,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'thompson-recipe-book-ratings',data:{ratings:data}})});})
.then(function(r){if(!r.ok)throw r.status;msg(box,v?'Saved \\u2713':'Cleared \\u2713');}).catch(function(){data=prev;render();msg(box,'Could not save \\u2014 check your connection and try again.');})
.then(function(){busy=false;});});
load().catch(function(){});
document.addEventListener('visibilitychange',function(){if(!document.hidden)load().catch(function(){});});
})();
</script>""" % json.dumps(RATINGS_URL)
def img(r, cls):
    if r.get("image"):
        return f'<img class="{cls}" src="{e(r["image"])}" alt="">'
    return f'<div class="ph {cls}">&#127858;</div>'
cards = ''.join(f'<a class="card" href="#{e(r["id"])}">{img(r,"")}<span class="badge" data-rid="{e(r["id"])}" hidden></span><h3>{e(r["title"])}</h3></a>' for r in R)
pages = ''
for r in R:
    meta = ''.join(f'<span><b>{k}</b> {e(str(r[f]))}</span>' for k, f in
                   [('Serves', 'servings'), ('Prep', 'prepTime'), ('Cook', 'cookTime'), ('Total', 'totalTime')] if r.get(f))
    ing = ''.join(f'<li>{e(i)}</li>' for i in r['ingredients'])
    st = ''.join(f'<li>{e(s)}</li>' for s in r['steps'])
    pages += f'''<section class="recipe" id="{e(r["id"])}"><a class="back" href="#">&larr; All recipes</a>
<div class="imgwrap">{img(r,"hero")}<span class="badge" data-rid="{e(r["id"])}" hidden></span></div><h2>{e(r["title"])}</h2><p class="desc">{e(r.get("description",""))}</p>
<div class="meta">{meta}</div><div class="ratings" data-rid="{e(r["id"])}"><h4>Family ratings</h4>{RATE_ROWS}<p class="rmsg"></p></div><div class="cols"><div><h4>Ingredients</h4><ul>{ing}</ul></div>
<div><h4>Steps</h4><ol>{st}</ol></div></div>
<p class="src">Source: <a href="{e(r["source"])}" target="_blank" rel="noopener">{e(r.get("sourceName", r["source"]))}</a></p></section>'''
css = '''body{margin:0;font-family:Georgia,serif;background:#fbf5ec;color:#3b2a1e}header{background:#b5542d;color:#fff8ef;text-align:center;padding:calc(2rem + env(safe-area-inset-top)) calc(1rem + env(safe-area-inset-right)) 2rem calc(1rem + env(safe-area-inset-left))}main{padding-left:calc(1.5rem + env(safe-area-inset-left))!important;padding-right:calc(1.5rem + env(safe-area-inset-right))!important;padding-bottom:calc(1.5rem + env(safe-area-inset-bottom))!important}
header h1{margin:0;font-size:2.2rem}header p{margin:.3rem 0 0;opacity:.85}main{max-width:1000px;margin:auto;padding:1.5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1.2rem}.card{background:#fff;border-radius:14px;overflow:hidden;
box-shadow:0 3px 12px #0002;text-decoration:none;color:inherit;transition:transform .15s}.card:hover{transform:translateY(-4px)}
.ph{display:flex;align-items:center;justify-content:center;font-size:4rem;background:#f3e3cf;aspect-ratio:4/3}.ph.hero{max-height:260px;width:100%;border-radius:10px}.card img,.card .ph{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}.card h3{margin:0;padding:.9rem 1rem;font-size:1.1rem}
.recipe{display:none;background:#fff;border-radius:14px;padding:1.5rem;box-shadow:0 3px 12px #0002}.recipe:target{display:block}
main:has(.recipe:target) .grid{display:none}.hero{width:100%;max-height:420px;object-fit:cover;border-radius:10px}
.back{color:#b5542d;text-decoration:none;display:inline-block;margin-bottom:1rem}h2{color:#8a3a1c;margin:.8rem 0 .3rem}.desc{font-style:italic}
.meta{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}.meta span{background:#f3e3cf;padding:.35rem .8rem;border-radius:20px}
.cols{display:grid;grid-template-columns:1fr 1.6fr;gap:2rem}h4{color:#b5542d;border-bottom:2px solid #f3e3cf;padding-bottom:.3rem}
li{margin:.45rem 0;line-height:1.5}.src a{color:#b5542d}@media(max-width:700px){.cols{grid-template-columns:1fr}header h1{font-size:1.7rem}}
.card .ph,.ph{display:grid !important;place-items:center;text-align:center}'''
ADD_CSS = """.fab{position:fixed;right:calc(1.2rem + env(safe-area-inset-right));bottom:calc(1.2rem + env(safe-area-inset-bottom));z-index:20;
background:#b5542d;color:#fff8ef;border:0;border-radius:30px;padding:.9rem 1.3rem;font:600 1rem Georgia,serif;box-shadow:0 6px 18px #0004;cursor:pointer}
.fab:active{transform:scale(.96)}main:has(.recipe:target)~.fab{display:none}
.sheet-bg{position:fixed;inset:0;background:#3b2a1e88;z-index:30;display:none;align-items:flex-end;justify-content:center}
.sheet-bg.open{display:flex}.sheet{background:#fbf5ec;width:100%;max-width:520px;border-radius:18px 18px 0 0;padding:1.3rem 1.3rem calc(1.3rem + env(safe-area-inset-bottom));box-shadow:0 -6px 24px #0003}
.sheet h3{margin:0 0 .8rem;color:#8a3a1c}.sheet label{display:block;font-size:.9rem;margin:.7rem 0 .3rem;color:#6b4a35}
.row{display:flex;gap:.5rem}.sheet input,.sheet textarea{flex:1;width:100%;box-sizing:border-box;font:16px Georgia,serif;padding:.7rem;border:1.5px solid #e2c9ad;border-radius:10px;background:#fff;color:#3b2a1e}
.sheet textarea{min-height:70px;resize:vertical}.btn{border:0;border-radius:10px;padding:.7rem 1rem;font:600 1rem Georgia,serif;cursor:pointer}
.btn.alt{background:#f3e3cf;color:#8a3a1c}.btn.go{background:#b5542d;color:#fff8ef;width:100%;margin-top:1rem}
.err{color:#b3261e;font-size:.85rem;min-height:1.1em;margin:.3rem 0 0}.x{float:right;background:none;border:0;font-size:1.5rem;color:#8a3a1c;cursor:pointer;line-height:1}"""
ADD_HTML = """<button class="fab" id="addBtn" type="button" aria-haspopup="dialog">&#xFF0B; Add Recipe</button>
<div class="sheet-bg" id="sheetBg"><div class="sheet" role="dialog" aria-modal="true" aria-labelledby="sheetTitle">
<button class="x" id="closeSheet" type="button" aria-label="Close">&times;</button><h3 id="sheetTitle">Add a recipe</h3>
<form id="addForm" novalidate><label for="recLink">Recipe link</label><div class="row">
<input id="recLink" type="url" autofocus inputmode="url" autocomplete="off" autocapitalize="off" placeholder="https://..." required>
<button class="btn alt" id="pasteBtn" type="button">Paste</button></div><p class="err" id="err"></p>
<label for="recNotes">Notes (optional)</label><textarea id="recNotes" placeholder="Anything to remember?"></textarea>
<button class="btn go" type="submit">Send</button></form></div></div>
<script>
(function(){
var TO='thompkitchen@mail.grokbot.com',bg=document.getElementById('sheetBg'),link=document.getElementById('recLink'),
notes=document.getElementById('recNotes'),err=document.getElementById('err'),paste=document.getElementById('pasteBtn');
function open(){err.textContent='';bg.classList.add('open');link.focus();}
function close(){bg.classList.remove('open');}
document.getElementById('addBtn').addEventListener('click',open);
document.getElementById('closeSheet').addEventListener('click',close);
bg.addEventListener('click',function(e){if(e.target===bg)close();});
document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
if(!(navigator.clipboard&&navigator.clipboard.readText))paste.style.display='none';
paste.addEventListener('click',function(){navigator.clipboard.readText().then(function(t){link.value=t.trim();err.textContent='';link.focus();})
.catch(function(){err.textContent='Clipboard not allowed here. Long-press the field and choose Paste.';link.focus();});});
document.getElementById('addForm').addEventListener('submit',function(e){e.preventDefault();var u=link.value.trim();
if(!u){err.textContent='Please paste a recipe link.';link.focus();return;}
if(!/^https?:\\/\\//i.test(u)){err.textContent='The link should start with http:// or https://';link.focus();return;}
var body='Recipe link: '+u+(notes.value.trim()?'\\n\\nNotes: '+notes.value.trim():'');
var href='mailto:'+TO+'?subject='+encodeURIComponent('Recipe: '+u)+'&body='+encodeURIComponent(body).replace(/%0A/g,'%0D%0A');
var a=document.createElement('a');a.href=href;a.style.display='none';document.body.appendChild(a);a.click();a.remove();
link.value='';notes.value='';close();});
})();
</script>"""
open('index.html', 'w').write(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#b5542d"><link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Recipes"><link rel="apple-touch-icon" href="icons/dog-icon-180.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/dog-icon-192.png">
<title>Thompson Recipe Book</title><style>{css}{ADD_CSS}{RATE_CSS}</style></head><body><header><h1>Thompson Recipe Book</h1></header>
<main><div class="grid">{cards}</div>{pages}</main>{ADD_HTML}{RATE_JS}<script>
if('serviceWorker' in navigator){{navigator.serviceWorker.register('sw.js',{{updateViaCache:'none'}}).then(r=>{{r.update();document.addEventListener('visibilitychange',()=>{{if(!document.hidden)r.update()}})}});let R0=!!navigator.serviceWorker.controller;navigator.serviceWorker.addEventListener('controllerchange',()=>{{if(R0)location.reload();R0=true}})}}
window.addEventListener('hashchange',function(){{window.scrollTo(0,0)}});
</script></body></html>''')
print(f'Built index.html with {len(R)} recipe(s)')

# ---- PWA assets (manifest, icons, service worker) ----
import os, hashlib
from PIL import Image, ImageDraw
TERRA, CREAM, TAN, LINE = (181, 84, 45), (251, 245, 236), (240, 214, 184), (214, 160, 120)
def draw_icon(size, maskable=False):
    from PIL import Image
    src = Image.open("icon-source.png").convert("RGB")
    if not maskable: return src.resize((size, size), Image.LANCZOS)
    bg = src.getpixel((src.width//2, 10)); out = Image.new("RGB", (size, size), bg)
    inner = int(size*0.8); out.paste(src.resize((inner, inner), Image.LANCZOS), ((size-inner)//2,)*2); return out

os.makedirs("icons", exist_ok=True)
for s in (180, 192, 512): draw_icon(s).save(f"icons/dog-icon-{s}.png")
for s in (192, 512): draw_icon(s, True).save(f"icons/dog-icon-maskable-{s}.png")
json.dump({"name": "Thompson Recipe Book", "short_name": "Recipes", "description": "John & family's favorite recipes",
  "id": "/recipe-book/", "start_url": "/recipe-book/", "scope": "/recipe-book/", "display": "standalone",
  "theme_color": "#b5542d", "background_color": "#fbf5ec",
  "icons": [{"src": f"icons/dog-icon-{s}.png", "sizes": f"{s}x{s}", "type": "image/png", "purpose": "any"} for s in (192, 512)] +
           [{"src": f"icons/dog-icon-maskable-{s}.png", "sizes": f"{s}x{s}", "type": "image/png", "purpose": "maskable"} for s in (192, 512)]},
  open("manifest.webmanifest", "w"), indent=2)
assets = ["./", "recipes.json", "manifest.webmanifest"] + [f"icons/{f}" for f in sorted(os.listdir("icons"))] + [r["image"] for r in R if r.get("image")]
ver = hashlib.sha1(open("index.html", "rb").read() + json.dumps(assets).encode()).hexdigest()[:10]
open("sw.js", "w").write("""// Generated by build.py. Pages/data: network-first (new recipes show when online), cached copy offline.
// Images: cache-first, refreshed in the background.
const CACHE = 'recipes-%s';
const ASSETS = %s;
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))); });
self.addEventListener('activate', e => e.waitUntil(caches.keys()
  .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
const save = (req, res) => { if (res.ok) { const cp = res.clone(); caches.open(CACHE).then(c => c.put(req, cp)); } return res; };
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.destination === 'image') {
    e.respondWith(caches.match(req).then(hit => { const net = fetch(req).then(r => save(req, r)).catch(() => hit); return hit || net; }));
  } else {
    e.respondWith(fetch(req, {cache: 'no-store'}).then(r => save(req, r))
      .catch(() => caches.match(req, {ignoreSearch: true}).then(h => h || caches.match('./'))));
  }
});
""" % (ver, json.dumps(assets)))
print("Built PWA assets: manifest.webmanifest, sw.js, icons/")
