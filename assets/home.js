// Overview page: show a band's range label inside its bar segment only when it fits.
(function () {
  const segments = document.querySelectorAll(".band-seg");
  function fitLabels() {
    segments.forEach(seg => {
      const label = seg.querySelector(".seg-label");
      seg.classList.toggle("label-hidden", !label || label.offsetWidth > seg.clientWidth);
    });
  }
  fitLabels();
  if (document.fonts) document.fonts.ready.then(fitLabels);
  window.addEventListener("resize", fitLabels);
})();
