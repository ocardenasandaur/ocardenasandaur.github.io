const en=document.documentElement.lang==='en';
async function copy(value,element){try{await navigator.clipboard.writeText(value);element.textContent=en?'Copied!':'¡Copiado!'}catch{element.textContent=en?'Could not copy':'No se pudo copiar'}}
document.querySelectorAll('.copy-code').forEach(b=>b.addEventListener('click',()=>copy(b.parentElement.querySelector('pre').innerText,b)));
document.getElementById('copy-link')?.addEventListener('click',()=>copy(location.href,document.getElementById('copy-status')));
document.getElementById('print-post')?.addEventListener('click',()=>window.print());
