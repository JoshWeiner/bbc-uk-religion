document.addEventListener('DOMContentLoaded',()=>{

  const modal      = document.getElementById('link-modal');
  const iframe     = document.getElementById('modal-frame');
  const btnClose   = document.getElementById('modal-close');

  // open modal
  document.querySelectorAll('.modal-link').forEach(a=>{
    a.addEventListener('click',e=>{
      e.preventDefault();
      const url=a.dataset.url;
      iframe.src=url;
      modal.classList.add('show');
      modal.setAttribute('aria-hidden','false');
      // If the site forbids embedding, open new tab instead
      iframe.onerror=()=>window.open(url,'_blank','noopener');
    });
  });

  // close helpers
  const close=()=>{
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden','true');
    iframe.src='';
  };
  btnClose.addEventListener('click',close);
  modal.addEventListener('click',e=>{ if(e.target===modal) close(); });
  window.addEventListener('keydown',e=>{ if(e.key==='Escape'&&modal.classList.contains('show')) close(); });

});