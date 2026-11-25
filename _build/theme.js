
  const root = document.documentElement;
  const themeBtn = document.getElementById('themeBtn');
  const printBtn = document.getElementById('printBtn');

  function setTheme(theme){
    root.dataset.theme = theme;
    const dark = theme === 'dark';
    themeBtn.textContent = dark ? 'Modo claro' : 'Modo oscuro';
    themeBtn.setAttribute('aria-pressed', String(dark));
    try { localStorage.setItem('guia-theme', theme); } catch(e) {}
  }
  try {
    const saved = localStorage.getItem('guia-theme');
    if (saved === 'dark' || saved === 'light') setTheme(saved);
  } catch(e) {}
  if (themeBtn) themeBtn.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));
  if (printBtn) printBtn.addEventListener('click', () => window.print());
  window.addEventListener('beforeprint', () => document.querySelectorAll('details').forEach(d => d.open = true));

  const links = [...document.querySelectorAll('.toc a[href^="#"]')];
  const sections = [...document.querySelectorAll('main section[id]')];
  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const id = entry.target.id;
        links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + id));
      });
    }, {rootMargin: '-15% 0px -70% 0px', threshold: 0});
    sections.forEach(s => obs.observe(s));
  }

  document.querySelectorAll('.openAll').forEach(b => b.addEventListener('click', () =>
    b.closest('section').querySelectorAll('details.qa').forEach(d => d.open = true)));
  document.querySelectorAll('.closeAll').forEach(b => b.addEventListener('click', () =>
    b.closest('section').querySelectorAll('details.qa').forEach(d => d.open = false)));

/* Visor de figuras */
(function(){
  const dialog = document.getElementById('figDialog');
  if (!dialog) return;
  const img = document.getElementById('figDialogImg');
  const cap = document.getElementById('figDialogCaption');
  const closeBtn = dialog.querySelector('.fig-dialog-close');
  const links = Array.from(document.querySelectorAll('.fig-open'));
  let current = 0;
  let savedScroll = 0;

  /* El diálogo modal puede arrastrar el scroll al abrirse. Guardar y
     restaurar la posición sin que la animación suave del sitio la delate. */
  function restoreScroll(y){
    if (Math.abs(window.scrollY - y) < 2) return;
    const html = document.documentElement;
    const prev = html.style.scrollBehavior;
    html.style.scrollBehavior = 'auto';
    window.scrollTo(0, y);
    html.style.scrollBehavior = prev;
  }

  function show(i){
    if (i < 0 || i >= links.length) return;
    current = i;
    const a = links[i];
    img.src = a.getAttribute('href');
    img.alt = a.getAttribute('data-alt') || '';
    cap.textContent = a.getAttribute('data-caption') || '';
    if (!dialog.open) {
      savedScroll = window.scrollY;
      dialog.showModal();
      if (closeBtn) closeBtn.focus({ preventScroll: true });
      restoreScroll(savedScroll);
      requestAnimationFrame(() => restoreScroll(savedScroll));
    }
  }

  links.forEach((a, i) => {
    a.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey) return;
      event.preventDefault();
      show(i);
    });
  });
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => restoreScroll(savedScroll));
  if (closeBtn) closeBtn.addEventListener('click', () => dialog.close());
  document.addEventListener('keydown', event => {
    if (!dialog.open) return;
    if (event.key === 'Escape') dialog.close();
    if (event.key === 'ArrowRight') show(current + 1);
    if (event.key === 'ArrowLeft') show(current - 1);
  });
})();
