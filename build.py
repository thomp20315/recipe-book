#!/usr/bin/env python3
"""Builds index.html from recipes.json. Run: python3 build.py"""
import json, html
R = json.load(open('recipes.json'))
e = html.escape
SB_URL = "https://fdxtpbaguqpnislglaur.supabase.co"
SB_KEY = "sb_publishable_FTtpdWJD-TPLVZoFWhcbnQ_M5g0VRCa"  # public publishable key (safe in the site; RLS policies in supabase.sql)
SB_JS = """<script>
window.SB=function(path,o){o=o||{};var h={'apikey':%s,'Content-Type':'application/json'};if(o.prefer)h.Prefer=o.prefer;
var u=%s+'/rest/v1/'+path;return fetch(u,{method:o.method||'GET',headers:h,body:o.body?JSON.stringify(o.body):undefined,cache:'no-store'})
.then(function(r){if(!r.ok)return r.text().then(function(t){throw new Error(r.status+' '+t)});return r.status===204?null:r.text().then(function(t){return t?JSON.parse(t):null});});};
</script>""" % (json.dumps(SB_KEY), json.dumps(SB_URL))
RATE_ROWS = "".join(f'<div class="rrow" data-who="{w}"><span class="who">{lbl}</span><span class="stars">' + "".join(f'<button type="button" class="star" data-v="{v}" aria-label="{lbl} {v} star">&#9733;</button>' for v in range(1, 6)) + '</span></div>' for w, lbl in (("mom", "Mom"), ("dad", "Dad"), ("kids", "Kids")))
RATE_CSS = """.card,.imgwrap{position:relative}.badge{position:absolute;top:.6rem;right:.6rem;background:#b5542dee;color:#fff8ef;font:700 .95rem Georgia,serif;padding:.3rem .65rem;border-radius:20px;box-shadow:0 2px 8px #0003;z-index:2}
.badge[hidden]{display:none}.ratings{background:#fbf5ec;border-radius:12px;padding:.4rem 1rem .6rem;margin:1rem 0}.ratings h4{margin:.6rem 0}
.rrow{display:flex;align-items:center;gap:.6rem;margin:.3rem 0}.stars{display:flex;flex-wrap:nowrap;flex-shrink:0}.rrow{flex-wrap:nowrap}.who{width:2.8rem;flex-shrink:0;font-weight:600;color:#6b4a35}
.star{background:none;border:0;font-size:1.75rem;line-height:1;padding:.1rem .1rem;color:#e2c9ad;cursor:pointer;-webkit-tap-highlight-color:transparent}
.star.on{color:#d9822b}.rmsg{font-size:.85rem;color:#8a6a55;min-height:1.1em;margin:.2rem 0 0}"""
RATE_JS = """<script>
(function(){
var data={},busy=false;
function avg(r){var v=['mom','dad','kids'].map(function(k){return r&&r[k]}).filter(function(x){return x>=1&&x<=5});return v.length?(v.reduce(function(a,b){return a+b},0)/v.length):null;}
function render(){document.querySelectorAll('.badge').forEach(function(b){var a=avg(data[b.dataset.rid]);if(a){b.textContent='\\u2605 '+a.toFixed(1);b.hidden=false}else b.hidden=true;});
document.querySelectorAll('.ratings').forEach(function(box){var r=data[box.dataset.rid]||{};box.querySelectorAll('.rrow').forEach(function(row){var v=r[row.dataset.who]||0;
row.querySelectorAll('.star').forEach(function(s){s.classList.toggle('on',+s.dataset.v<=v)});});});}
function load(){return SB('ratings?select=recipe_id,person,stars').then(function(rows){var d={};rows.forEach(function(x){(d[x.recipe_id]=d[x.recipe_id]||{})[x.person]=x.stars});data=d;render();});}
function setv(rid,who,v){data[rid]=data[rid]||{};if(v)data[rid][who]=v;else{delete data[rid][who];if(!Object.keys(data[rid]).length)delete data[rid];}}
function msg(box,t){var m=box.querySelector('.rmsg');if(m)m.textContent=t;}
document.addEventListener('click',function(e){var s=e.target.closest('.star');if(!s)return;e.preventDefault();var box=s.closest('.ratings'),rid=box.dataset.rid,who=s.closest('.rrow').dataset.who,
cur=(data[rid]||{})[who]||0,v=+s.dataset.v;if(v&&v===cur)v=0;
if(busy)return;busy=true;var prev=JSON.parse(JSON.stringify(data));setv(rid,who,v);render();msg(box,'Saving\\u2026');
var q=v?SB('ratings?on_conflict=recipe_id,person',{method:'POST',prefer:'resolution=merge-duplicates,return=minimal',body:{recipe_id:rid,person:who,stars:v}})
:SB('ratings?recipe_id=eq.'+encodeURIComponent(rid)+'&person=eq.'+who,{method:'DELETE'});
q.then(function(){msg(box,v?'Saved \\u2713':'Cleared \\u2713');busy=false;load().catch(function(){});}).catch(function(){data=prev;render();msg(box,'Could not save \\u2014 check your connection and try again.');})
.then(function(){busy=false;});});
load().catch(function(){});setInterval(function(){if(!document.hidden)load().catch(function(){})},30000);
document.addEventListener('visibilitychange',function(){if(!document.hidden)load().catch(function(){});});
})();
</script>"""
def img(r, cls):
    if r.get("image"):
        return f'<img class="{cls}" src="{e(r["image"])}" alt="">'
    return f'<div class="ph {cls}">&#127858;</div>'
import unicodedata
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
def stext(r): return norm(' '.join([r.get('title') or '', ' '.join(r.get('ingredients') or []), r.get('sourceName') or '', r.get('source') or '', r.get('addedBy') or '']))
cards = ''.join(f'<a class="card" data-s="{e(stext(r))}" href="#{e(r["id"])}">{img(r,"")}<span class="badge" data-rid="{e(r["id"])}" hidden></span><h3>{e(r["title"])}</h3></a>' for r in R)
pages = ''
for r in R:
    meta = ''.join(f'<span><b>{k}</b> {e(str(r[f]))}</span>' for k, f in
                   [('Serves', 'servings'), ('Prep', 'prepTime'), ('Cook', 'cookTime'), ('Total', 'totalTime')] if r.get(f))
    ing = ''.join(f'<li>{e(i)}</li>' for i in r['ingredients'])
    st = ''.join(f'<li>{e(s)}</li>' for s in r['steps'])
    pages += f'''<section class="recipe" id="{e(r["id"])}"><a class="back" href="#">&larr; All recipes</a>
<div class="imgwrap">{img(r,"hero")}<span class="badge" data-rid="{e(r["id"])}" hidden></span></div><h2>{e(r["title"])}</h2><p class="desc">{e(r.get("description",""))}</p>
<div class="meta">{meta}</div><button type="button" class="cartadd" data-rid="{e(r["id"])}">&#128722; Add to shopping cart</button><div class="ratings" data-rid="{e(r["id"])}"><h4>Family ratings</h4>{RATE_ROWS}<p class="rmsg"></p></div><div class="cols"><div><h4>Ingredients</h4><ul>{ing}</ul></div>
<div><h4>Steps</h4><ol>{st}</ol></div></div>
<p class="src">Source: <a href="{e(r["source"])}" target="_blank" rel="noopener">{e(r.get("sourceName", r["source"]))}</a></p></section>'''
css = '''body{margin:0;font-family:Georgia,serif;background:#fbf5ec;color:#3b2a1e}header{background:#b5542d;color:#fff8ef;text-align:center;padding:calc(2rem + env(safe-area-inset-top)) calc(1rem + env(safe-area-inset-right)) 2rem calc(1rem + env(safe-area-inset-left))}main{padding-left:calc(1.5rem + env(safe-area-inset-left))!important;padding-right:calc(1.5rem + env(safe-area-inset-right))!important;padding-bottom:calc(1.5rem + env(safe-area-inset-bottom))!important}
header h1{margin:0;font-size:2.2rem}header p{margin:.3rem 0 0;opacity:.85}main{max-width:1000px;margin:auto;padding:1.5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1.2rem}.card{background:#fff;border-radius:14px;overflow:hidden;
box-shadow:0 3px 12px #0002;text-decoration:none;color:inherit;transition:transform .15s}.card:hover{transform:translateY(-4px)}
.ph{display:flex;align-items:center;justify-content:center;font-size:4rem;background:#f3e3cf;aspect-ratio:4/3}.ph.hero{max-height:260px;width:100%;border-radius:10px}.card img,.card .ph{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}.card h3{margin:0;padding:.9rem 1rem;font-size:1.1rem}
.recipe{display:none;background:#fff;border-radius:14px;padding:1.5rem;box-shadow:0 3px 12px #0002}.recipe:target{display:block}
main:has(.recipe:target) .grid,main:has(.recipe:target) .search,main:has(.recipe:target) .nomatch{display:none!important}.hero{width:100%;max-height:420px;object-fit:cover;border-radius:10px}
.back{color:#b5542d;text-decoration:none;display:inline-block;margin-bottom:1rem}h2{color:#8a3a1c;margin:.8rem 0 .3rem}.desc{font-style:italic}
.meta{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}.meta span{background:#f3e3cf;padding:.35rem .8rem;border-radius:20px}
.cols{display:grid;grid-template-columns:1fr 1.6fr;gap:2rem}h4{color:#b5542d;border-bottom:2px solid #f3e3cf;padding-bottom:.3rem}
li{margin:.45rem 0;line-height:1.5}.src a{color:#b5542d}@media(max-width:700px){.cols{grid-template-columns:1fr}header h1{font-size:1.7rem}}
.card .ph,.ph{display:grid !important;place-items:center;text-align:center}'''
SEARCH_CSS = """.search{position:sticky;top:env(safe-area-inset-top);z-index:10;display:flex;align-items:center;background:#fff;border:1.5px solid #e2c9ad;border-radius:28px;padding:0 .4rem 0 .9rem;margin:-.4rem 0 1.2rem;box-shadow:0 4px 14px #3b2a1e22}
.sicon{font-size:1rem;opacity:.6;margin-right:.4rem}.search input{flex:1;min-width:0;border:0;outline:0;background:transparent;font:16px Georgia,serif;color:#3b2a1e;padding:.8rem 0;-webkit-appearance:none;appearance:none}
.search input::-webkit-search-cancel-button{display:none}.search:focus-within{border-color:#b5542d}
.qx{border:0;background:#f3e3cf;color:#8a3a1c;width:2rem;height:2rem;border-radius:50%;font-size:1.3rem;line-height:1;cursor:pointer;flex-shrink:0}.qx[hidden]{display:none}
.card.hide{display:none}.nomatch{text-align:center;color:#8a6a55;font-style:italic;padding:2rem 1rem}.nomatch[hidden]{display:none}"""
SEARCH_JS = """<script>
(function(){var q=document.getElementById('q'),x=document.getElementById('qx'),nm=document.getElementById('nomatch'),nmq=document.getElementById('nmq'),cards=[].slice.call(document.querySelectorAll('.card'));
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
function run(){var raw=q.value,w=norm(raw).split(/\\s+/).filter(Boolean),n=0;
cards.forEach(function(c){var ok=w.every(function(t){return c.dataset.s.indexOf(t)>=0});c.classList.toggle('hide',!ok);if(ok)n++;});
x.hidden=!raw;nm.hidden=n>0;nmq.textContent=raw.trim();}
q.addEventListener('input',run);x.addEventListener('click',function(){q.value='';run();q.focus();});
q.addEventListener('keydown',function(e){if(e.key==='Escape'){q.value='';run();}if(e.key==='Enter')q.blur();});run();})();
</script>"""
CART_CSS = """.shop{background:#fff;border-radius:12px;box-shadow:0 2px 8px #0001;padding:.9rem 1rem;margin-bottom:1rem}.shop label{display:block;font-size:.9rem;color:#6b4a35;margin-bottom:.35rem}
.ziprow{display:flex;gap:.5rem}.ziprow input{width:7.5rem;font:16px Georgia,serif;padding:.7rem;border:1.5px solid #e2c9ad;border-radius:10px;letter-spacing:.1em}
.gobtn{flex:1;border:0;border-radius:10px;background:#3f7d3a;color:#fff;font:700 1.05rem Georgia,serif;padding:.75rem;cursor:pointer}.gobtn:disabled{opacity:.6}
.shopmsg{margin:.6rem 0 0;font-size:.92rem;min-height:1em}.shopmsg.ok{color:#2f6b2a;font-weight:700}.shopmsg.err{color:#b3261e}
.res h4{margin:.2rem 0 .6rem;color:#8a3a1c}.res .best{background:#e6f2df;color:#2f6b2a;border-radius:10px;padding:.6rem .8rem;font-weight:700;margin-bottom:.7rem}
.res .store{border:1.5px solid #f3e3cf;border-radius:10px;padding:.6rem .8rem;margin-bottom:.6rem}.res .store.cheap{border-color:#3f7d3a}.res .sh{display:flex;justify-content:space-between;gap:.5rem;font-weight:700}.res .sa{font-size:.82rem;color:#8a6a55}
.res .pick{border-top:1px solid #f3e3cf;padding:.45rem 0;font-size:.92rem}.res .pick:first-of-type{border-top:0}.res .pn a{color:#b5542d;font-weight:600}.res .pw{font-size:.8rem;color:#5d7a4f}.res .pp{float:right;font-weight:700}.res details.store summary{list-style:none;cursor:pointer}.res details.store summary::-webkit-details-marker{display:none}.res details.store summary .sh span:first-child:before{content:'\\25B8  ';color:#b5542d}.res details[open].store summary .sh span:first-child:before{content:'\\25BE  '}
.res .cp{color:#2f6b2a;font-size:.85rem;display:flex;justify-content:space-between;gap:.5rem}.res .cp a{color:#2f6b2a}.res .fp{font-size:.88rem;font-weight:700;display:flex;justify-content:space-between}.res .sum{border-top:2px solid #f3e3cf;margin-top:.4rem;padding-top:.4rem;font-size:.9rem}.res .sum>div{display:flex;justify-content:space-between}.res .tot{font-weight:700;font-size:1rem}
.res .miss{font-size:.83rem;color:#b3261e;margin:.4rem 0}.res .sv{color:#2f6b2a}.res .rh{margin:1rem 0 .5rem;color:#8a3a1c;font-size:1rem}.res .hyb{border:2px dashed #3f7d3a;border-radius:10px;padding:.6rem .8rem;margin-bottom:.6rem;background:#f6fbf3}.res .hgrp{font-size:.9rem;margin-top:.4rem}.res .hgrp ul{margin:.2rem 0 0;padding-left:1.2rem}
.res .all{list-style:none;padding:0;margin:0;font-size:.9rem}.res .all li{display:flex;justify-content:space-between;border-top:1px solid #f3e3cf;padding:.35rem 0}.res .notes{font-size:.85rem;color:#6b4a35;font-style:italic}.res .when{font-size:.78rem;color:#a08a7a}
header{position:relative}header h1{padding:0 3.3rem;text-wrap:balance}@media(max-width:480px){header h1{font-size:1.5rem}}.cartbtn{position:absolute;top:calc(.8rem + env(safe-area-inset-top));right:calc(.8rem + env(safe-area-inset-right));background:#fff8ef22;border:1.5px solid #fff8ef88;color:#fff8ef;width:2.9rem;height:2.9rem;border-radius:50%;font-size:1.35rem;cursor:pointer;display:flex;align-items:center;justify-content:center}
.cnt{position:absolute;top:-.35rem;right:-.35rem;background:#fff8ef;color:#b5542d;font:700 .78rem system-ui,sans-serif;min-width:1.3rem;height:1.3rem;border-radius:.65rem;display:flex;align-items:center;justify-content:center;padding:0 .25rem;box-shadow:0 1px 4px #0003}.cnt[hidden]{display:none}
.cartadd{display:block;width:100%;background:#b5542d;color:#fff8ef;border:0;border-radius:12px;padding:.85rem;font:600 1.05rem Georgia,serif;margin:.4rem 0 1rem;cursor:pointer}.cartadd:active{transform:scale(.98)}
.toast{position:fixed;left:50%;bottom:calc(5.5rem + env(safe-area-inset-bottom));transform:translateX(-50%) translateY(20px);background:#3b2a1e;color:#fff8ef;padding:.75rem 1.2rem;border-radius:24px;font:600 .95rem Georgia,serif;opacity:0;transition:.25s;z-index:60;pointer-events:none;max-width:90vw;text-align:center}.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.cart-bg{position:fixed;inset:0;background:#3b2a1e88;z-index:40;display:none}.cart-bg.open{display:block}
.cart{position:absolute;inset:0;margin:auto;max-width:560px;background:#fbf5ec;display:flex;flex-direction:column;padding-top:env(safe-area-inset-top)}
.cart-h{display:flex;align-items:center;gap:.5rem;background:#b5542d;color:#fff8ef;padding:.9rem 1rem}.cart-h h3{flex:1;margin:0;font-size:1.3rem}.cart-h button{background:none;border:0;color:#fff8ef;font-size:1.7rem;cursor:pointer;line-height:1}
.cart-body{flex:1;overflow:auto;-webkit-overflow-scrolling:touch;padding:1rem 1rem 1.5rem}
.cust{display:flex;gap:.5rem;margin-bottom:1rem}.cust input{flex:1;min-width:0;font:16px Georgia,serif;padding:.7rem;border:1.5px solid #e2c9ad;border-radius:10px;background:#fff;color:#3b2a1e}
.cust button,.cart-f button{border:0;border-radius:10px;padding:.7rem 1rem;font:600 .95rem Georgia,serif;cursor:pointer;background:#b5542d;color:#fff8ef}
.grp{background:#fff;border-radius:12px;box-shadow:0 2px 8px #0001;margin-bottom:1rem;overflow:hidden}.grp-h{display:flex;align-items:center;gap:.5rem;padding:.7rem 1rem;background:#f3e3cf;color:#8a3a1c;font-weight:700}
.grp-h span{flex:1}.grp-h button{background:none;border:0;color:#8a3a1c;font:600 .85rem Georgia,serif;text-decoration:underline;cursor:pointer}
.it{display:flex;align-items:center;gap:.6rem;padding:.55rem 1rem;border-top:1px solid #f3e3cf}.it:first-of-type{border-top:0}
.it input[type=checkbox]{width:1.35rem;height:1.35rem;accent-color:#b5542d;flex-shrink:0}.it .t{flex:1;line-height:1.4;word-break:break-word}.it.done .t{text-decoration:line-through;color:#a08a7a}
.it button{background:none;border:0;font-size:1.05rem;padding:.3rem;cursor:pointer;color:#8a6a55}.it .ed{flex:1;font:16px Georgia,serif;padding:.4rem;border:1.5px solid #b5542d;border-radius:8px}
.cart-f{display:flex;gap:.5rem;padding:.8rem 1rem calc(.8rem + env(safe-area-inset-bottom));border-top:1px solid #e2c9ad;background:#fbf5ec}.cart-f button{flex:1;background:#f3e3cf;color:#8a3a1c}
.empty{text-align:center;color:#8a6a55;font-style:italic;padding:2rem 0}.cstat{font-size:.85rem;color:#8a6a55;min-height:1.1em;margin:-.4rem 0 .6rem}"""
CART_HTML = """<div class="toast" id="toast" role="status" aria-live="polite"></div>
<div class="cart-bg" id="cartBg"><div class="cart" role="dialog" aria-modal="true" aria-labelledby="cartTitle">
<div class="cart-h"><h3 id="cartTitle">&#128722; Shopping cart</h3><button type="button" id="cartClose" aria-label="Close cart">&times;</button></div>
<div class="cart-body">
<div class="shop"><label for="zipIn">Your zip code</label><div class="ziprow"><input id="zipIn" type="text" inputmode="numeric" pattern="[0-9]*" maxlength="5" placeholder="12345" autocomplete="postal-code">
<button type="button" class="gobtn" id="goBtn">&#128717; Let&rsquo;s go shopping</button></div><p class="shopmsg" id="shopMsg"></p></div>
<form class="cust" id="custForm"><input id="custIn" type="text" placeholder="Add an item (e.g. milk)" enterkeyhint="done" autocomplete="off"><button type="submit">Add</button></form>
<p class="cstat" id="cstat"></p><div id="cartList"></div>
<div class="shop res" id="results" hidden></div></div>
<div class="cart-f"><button type="button" id="clrChecked">Clear checked</button><button type="button" id="clrAll">Clear all</button></div></div></div>
<script>
(function(){
var REC=""" + json.dumps({r["id"]: {"t": r["title"], "i": r["ingredients"]} for r in R}, ensure_ascii=False) + """;
var items=[],$=function(i){return document.getElementById(i)};
function esc(s){var d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML;}
function safeUrl(u){return /^https?:\\/\\//i.test(u||'')?u:null;}
function toast(t){var el=$('toast');el.textContent=t;el.classList.add('show');clearTimeout(el._t);el._t=setTimeout(function(){el.classList.remove('show')},2200);}
var seq=0;function load(){var my=++seq;return SB('cart_items?select=*&order=sort_order.asc,created_at.asc').then(function(x){if(my===seq){items=x;render();}}).catch(function(){});}
function act(p,okMsg){$('cstat').textContent='Saving\\u2026';return p.then(function(r){return load().then(function(){$('cstat').textContent='';if(okMsg)toast(okMsg);return r});})
.catch(function(){$('cstat').textContent='Couldn\\u2019t save \\u2014 check your connection and try again.';toast('Couldn\\u2019t save \\u2014 try again');load();});}
function render(){var n=items.filter(function(i){return !i.checked}).length,c=$('cartCnt');c.textContent=n>99?'99+':n;c.hidden=!n;
var L=$('cartList');if(!items.length){L.innerHTML='<p class="empty">Your cart is empty. Add a recipe\\u2019s ingredients from its page, or add an item above.</p>';return;}
var groups={},order=[];items.forEach(function(i){var k=i.recipe_id||'';if(!groups[k]){groups[k]=[];order.push(k)}groups[k].push(i);});
order.sort(function(a,b){return (a===''?1:0)-(b===''?1:0)});
L.innerHTML=order.map(function(k){var g=groups[k],title=k?(g[0].recipe_title||(REC[k]&&REC[k].t)||k):'Other items';
return '<div class="grp"><div class="grp-h"><span>'+esc(title)+'</span><button type="button" data-delgrp="'+esc(k)+'">Remove</button></div>'+g.map(function(i){
return '<div class="it'+(i.checked?' done':'')+'" data-id="'+esc(i.id)+'"><input type="checkbox" aria-label="Check off '+esc(i.text)+'"'+(i.checked?' checked':'')+'><span class="t">'+esc(i.text)+'</span><button type="button" class="edit" aria-label="Edit">&#9998;</button><button type="button" class="del" aria-label="Delete">&#128465;</button></div>';}).join('')+'</div>';}).join('');}
function money(v){return (typeof v==='number')?'$'+v.toFixed(2):esc(v||'');}
function num(v){return typeof v==='number'?v:null;}
function pickLine(p){var u=safeUrl(p.url),c=p.coupon,fp=num(p.final_price)!=null?p.final_price:(num(p.price)!=null&&c&&num(c.savings)!=null?p.price-c.savings:null);
var h='<div class="pick"><span class="pp">'+money(p.price)+(p.unit?' <small>/ '+esc(p.unit)+'</small>':'')+'</span><div class="pn">'+esc(p.item)+': '+(u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(p.product)+'</a>':esc(p.product))+(p.brand?' <small>('+esc(p.brand)+')</small>':'')+'</div>'+(p.why_clean?'<div class="pw">&#127807; '+esc(p.why_clean)+'</div>':'');
if(c){var cu=safeUrl(c.source_url);h+='<div class="cp">&#127991; '+esc(c.description||'Coupon')+(c.type?' <small>('+esc(String(c.type).replace('_',' '))+')</small>':'')+(cu?' <a href="'+esc(cu)+'" target="_blank" rel="noopener">details</a>':'')+'<span>'+(num(c.savings)!=null?'&minus;'+money(c.savings):'')+'</span></div>';}
if(c&&fp!=null)h+='<div class="fp">Final <span>'+money(fp)+'</span></div>';return h+'</div>';}
function sums(s){return '<div class="sum"><div>Subtotal <span>'+money(num(s.subtotal)!=null?s.subtotal:s.total)+'</span></div>'+(num(s.coupon_savings)?'<div class="cp">Coupons saved <span>&minus;'+money(s.coupon_savings)+'</span></div>':'')+'<div class="tot">Total <span>'+money(s.total)+'</span></div></div>';}
function renderResults(rows){var box=$('results');if(!rows||!rows.length){box.hidden=true;return;}var row=rows[0],r=row.result||{},st=r.stores||[],picks=r.picks||[];
var byId={};st.forEach(function(s){byId[s.id]=s});
var priced=st.filter(function(s){return num(s.total)!=null}).sort(function(a,b){return a.total-b.total});
var top=(Array.isArray(r.top3)&&r.top3.length?r.top3.map(function(id){return byId[id]}).filter(Boolean):priced).slice(0,3);
var full=priced.filter(function(s){return !(Array.isArray(s.items_missing)&&s.items_missing.length)});var cheapest=(r.cheapest_store&&byId[r.cheapest_store])||full[0]||priced[0]||null;
var h='<h4>&#129534; Shopping results</h4><div class="when">'+esc(new Date(row.created_at).toLocaleString())+(r.zip||row.zip?' &middot; zip '+esc(r.zip||row.zip):'')+'</div>';
if(cheapest)h+='<div class="best">Cheapest overall: '+esc(cheapest.name)+' &mdash; '+money(cheapest.total)+(num(cheapest.coupon_savings)?' <small>(after '+money(cheapest.coupon_savings)+' in coupons)</small>':'')+'</div>';
var hy=r.hybrid;
if(hy&&Array.isArray(hy.assignments)&&hy.assignments.length){var hs=(hy.stores||[]).map(function(id){return byId[id]?byId[id].name:id});
h+='<details class="store hyb"><summary><div class="sh"><span>&#128256; Best 2-store split</span><span>'+money(hy.total)+'</span></div><div class="sa">'+esc(hs.join(' + '))+(num(hy.savings_vs_best_single)?' &middot; <b class="sv">saves '+money(hy.savings_vs_best_single)+'</b> vs. one store':'')+'</div></summary>';
(hy.stores||[]).forEach(function(id){var its=hy.assignments.filter(function(a){return a.store===id});if(!its.length)return;h+='<div class="hgrp"><b>'+esc(byId[id]?byId[id].name:id)+'</b><ul>'+its.map(function(a){return '<li>'+esc(a.item)+'</li>'}).join('')+'</ul></div>';});
h+=sums(hy)+(hy.note?'<p class="notes">'+esc(hy.note)+'</p>':'')+'</details>';}
if(top.length){h+='<h5 class="rh">Top '+top.length+' store'+(top.length>1?'s':'')+'</h5>';
h+=top.map(function(s,ix){var ps=picks.filter(function(p){return p.store===s.id||p.store===s.name});
var miss=Array.isArray(s.items_missing)?s.items_missing:[];
return '<details class="store'+(s===cheapest?' cheap':'')+'"'+(ix===0?' open':'')+'><summary><div class="sh"><span>'+(ix+1)+'. '+esc(s.name)+'</span><span>'+money(s.total)+'</span></div><div class="sa">'+esc(s.address||'')+(s.distance_mi!=null?' &middot; '+esc(s.distance_mi)+' mi':'')+(s.items_found!=null?' &middot; '+esc(s.items_found)+' found':'')+(miss.length?' &middot; '+miss.length+' missing':'')+(num(s.coupon_savings)?' &middot; <b class="sv">'+money(s.coupon_savings)+' coupons</b>':'')+'</div></summary>'+
ps.map(pickLine).join('')+(miss.length?'<div class="miss">Not found here: '+miss.map(esc).join(', ')+'</div>':'')+(ps.length||num(s.total)!=null?sums(s):'')+'</details>';}).join('');}
var rest=st.filter(function(s){return top.indexOf(s)<0});
if(st.length){h+='<h5 class="rh">All stores checked</h5><ul class="all">'+st.map(function(s){return '<li><span>'+esc(s.name)+(s.distance_mi!=null?' <small>'+esc(s.distance_mi)+' mi</small>':'')+'</span><span>'+(num(s.total)!=null?money(s.total):'<small>no prices</small>')+'</span></li>'}).join('')+'</ul>';}
if(r.notes)h+='<p class="notes">'+esc(r.notes)+'</p>';box.innerHTML=h;box.hidden=false;}
function loadResults(){return SB('shopping_results?select=*&order=created_at.desc&limit=1').then(renderResults).catch(function(){});}
function loadZip(){return SB('settings?key=eq.zip&select=value').then(function(r){if(r[0]&&document.activeElement!==$('zipIn'))$('zipIn').value=r[0].value||'';}).catch(function(){});}
function openCart(){$('cartBg').classList.add('open');document.body.style.overflow='hidden';load();loadZip();loadResults();}
function closeCart(){$('cartBg').classList.remove('open');document.body.style.overflow='';}
$('cartBtn').addEventListener('click',openCart);$('cartClose').addEventListener('click',closeCart);
$('cartBg').addEventListener('click',function(e){if(e.target===$('cartBg'))closeCart();});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&$('cartBg').classList.contains('open'))closeCart();});
document.addEventListener('click',function(e){var b=e.target.closest('.cartadd');if(!b)return;var rid=b.dataset.rid,R_=REC[rid];if(!R_)return;b.disabled=true;
SB('cart_items?select=id&limit=1&recipe_id=eq.'+encodeURIComponent(rid)).then(function(ex){
if(ex.length&&!confirm('\\u201c'+R_.t+'\\u201d is already in the cart. Add its ingredients again?\\n\\nOK = add again, Cancel = skip')){toast('Skipped \\u2014 already in cart');return;}
var base=Date.now()/1000;return act(SB('cart_items',{method:'POST',prefer:'return=minimal',body:R_.i.map(function(t,ix){return {recipe_id:rid,recipe_title:R_.t,text:t,sort_order:base+ix/1000}})}),'Added '+R_.i.length+' items \\u2713');})
.catch(function(){toast('Couldn\\u2019t reach the cart \\u2014 try again');}).then(function(){b.disabled=false;});});
$('custForm').addEventListener('submit',function(e){e.preventDefault();var t=$('custIn').value.trim();if(!t)return;$('custIn').value='';
act(SB('cart_items',{method:'POST',prefer:'return=minimal',body:{text:t}}),'Added \\u2713');});
function upd(id,patch){return SB('cart_items?id=eq.'+id,{method:'PATCH',prefer:'return=minimal',body:patch});}
$('cartList').addEventListener('change',function(e){if(e.target.type!=='checkbox')return;var id=e.target.closest('.it').dataset.id,v=e.target.checked;
e.target.closest('.it').classList.toggle('done',v);act(upd(id,{checked:v}));});
$('cartList').addEventListener('click',function(e){var row=e.target.closest('.it'),g=e.target.closest('[data-delgrp]');
if(g){var k=g.dataset.delgrp;if(confirm('Remove all items for this recipe?'))act(SB('cart_items?'+(k?'recipe_id=eq.'+encodeURIComponent(k):'recipe_id=is.null'),{method:'DELETE'}),'Removed \\u2713');return;}
if(!row)return;var id=row.dataset.id;
if(e.target.closest('.del')){row.style.opacity=.4;act(SB('cart_items?id=eq.'+id,{method:'DELETE'}));return;}
if(e.target.closest('.edit')){var sp=row.querySelector('.t'),old=sp.textContent,inp=document.createElement('input');inp.className='ed';inp.value=old;sp.replaceWith(inp);inp.focus();var done=false;
function fin(save){if(done)return;done=true;var v=inp.value.trim();if(save&&v&&v!==old)act(upd(id,{text:v}));else render();}
inp.addEventListener('keydown',function(k){if(k.key==='Enter'){k.preventDefault();fin(true)}if(k.key==='Escape')fin(false)});inp.addEventListener('blur',function(){fin(true)});}});
$('clrChecked').addEventListener('click',function(){if(!items.some(function(i){return i.checked})){toast('Nothing checked yet');return;}act(SB('cart_items?checked=is.true',{method:'DELETE'}),'Cleared checked items \\u2713');});
$('clrAll').addEventListener('click',function(){if(!items.length)return;if(confirm('Clear the whole shopping cart for everyone?'))act(SB('cart_items?id=not.is.null',{method:'DELETE'}),'Cart cleared');});
$('zipIn').addEventListener('input',function(){this.value=this.value.replace(/\\D/g,'').slice(0,5);var z=this.value;if(z.length===5)SB('settings?on_conflict=key',{method:'POST',prefer:'resolution=merge-duplicates,return=minimal',body:{key:'zip',value:z}}).then(function(){toast('Zip saved \\u2713')}).catch(function(){});});
$('goBtn').addEventListener('click',function(){var z=$('zipIn').value,m=$('shopMsg'),btn=this;m.className='shopmsg';
if(!/^[0-9]{5}$/.test(z)){m.className='shopmsg err';m.textContent='Enter your 5-digit zip code first.';$('zipIn').focus();return;}
var un=items.filter(function(i){return !i.checked});if(!un.length){m.className='shopmsg err';m.textContent='Your cart has no unchecked items to shop for.';return;}
var who='';try{who=localStorage.getItem('rb-addedBy')||''}catch(_){}
btn.disabled=true;m.textContent='Sending\\u2026';
SB('settings?on_conflict=key',{method:'POST',prefer:'resolution=merge-duplicates,return=minimal',body:{key:'zip',value:z}}).catch(function(){}).then(function(){
return SB('shopping_requests',{method:'POST',prefer:'return=minimal',body:{zip:z,requested_by:who||null,items:un.map(function(i){return {text:i.text,recipe_id:i.recipe_id,recipe_title:i.recipe_title}})}});})
.then(function(){m.className='shopmsg ok';m.textContent='Sous-Chef is on it! Results will show up here.';})
.catch(function(){m.className='shopmsg err';m.textContent='Couldn\\u2019t send \\u2014 check your connection and try again.';}).then(function(){btn.disabled=false;});});
load();document.addEventListener('visibilitychange',function(){if(!document.hidden){load();if($('cartBg').classList.contains('open')){loadResults();loadZip();}}});
setInterval(function(){if(!document.hidden&&$('cartBg').classList.contains('open')){load();loadResults();}},20000);
})();
</script>"""

ADD_CSS = """.fab{position:fixed;right:calc(1.2rem + env(safe-area-inset-right));bottom:calc(1.2rem + env(safe-area-inset-bottom));z-index:20;
background:#b5542d;color:#fff8ef;border:0;border-radius:30px;padding:.9rem 1.3rem;font:600 1rem Georgia,serif;box-shadow:0 6px 18px #0004;cursor:pointer}
.fab:active{transform:scale(.96)}main:has(.recipe:target)~.fab{display:none}
.sheet-bg{position:fixed;inset:0;background:#3b2a1e88;z-index:30;display:none;align-items:flex-end;justify-content:center}
.sheet-bg.open{display:flex}.sheet{background:#fbf5ec;width:100%;max-width:520px;border-radius:18px 18px 0 0;padding:1.3rem 1.3rem calc(1.3rem + env(safe-area-inset-bottom));box-shadow:0 -6px 24px #0003}
.sheet h3{margin:0 0 .8rem;color:#8a3a1c}.sheet label{display:block;font-size:.9rem;margin:.7rem 0 .3rem;color:#6b4a35}
.row{display:flex;gap:.5rem}.sheet input,.sheet textarea{flex:1;width:100%;box-sizing:border-box;font:16px Georgia,serif;padding:.7rem;border:1.5px solid #e2c9ad;border-radius:10px;background:#fff;color:#3b2a1e}
.sheet textarea{min-height:70px;resize:vertical}.btn{border:0;border-radius:10px;padding:.7rem 1rem;font:600 1rem Georgia,serif;cursor:pointer}
.btn.alt{background:#f3e3cf;color:#8a3a1c}.btn.go{background:#b5542d;color:#fff8ef;width:100%;margin-top:1rem}
.err{color:#b3261e;font-size:.85rem;min-height:1.1em;margin:.3rem 0 0}.who-pick{display:flex;gap:.5rem}.who-pick button{flex:1;border:1.5px solid #e2c9ad;background:#fff;color:#6b4a35;border-radius:20px;padding:.5rem;font:600 .95rem Georgia,serif;cursor:pointer}.who-pick button.on{background:#b5542d;border-color:#b5542d;color:#fff8ef}.ok{background:#e6f2df;color:#2f6b2a;border-radius:10px;padding:.6rem .8rem;margin:.8rem 0 0;font-weight:600}.ok[hidden]{display:none}.btn.go:disabled{opacity:.7}.x{float:right;background:none;border:0;font-size:1.5rem;color:#8a3a1c;cursor:pointer;line-height:1}"""
ADD_HTML = """<button class="fab" id="addBtn" type="button" aria-haspopup="dialog">&#xFF0B; Add Recipe</button>
<div class="sheet-bg" id="sheetBg"><div class="sheet" role="dialog" aria-modal="true" aria-labelledby="sheetTitle">
<button class="x" id="closeSheet" type="button" aria-label="Close">&times;</button><h3 id="sheetTitle">Add a recipe</h3>
<form id="addForm" novalidate><label for="recLink">Recipe link</label><div class="row">
<input id="recLink" type="url" autofocus inputmode="url" autocomplete="off" autocapitalize="off" placeholder="https://..." required>
<button class="btn alt" id="pasteBtn" type="button">Paste</button></div><p class="err" id="err"></p>
<label for="recNotes">Notes (optional)</label><textarea id="recNotes" placeholder="Anything to remember?"></textarea>
<label>Added by (optional)</label><div class="who-pick" id="whoPick"><button type="button" data-w="Mom">Mom</button><button type="button" data-w="Dad">Dad</button><button type="button" data-w="Kids">Kids</button></div>
<p class="ok" id="okMsg" hidden></p>
<button class="btn go" id="sendBtn" type="submit">Send</button></form></div></div>
<script>
(function(){
var bg=document.getElementById('sheetBg'),link=document.getElementById('recLink'),
notes=document.getElementById('recNotes'),err=document.getElementById('err'),paste=document.getElementById('pasteBtn'),
ok=document.getElementById('okMsg'),send=document.getElementById('sendBtn'),pick=document.getElementById('whoPick'),busy=false;
var who='';try{who=localStorage.getItem('rb-addedBy')||''}catch(_){}
function showWho(){pick.querySelectorAll('button').forEach(function(b){b.classList.toggle('on',b.dataset.w===who)});}
pick.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;who=(who===b.dataset.w)?'':b.dataset.w;try{localStorage.setItem('rb-addedBy',who)}catch(_){}showWho();});showWho();
function open(){err.textContent='';ok.hidden=true;send.textContent='Send';bg.classList.add('open');link.focus();}
function close(){bg.classList.remove('open');}
document.getElementById('addBtn').addEventListener('click',open);
document.getElementById('closeSheet').addEventListener('click',close);
bg.addEventListener('click',function(e){if(e.target===bg&&!busy)close();});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!busy)close();});
if(!(navigator.clipboard&&navigator.clipboard.readText))paste.style.display='none';
paste.addEventListener('click',function(){navigator.clipboard.readText().then(function(t){link.value=t.trim();err.textContent='';link.focus();})
.catch(function(){err.textContent='Clipboard not allowed here. Long-press the field and choose Paste.';link.focus();});});
document.getElementById('addForm').addEventListener('submit',function(e){e.preventDefault();if(busy)return;var u=link.value.trim();err.textContent='';
if(!u){err.textContent='Please paste a recipe link.';link.focus();return;}
if(!/^https?:\\/\\//i.test(u)){err.textContent='The link should start with http:// or https://';link.focus();return;}
var item={url:u,notes:notes.value.trim()};if(who)item.added_by=who;
busy=true;send.disabled=true;send.textContent='Adding\\u2026';
SB('recipe_queue',{method:'POST',prefer:'return=minimal',body:item}).then(function(){ok.textContent='Added! \\u2713 It\\u2019ll appear in the book shortly';ok.hidden=false;send.textContent='Added \\u2713';
link.value='';notes.value='';setTimeout(function(){busy=false;send.disabled=false;close();},1800);})
.catch(function(){busy=false;send.disabled=false;send.textContent='Retry';err.textContent='Couldn\\u2019t save \\u2014 check your connection and tap Retry.';});});
})();
</script>"""
open('index.html', 'w').write(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#b5542d"><link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Recipes"><link rel="apple-touch-icon" href="icons/dog-icon-180.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/dog-icon-192.png">
<title>Thompson Recipe Book</title><style>{css}{ADD_CSS}{RATE_CSS}{SEARCH_CSS}{CART_CSS}</style></head><body><header><button type="button" class="cartbtn" id="cartBtn" aria-label="Shopping cart">&#128722;<span class="cnt" id="cartCnt" hidden>0</span></button><h1>Thompson Recipe Book</h1></header>
<main><div class="search" role="search"><span class="sicon" aria-hidden="true">&#128269;</span><input id="q" type="search" placeholder="Search recipes, ingredients, who added&hellip;" aria-label="Search recipes" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="search"><button type="button" id="qx" class="qx" aria-label="Clear search" hidden>&times;</button></div><div class="grid">{cards}</div><p class="nomatch" id="nomatch" hidden>No recipes match &ldquo;<span id="nmq"></span>&rdquo;. Try another word.</p>{pages}</main>{SB_JS}{ADD_HTML}{RATE_JS}{SEARCH_JS}{CART_HTML}<script>
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
