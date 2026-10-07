// Overview page: show a band's range label inside its bar segment only when it fits,
// and hide frequency tick labels that would overlap their neighbours.
(function () {
  const segments = document.querySelectorAll(".band-seg");
  const tickRows = document.querySelectorAll(".band-ticks");
  const GAP = 6; // minimum px between tick labels

  function fitLabels() {
    segments.forEach(seg => {
      const label = seg.querySelector(".seg-label");
      seg.classList.toggle("label-hidden", !label || label.offsetWidth > seg.clientWidth);
    });
  }

  function fitTicks() {
    tickRows.forEach(row => {
      const ticks = [...row.children];
      ticks.forEach(t => { t.style.visibility = ""; });
      // Keep the first and last edge; drop any tick that runs into the previous shown one.
      let prev = ticks[0];
      for (let i = 1; i < ticks.length; i++) {
        const t = ticks[i];
        const collides = t.getBoundingClientRect().left < prev.getBoundingClientRect().right + GAP;
        if (!collides) { prev = t; continue; }
        if (i === ticks.length - 1 && prev !== ticks[0]) {
          prev.style.visibility = "hidden";   // the group's upper edge wins over an inner tick
          if (t.getBoundingClientRect().left < ticks[0].getBoundingClientRect().right + GAP) t.style.visibility = "hidden";
        } else {
          t.style.visibility = "hidden";
        }
      }
    });
  }

  function fit() { fitLabels(); fitTicks(); }
  fit();
  if (document.fonts) document.fonts.ready.then(fit);
  window.addEventListener("resize", fit);
})();
