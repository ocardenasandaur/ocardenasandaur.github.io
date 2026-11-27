/* Public index: no draft content is loaded. */
let blogIndex=null,blogFailure=false,blogQuery='',blogCategory='all';
function renderBlog(){
 const root=document.getElementById('blog-list'); if(!root)return;
 const en=currentLang==='en', tr=(a,b)=>en?b:a;
 const intro=`<p class="blog-intro">${tr('Un espacio para compartir ideas, dentro y fuera de la matemática. Aquí tendrán cabida notas matemáticas, reflexiones, opiniones, lecturas, viajes, fotografías y pequeños relatos de la vida cotidiana.','A space to share ideas, both within and beyond mathematics. Here you will find mathematical notes, reflections, opinions, books, travel, photographs and short stories from everyday life.')}</p>`;
 root.innerHTML=intro;
 if(blogFailure){root.insertAdjacentHTML('beforeend',`<div class="blog-empty" role="status">${tr('No se pudo cargar el blog. Inténtalo de nuevo recargando la página.','The blog could not be loaded. Please reload the page.')}</div>`);return;}
 if(!blogIndex){root.insertAdjacentHTML('beforeend',`<p role="status">${tr('Cargando entradas…','Loading posts…')}</p>`);return;}
 const cats=blogIndex.categories||{}, grouped=new Map();
 for(const p of blogIndex.posts||[]){const k=p.translation?'translation:'+p.translation:'slug:'+p.slug; if(!grouped.has(k)||p.language===currentLang)grouped.set(k,p);}
 const posts=[...grouped.values()].sort((a,b)=>b.date.localeCompare(a.date));
 if(!posts.length){root.insertAdjacentHTML('beforeend',`<div class="blog-empty"><strong>${tr('Un espacio por escribir','A space yet to be written')}</strong>${tr('Por ahora no hay entradas publicadas.','There are no published posts yet.')}</div>`);return;}
 const catLabel=k=>cats[k]?.[en?1:0]||k;
 const used=[...new Set(posts.flatMap(p=>p.categories))];if(blogCategory!=='all'&&!used.includes(blogCategory))blogCategory='all';
 const levels={general:tr('General','General'),introductorio:tr('Introductorio','Introductory'),intermedio:tr('Intermedio','Intermediate'),avanzado:tr('Avanzado','Advanced')};
 const dateLabel=p=>{const d=new Date(p.date+'T00:00:00Z');return Number.isNaN(d.valueOf())?p.date:new Intl.DateTimeFormat(en?'en-GB':'es-CL',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(d)};
 const card=p=>`<a class="blog-entry" href="${esc(p.url)}">${p.cover?`<img src="${esc(p.cover)}" alt="" loading="lazy">`:''}<div class="blog-entry-body"><div class="blog-tags">${p.categories.map(k=>`<span class="blog-tag" style="color:${/^#[0-9a-f]{6}$/i.test(cats[k]?.[2]||'')?({'#7c3aed':'#5b21b6','#64748b':'#475569'}[cats[k][2]]||cats[k][2]):'#5b21b6'}">${esc(catLabel(k))}</span>`).join('')}</div><h3>${esc(p.title)}</h3>${p.summary?`<p>${esc(p.summary)}</p>`:''}<div class="blog-meta">${esc(dateLabel(p))} · ${p.language.toUpperCase()} · ${p.minutes} min${p.level?' · '+esc(levels[p.level]||p.level):''}</div><span class="blog-read">${tr('Leer entrada','Read post')} →</span></div></a>`;
 const featured=posts.find(p=>p.featured);
 if(featured)root.insertAdjacentHTML('beforeend',`<section class="blog-featured"><h3 class="subsec-title">${tr('Entrada destacada','Featured post')}</h3>${card(featured)}</section>`);
 root.insertAdjacentHTML('beforeend',`<h3 class="subsec-title">${tr('Todas las entradas','All posts')}</h3><div class="blog-controls"><input type="search" id="blog-search" aria-label="${tr('Buscar entradas','Search posts')}" placeholder="${tr('Buscar entradas…','Search posts…')}"><select id="blog-category" aria-label="${tr('Categoría','Category')}"><option value="all">${tr('Todas las categorías','All categories')}</option>${used.map(k=>`<option value="${esc(k)}">${esc(catLabel(k))}</option>`).join('')}</select></div><p class="blog-count" aria-live="polite"></p><div class="blog-grid"></div>`);
 const input=root.querySelector('input'),select=root.querySelector('select');input.value=blogQuery;select.value=blogCategory;
 const fold=s=>String(s).normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase();
 function update(){const q=fold(blogQuery.trim()), matches=posts.filter(p=>(blogCategory==='all'||p.categories.includes(blogCategory))&&fold([p.title,p.summary,...p.categories.map(catLabel),...(p.tags||[]),p.search||''].join(' ')).includes(q));root.querySelector('.blog-count').textContent=matches.length+' '+tr('entradas','posts');root.querySelector('.blog-grid').innerHTML=matches.length?matches.map(card).join(''):`<p>${tr('No hay coincidencias.','No matching posts.')}</p>`;}
 input.addEventListener('input',()=>{blogQuery=input.value;update()});select.addEventListener('change',()=>{blogCategory=select.value;update()});update();
}
fetch('blog/index.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(d=>{blogIndex=d;renderBlog()}).catch(()=>{blogFailure=true;renderBlog()});
