// Arnetrice — operational interactions.
// No framework: IntersectionObserver reveals, sticky-nav shrink, count-ups.
(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Reveal on scroll ---------- */
  const revealTargets = document.querySelectorAll("[data-reveal]");
  if (revealTargets.length && "IntersectionObserver" in window && !reducedMotion) {
    const io = new IntersectionObserver(
      (entries, observer) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-revealed");
            observer.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -80px 0px" }
    );
    revealTargets.forEach((el) => io.observe(el));
  } else {
    revealTargets.forEach((el) => el.classList.add("is-revealed"));
  }

  /* ---------- Sticky nav shrink ---------- */
  const nav = document.querySelector("[data-nav]");
  if (nav) {
    let lastY = -1;
    const onScroll = () => {
      const y = window.scrollY;
      if ((y > 24) !== (lastY > 24)) {
        nav.classList.toggle("is-scrolled", y > 24);
      }
      lastY = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mobile nav toggle (no Alpine dependency) ---------- */
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navOverlay = document.querySelector("[data-nav-overlay]");
  if (navToggle && navOverlay) {
    navToggle.addEventListener("click", () => {
      const open = navOverlay.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
    });
    navOverlay.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        navOverlay.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      })
    );
  }

  /* ---------- Filter buttons — channel filter active state on /insights ---------- */
  const filterBtns = document.querySelectorAll("[data-channel-btn]");
  if (filterBtns.length) {
    filterBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        filterBtns.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
      });
    });
  }

  /* ---------- HTMX swap: mark reveal targets as visible (no flash of empty) ---------- */
  document.body.addEventListener("htmx:afterSwap", (evt) => {
    if (!evt.target) return;
    evt.target.querySelectorAll("[data-reveal]").forEach((el) => el.classList.add("is-revealed"));
  });

  /* ---------- Metric count-ups (when in viewport) ---------- */
  const counters = document.querySelectorAll("[data-count]");
  if (counters.length && "IntersectionObserver" in window && !reducedMotion) {
    const co = new IntersectionObserver(
      (entries, observer) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseFloat(el.dataset.count || "0");
            const duration = parseInt(el.dataset.countDuration || "1200", 10);
            const start = performance.now();
            const step = (now) => {
              const t = Math.min(1, (now - start) / duration);
              const eased = 1 - Math.pow(1 - t, 3);
              el.textContent = Math.round(target * eased).toLocaleString();
              if (t < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
            observer.unobserve(el);
          }
        }
      },
      { threshold: 0.5 }
    );
    counters.forEach((el) => co.observe(el));
  } else {
    counters.forEach((el) => {
      el.textContent = parseFloat(el.dataset.count || "0").toLocaleString();
    });
  }
})();
