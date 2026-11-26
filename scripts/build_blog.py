#!/usr/bin/env python3
"""Build standalone public articles and an index from Markdown + YAML."""
import argparse, datetime as dt, html, json, re, shutil
from pathlib import Path
from urllib.parse import quote
import yaml
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

E=lambda s: html.escape(str(s), quote=True)
SLUG=re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
LEVELS={'general':('General','General'),'introductorio':('Introductorio','Introductory'),'intermedio':('Intermedio','Intermediate'),'avanzado':('Avanzado','Advanced')}
ENV={'definition':('Definición','Definition'),'theorem':('Teorema','Theorem'),'proposition':('Proposición','Proposition'),'lemma':('Lema','Lemma'),'proof':('Demostración','Proof'),'example':('Ejemplo','Example'),'remark':('Observación','Remark')}

def math_inline(state,silent):
    pos=state.pos; s=state.src
    for start,end,display in [(r'\[',r'\]',True),('$$','$$',True),(r'\(',r'\)',False),('$','$',False)]:
        if not s.startswith(start,pos): continue
        stop=s.find(end,pos+len(start))
        if stop<0 or stop==pos+len(start): continue
        if start=='$' and ('\n' in s[pos+1:stop] or s[pos+1].isspace() or s[stop-1].isspace()): continue
        if not silent:
            t=state.push('math_raw','',0);t.content=s[pos+len(start):stop];t.meta={'display':display}
        state.pos=stop+len(end);return True
    return False

def math_render(tokens,idx,options,env):
    t=tokens[idx];return '<span class="math-source">'+(r'\[' if t.meta['display'] else r'\(')+E(t.content)+(r'\]' if t.meta['display'] else r'\)')+'</span>'

def math_block(state,start,end,silent):
    pos=state.bMarks[start]+state.tShift[start]; line=state.src[pos:state.eMarks[start]].strip()
    if line not in ('$$',r'\['):return False
    close='$$' if line=='$$' else r'\]'; i=start+1
    while i<end and state.src[state.bMarks[i]+state.tShift[i]:state.eMarks[i]].strip()!=close:i+=1
    if i==end:return False
    if silent:return True
    tok=state.push('math_block','div',0);tok.content=state.getLines(start+1,i,0,False);tok.block=True;state.line=i+1;return True

def math_block_render(tokens,idx,options,env):return '<div class="math-display">\\['+E(tokens[idx].content)+'\\]</div>\n'

def markdown(lang):
    md=MarkdownIt('commonmark',{'html':False}).enable('table').enable('strikethrough')
    md.inline.ruler.before('escape','math_raw',math_inline);md.renderer.rules['math_raw']=math_render
    md.block.ruler.before('fence','math_block',math_block,{'alt':['paragraph','reference','blockquote','list']});md.renderer.rules['math_block']=math_block_render
    # Fenced mathematical environments, with Markdown content and math inside.
    def fence(tokens,idx,opts,env):
        t=tokens[idx]; parts=t.info.strip().split(maxsplit=1);name=parts[0] if parts else '';title=parts[1] if len(parts)>1 else ''
        if name in ENV:
            label=ENV[name][lang=='en'];return f'<section class="math-env {name}"><strong>{E(label)}{": "+E(title) if title else ""}</strong>{md.render(t.content)}</section>'
        try:lexer=get_lexer_by_name(name) if name else TextLexer()
        except ValueError:lexer=TextLexer()
        return '<div class="code-wrap"><button type="button" class="copy-code">'+('Copy code' if lang=='en' else 'Copiar código')+'</button>'+highlight(t.content,lexer,HtmlFormatter())+'</div>'
    md.renderer.rules['fence']=fence
    return md

def parse(path,cats):
    raw=path.read_text(encoding='utf-8'); match=re.match(r'\A---\s*\n(.*?)\n---[ \t]*\n(.*)\Z',raw,re.S)
    if not match:raise ValueError(f'{path}: missing YAML front matter')
    m=yaml.safe_load(match[1]); body=match[2]
    if not isinstance(m,dict):raise ValueError(f'{path}: expected metadata mapping')
    if m.get('published') is not True:return None
    slug=path.stem
    if slug in ('posts','images','files') or not SLUG.fullmatch(slug):raise ValueError(f'{path}: invalid filename')
    lang=m.get('language','es'); title=m.get('title'); date=str(m.get('date','')); categories=m.get('categories',[])
    if lang not in ('es','en') or not isinstance(title,str) or not title.strip():raise ValueError(f'{path}: invalid language or title')
    dt.date.fromisoformat(date)
    if not isinstance(categories,list) or any(not isinstance(k,str) or k not in cats for k in categories):raise ValueError(f'{path}: unknown categories')
    level=m.get('level','') or ''
    if level and level not in LEVELS:raise ValueError(f'{path}: invalid level')
    translation=m.get('translation','') or ''
    if translation and not SLUG.fullmatch(translation):raise ValueError(f'{path}: invalid translation group')
    cover=m.get('cover','') or ''
    if cover:
        # Cover paths relative to blog/, local only.
        rel=Path(cover)
        if rel.is_absolute() or '..' in rel.parts or not cover.startswith('images/') or not (path.parent.parent/rel).is_file():raise ValueError(f'{path}: invalid cover')
    tags=m.get('tags',[]) or []
    if not isinstance(tags,list) or any(not isinstance(k,str) for k in tags):raise ValueError(f'{path}: invalid tags')
    return dict(slug=slug,title=title,date=date,categories=list(dict.fromkeys(categories)),language=lang,level=level,translation=translation,cover='blog/'+quote(cover,safe='/') if cover else '',summary=str(m.get('summary','') or ''),featured=m.get('featured') is True,tags=tags,series=str(m.get('series','') or ''),prerequisites=str(m.get('prerequisites','') or ''),minutes=max(1,round(len(body.split())/200)),url=f'blog/{slug}/',search=body[:20000],body=body)

def page(p,others,cats):
    en=p['language']=='en'; tr=lambda a,b:b if en else a
    alternate=next((x for x in others if p['translation'] and x['translation']==p['translation'] and x['language']!=p['language']),None)
    alt=f'<a href="../{E(alternate["slug"])}/">{"Español" if en else "English"}</a>' if alternate else ''
    md=markdown(p['language']);body=md.render(p['body'])
    tags=''.join(f'<span class="tag">{E(cats[k][en])}</span>' for k in p['categories'])
    level=(' · '+E(LEVELS[p['level']][en])) if p['level'] else ''
    prereq=f'<p class="prerequisites"><strong>{tr("Conocimientos previos","Prerequisites")}:</strong> {E(p["prerequisites"])}</p>' if p['prerequisites'] else ''
    cover=f'<img class="cover" src="../../{E(p["cover"])}" alt="">' if p['cover'] else ''
    related=[x for x in others if p['series'] and x['series']==p['series'] and x['slug']!=p['slug'] and x['language']==p['language']]
    series=f'<aside><h2>{tr("En esta serie","In this series")}: {E(p["series"])}</h2><ul>'+''.join(f'<li><a href="../{E(x["slug"])}/">{E(x["title"])}</a></li>' for x in sorted(related,key=lambda x:x['date']))+'</ul></aside>' if related else ''
    return f'''<!doctype html><html lang="{p['language']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(p['title'])} — Blog</title><meta name="description" content="{E(p['summary'])}"><link rel="canonical" href="https://ocardenasandaur.github.io/{p['url']}"><link rel="stylesheet" href="../article.css"><script src="../article.js" defer></script><script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']],processEscapes:true}},options:{{skipHtmlTags:['script','noscript','style','textarea','pre','code']}}}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script></head><body><main><nav><a href="../../#blog">← {tr('Volver al blog','Back to blog')}</a>{alt}</nav><header><div class="tags">{tags}</div><h1>{E(p['title'])}</h1><p class="meta">O’Bryan Cárdenas-Andaur · {E(p['date'])} · {p['minutes']} min{level}</p>{prereq}{cover}</header><article>{body}</article>{series}<footer><button id="copy-link" type="button">{tr('Copiar enlace','Copy link')}</button> <button id="print-post" type="button">{tr('Imprimir','Print')}</button><span id="copy-status" aria-live="polite"></span></footer></main></body></html>'''

def build(root):
    blog=root/'blog';cats=json.loads((blog/'categories.json').read_text()); posts=[]
    for path in sorted((blog/'posts').glob('*.md')):
        p=parse(path,cats)
        if p:posts.append(p)
    seen=set()
    for p in posts:
        key=(p['translation'],p['language'])
        if key[0] and key in seen:raise ValueError(f'Duplicate translation: {key}')
        seen.add(key)
    # Only generated directories listed in the previous index are removed.
    index=blog/'index.json'
    if index.exists():
        for p in json.loads(index.read_text()).get('posts',[]):
            slug=p.get('slug','')
            if SLUG.fullmatch(slug) and slug not in ('posts','images','files') and (blog/slug/'index.html').is_file():shutil.rmtree(blog/slug)
    for p in posts:
        target=blog/p['slug'];target.mkdir(exist_ok=True);(target/'index.html').write_text(page(p,posts,cats),encoding='utf-8')
    public=[{k:v for k,v in p.items() if k!='body'} for p in sorted(posts,key=lambda x:x['date'],reverse=True)]
    index.write_text(json.dumps({'categories':cats,'posts':public},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Raw drafts and source files do not enter the deployed Pages artifact.
    shutil.rmtree(blog/'posts',ignore_errors=True)
    print(f'Published {len(posts)} blog posts')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True,help='Staging directory, NOT repository source');a=ap.parse_args();root=a.root.resolve()
    if root==Path(__file__).resolve().parents[1]:ap.error('Use a staging directory, not the source repository')
    build(root)
