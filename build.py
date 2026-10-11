#!/usr/bin/env python3
"""Builds index.html from recipes.json. Run: python3 build.py"""
import json, html
R = json.load(open('recipes.json'))
e = html.escape
def img(r, cls):
    if r.get("image"):
        return f'<img class="{cls}" src="{e(r["image"])}" alt="">'
    return f'<div class="ph {cls}">&#127858;</div>'
cards = ''.join(f'<a class="card" href="#{e(r["id"])}">{img(r,"")}<h3>{e(r["title"])}</h3></a>' for r in R)
pages = ''
for r in R:
    meta = ''.join(f'<span><b>{k}</b> {e(str(r[f]))}</span>' for k, f in
                   [('Serves', 'servings'), ('Prep', 'prepTime'), ('Cook', 'cookTime'), ('Total', 'totalTime')] if r.get(f))
    ing = ''.join(f'<li>{e(i)}</li>' for i in r['ingredients'])
    st = ''.join(f'<li>{e(s)}</li>' for s in r['steps'])
    pages += f'''<section class="recipe" id="{e(r["id"])}"><a class="back" href="#">&larr; All recipes</a>
{img(r,"hero")}<h2>{e(r["title"])}</h2><p class="desc">{e(r.get("description",""))}</p>
<div class="meta">{meta}</div><div class="cols"><div><h4>Ingredients</h4><ul>{ing}</ul></div>
<div><h4>Steps</h4><ol>{st}</ol></div></div>
<p class="src">Source: <a href="{e(r["source"])}" target="_blank" rel="noopener">{e(r.get("sourceName", r["source"]))}</a></p></section>'''
css = '''body{margin:0;font-family:Georgia,serif;background:#fbf5ec;color:#3b2a1e}header{background:#b5542d;color:#fff8ef;text-align:center;padding:2rem 1rem}
header h1{margin:0;font-size:2.2rem}header p{margin:.3rem 0 0;opacity:.85}main{max-width:1000px;margin:auto;padding:1.5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1.2rem}.card{background:#fff;border-radius:14px;overflow:hidden;
box-shadow:0 3px 12px #0002;text-decoration:none;color:inherit;transition:transform .15s}.card:hover{transform:translateY(-4px)}
.ph{display:flex;align-items:center;justify-content:center;font-size:4rem;background:#f3e3cf;aspect-ratio:4/3}.ph.hero{max-height:260px;width:100%;border-radius:10px}.card .ph{display:flex !important}.card img,.card .ph{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}.card h3{margin:0;padding:.9rem 1rem;font-size:1.1rem}
.recipe{display:none;background:#fff;border-radius:14px;padding:1.5rem;box-shadow:0 3px 12px #0002}.recipe:target{display:block}
main:has(.recipe:target) .grid{display:none}.hero{width:100%;max-height:420px;object-fit:cover;border-radius:10px}
.back{color:#b5542d;text-decoration:none;display:inline-block;margin-bottom:1rem}h2{color:#8a3a1c;margin:.8rem 0 .3rem}.desc{font-style:italic}
.meta{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}.meta span{background:#f3e3cf;padding:.35rem .8rem;border-radius:20px}
.cols{display:grid;grid-template-columns:1fr 1.6fr;gap:2rem}h4{color:#b5542d;border-bottom:2px solid #f3e3cf;padding-bottom:.3rem}
li{margin:.45rem 0;line-height:1.5}.src a{color:#b5542d}@media(max-width:700px){.cols{grid-template-columns:1fr}header h1{font-size:1.7rem}}'''
open('index.html', 'w').write(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Thompson Recipe Book</title><style>{css}</style></head><body><header><h1>Thompson Recipe Book</h1><p>John &amp; family's favorites</p></header>
<main><div class="grid">{cards}</div>{pages}</main></body></html>''')
print(f'Built index.html with {len(R)} recipe(s)')
