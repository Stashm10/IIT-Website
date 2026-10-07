(function(){
  const header    = document.getElementById('siteHeader');
  const hamburger = document.getElementById('hamburgerBtn');
  const mobileMenu = document.getElementById('mobileMenu');

  const SCROLL_THRESHOLD = 60;
  let ticking = false;
  function onScroll(){
    if (!ticking){
      requestAnimationFrame(() => {
        header.classList.toggle('is-scrolled', window.scrollY > SCROLL_THRESHOLD);
        ticking = false;
      });
      ticking = true;
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  const triggers = document.querySelectorAll('.nav-trigger');
  function closeAllPanels(except){
    triggers.forEach(btn => {
      if (btn === except) return;
      btn.setAttribute('aria-expanded', 'false');
      document.getElementById(btn.getAttribute('aria-controls')).classList.remove('open');
    });
  }
  triggers.forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = document.getElementById(btn.getAttribute('aria-controls'));
      const isOpen = panel.classList.contains('open');
      closeAllPanels(btn);
      panel.classList.toggle('open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  if (hamburger){
    hamburger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', String(isOpen));
    });
  }

  const searchToggle = document.querySelector('.site-search__toggle');
  const searchPanel  = document.getElementById('searchPanel');
  if (searchToggle && searchPanel){
    const srLabel = searchToggle.querySelector('.show-for-sr');
    searchToggle.addEventListener('click', () => {
      const opening = searchToggle.getAttribute('aria-expanded') !== 'true';
      searchToggle.setAttribute('aria-expanded', String(opening));
      document.body.classList.toggle(searchToggle.dataset.buttonOpenClass, opening);
      searchPanel.hidden = !opening;
      srLabel.textContent = opening
        ? searchToggle.dataset.buttonCloseText
        : searchToggle.dataset.buttonOpenText;
      if (opening) searchPanel.querySelector('input').focus();
    });
  }

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.main-nav')) closeAllPanels(null);
    if (!e.target.closest('.scrolled-actions')) mobileMenu.classList.remove('open');
    if (searchToggle && !e.target.closest('.site-search__toggle') && !e.target.closest('.search-panel')){
      searchToggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove(searchToggle.dataset.buttonOpenClass);
      searchPanel.hidden = true;
      searchToggle.querySelector('.show-for-sr').textContent = searchToggle.dataset.buttonOpenText;
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape'){
      closeAllPanels(null);
      mobileMenu.classList.remove('open');
      if (searchToggle){
        searchToggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove(searchToggle.dataset.buttonOpenClass);
        searchPanel.hidden = true;
        searchToggle.querySelector('.show-for-sr').textContent = searchToggle.dataset.buttonOpenText;
      }
    }
  });
})();
