// Illinois Tech header: condensed state on scroll, "Resources for..." and mobile menus,
// and the search panel (results open on iit.edu's own search page).
(function () {
  const header = document.getElementById("siteHeader");
  const hamburger = document.getElementById("hamburgerBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const audienceItem = document.getElementById("audienceItem");
  const audienceToggle = document.getElementById("audienceToggle");
  const searchToggle = document.getElementById("searchToggle");
  const searchPanel = document.getElementById("searchPanel");
  const searchForm = document.getElementById("searchForm");

  const SCROLL_THRESHOLD = 60;
  let ticking = false;
  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      header.classList.toggle("is-scrolled", window.scrollY > SCROLL_THRESHOLD);
      ticking = false;
    });
  }, { passive: true });

  function setOpen(button, open, onToggle) {
    button.setAttribute("aria-expanded", String(open));
    onToggle(open);
  }
  const toggleMobile = open => setOpen(hamburger, open, o => mobileMenu.classList.toggle("open", o));
  const toggleAudience = open => setOpen(audienceToggle, open, o => audienceItem.classList.toggle("open", o));
  const toggleSearch = open => setOpen(searchToggle, open, o => {
    searchPanel.hidden = !o;
    if (o) searchPanel.querySelector("input").focus();
  });

  hamburger.addEventListener("click", () => toggleMobile(!mobileMenu.classList.contains("open")));
  audienceToggle.addEventListener("click", () => toggleAudience(!audienceItem.classList.contains("open")));
  searchToggle.addEventListener("click", () => toggleSearch(searchPanel.hidden));

  searchForm.addEventListener("submit", e => {
    e.preventDefault();
    const q = searchForm.querySelector("input").value.trim();
    if (!q) return;
    window.open(`https://www.iit.edu/search#?cludoquery=${encodeURIComponent(q)}&cludopage=1&cludoinputtype=standard`,
      "_blank", "noopener");
  });

  document.addEventListener("click", e => {
    if (!e.target.closest(".scrolled-actions") && !e.target.closest("#mobileMenu")) toggleMobile(false);
    if (!e.target.closest("#audienceItem")) toggleAudience(false);
    if (!e.target.closest("#searchToggle") && !e.target.closest("#searchPanel")) toggleSearch(false);
  });
  document.addEventListener("keydown", e => {
    if (e.key !== "Escape") return;
    toggleMobile(false);
    toggleAudience(false);
    toggleSearch(false);
  });
})();
