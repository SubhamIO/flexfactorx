(function () {
  'use strict';

  // ── Stat counter — counts up from 0 on scroll into view ──
  function animateCounter(el) {
    var original = el.textContent.trim();
    var match = original.match(/^([\d.]+)(.*)/);
    if (!match) return; // non-numeric (∞ etc.) — leave as-is

    var target   = parseFloat(match[1]);
    var suffix   = match[2]; // '+', 'K+', '%', etc.
    var duration = 1400;
    var start    = performance.now();

    (function tick(now) {
      var p      = Math.min((now - start) / duration, 1);
      var eased  = 1 - Math.pow(1 - p, 3); // ease-out cubic
      el.textContent = Math.floor(eased * target) + suffix;
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = original; // snap to exact original on finish
    }(start));
  }

  var counters = document.querySelectorAll('[data-count-up]');
  if (counters.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        animateCounter(entry.target);
      });
    }, { threshold: 0.6 });

    counters.forEach(function (el) { io.observe(el); });
  }
}());
