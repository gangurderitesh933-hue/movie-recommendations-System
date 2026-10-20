import { gsap } from "https://esm.sh/gsap@3.12.5";
import { ScrollTrigger } from "https://esm.sh/gsap@3.12.5/ScrollTrigger";
import Lenis from "https://esm.sh/lenis@1.1.20";
import { createCinemaScene } from "./hero3d.js";

gsap.registerPlugin(ScrollTrigger);

function mount(root) {
  if (!root || root.dataset.initialized === "true") return null;
  root.dataset.initialized = "true";
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const mobile = window.matchMedia("(max-width: 760px)").matches;
  const loading = root.querySelector(".cine-journey__loading");
  const loadingBar = root.querySelector(".cine-journey__loading-bar");
  const progressFill = root.querySelector(".cine-journey__progress-fill");
  const copy = root.querySelector(".cine-journey__copy");
  const veil = root.querySelector(".cine-journey__veil");
  const cta = root.querySelector(".cine-journey__cta");
  const callouts = gsap.utils.toArray(root.querySelectorAll(".cine-journey__callout"));
  const dialog = root.querySelector(".cine-journey__modal");
  const scrollContainer = document.querySelector('[data-testid="stMain"]') || window;
  const abortController = new AbortController();
  const fullBleedContainer = root.closest(".stHtml") || root.parentElement;
  const scrollContent = scrollContainer === window
    ? document.documentElement
    : scrollContainer.querySelector('[data-testid="stMainBlockContainer"]') || scrollContainer.firstElementChild;
  function alignFullBleedHero() {
    const containerRect = fullBleedContainer.getBoundingClientRect();
    const centeredOffset = window.innerWidth / 2 - (containerRect.left + containerRect.width / 2);
    root.style.setProperty("--cine-scrollbar-gutter", `${centeredOffset}px`);
  }
  alignFullBleedHero();
  window.addEventListener("resize", alignFullBleedHero, { signal: abortController.signal });
  let scene3d = null;
  let lenis = null;
  let lenisFrame = null;
  let timeline = null;
  let fallbackTimer = null;
  let headlineTimer = null;
  let disposed = false;

  function parseMovies() {
    try {
      return JSON.parse(root.querySelector("[data-movies-json]").textContent);
    } catch (error) {
      console.error("Could not read the Discover hero movie data.", error);
      return [];
    }
  }
  function openDetails(movie) {
    dialog.querySelector("[data-detail-title]").textContent = movie.cleanTitle || movie.title;
    dialog.querySelector("[data-detail-meta]").textContent = [movie.year, movie.genres].filter(Boolean).join(" · ");
    dialog.showModal();
  }
  function attachAccessibleMovieList(movies) {
    const list = root.querySelector("[data-accessible-movies]");
    for (const movie of movies) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `${movie.cleanTitle || movie.title}${movie.year ? ` (${movie.year})` : ""}`;
      button.addEventListener("click", () => openDetails(movie), { signal: abortController.signal });
      list.appendChild(button);
    }
  }
  function setupLinks() {
    const target = document.querySelector("#discover-stats");
    for (const link of root.querySelectorAll(".cine-journey__cta")) {
      link.addEventListener("click", (event) => {
        if (!target) return;
        event.preventDefault();
        if (lenis && !reducedMotion) {
          const targetOffset = scrollContainer === window
            ? target.getBoundingClientRect().top + window.scrollY
            : target.getBoundingClientRect().top - scrollContainer.getBoundingClientRect().top + scrollContainer.scrollTop;
          lenis.scrollTo(targetOffset, { duration: 1.1 });
        } else {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, { signal: abortController.signal });
    }
    dialog.querySelector(".cine-journey__modal-close").addEventListener(
      "click", () => dialog.close(), { signal: abortController.signal },
    );
    dialog.querySelector(".cine-journey__modal-cta").addEventListener("click", () => dialog.close(), {
      signal: abortController.signal,
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    }, { signal: abortController.signal });
  }
  function revealHeadline() {
    if (root.classList.contains("cine-journey__animate-headline")
      || root.classList.contains("cine-journey__headline-visible")) return;
    if (reducedMotion) {
      root.classList.add("cine-journey__headline-visible");
      return;
    }
    root.classList.add("cine-journey__animate-headline");
    headlineTimer = window.setTimeout(() => {
      root.classList.add("cine-journey__headline-visible");
    }, 900);
  }
  function setStaticFallback() {
    root.classList.add("cine-journey__webgl-fallback");
    root.dataset.ready = "true";
    loading.classList.add("is-done");
    copy.style.opacity = "1";
    revealHeadline();
  }
  function dispose() {
    if (disposed) return;
    disposed = true;
    abortController.abort();
    window.clearTimeout(fallbackTimer);
    window.clearTimeout(headlineTimer);
    timeline?.scrollTrigger?.kill();
    timeline?.kill();
    scene3d?.dispose();
    if (lenis) {
      if (lenisFrame !== null) window.cancelAnimationFrame(lenisFrame);
      lenis.destroy();
    }
  }
  const runtime = { root, dispose };
  window.__cineHeroRuntime = runtime;

  const movies = parseMovies();
  attachAccessibleMovieList(movies);
  setupLinks();
  if (reducedMotion) {
    root.classList.add("cine-journey__reduced");
    root.dataset.ready = "true";
    loading.classList.add("is-done");
    revealHeadline();
    return runtime;
  }

  lenis = new Lenis({
    wrapper: scrollContainer,
    content: scrollContent,
    duration: .75,
    smoothWheel: true,
    syncTouch: !mobile,
    touchMultiplier: 1.15,
  });
  lenis.on("scroll", ScrollTrigger.update);
  const tickLenis = (time) => {
    if (disposed || !lenis) return;
    lenis.raf(time);
    lenisFrame = window.requestAnimationFrame(tickLenis);
  };
  lenisFrame = window.requestAnimationFrame(tickLenis);

  function setProgress(value) {
    loadingBar.style.width = `${Math.max(0, Math.min(100, value))}%`;
  }
  fallbackTimer = window.setTimeout(() => {
    if (!scene3d && !disposed) setStaticFallback();
  }, 5000);

  createCinemaScene(root, movies, setProgress).then((result) => {
    if (disposed || !root.isConnected) {
      result.dispose();
      return;
    }
    scene3d = result;
    root.classList.remove("cine-journey__webgl-fallback");
    window.clearTimeout(fallbackTimer);
    root.dataset.ready = "true";
    loading.classList.add("is-done");
    revealHeadline();
    initializeScrollScenes();
  }).catch((error) => {
    if (disposed) return;
    console.error("The 3D cinema hero could not start; showing the static hero.", error);
    setStaticFallback();
  });

  function initializeScrollScenes() {
    if (disposed || !scene3d) return;
    const { reelPivot, ribbon, posters, camera } = scene3d;
    const posterCards = [...posters.children];
    timeline = gsap.timeline({
      defaults: { ease: "power2.inOut" },
      scrollTrigger: {
        trigger: root,
        scroller: scrollContainer,
        start: "top top",
        end: "+=190%",
        pin: root,
        pinSpacing: true,
        scrub: .55,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: (self) => {
          progressFill.style.width = `${self.progress * 100}%`;
        },
      },
    });

    // Scene 1: hold the reel centered while the semantic HTML headline enters on load.
    timeline.to(reelPivot.rotation, { z: -.12, y: .25, duration: .3 }, .05);

    // Scene 2: unspool the ribbon, travel beside it, and show collection facts.
    timeline.to(copy, { opacity: 0, y: -20, duration: .22 }, .55);
    timeline.to(reelPivot.position, { x: -2.7, y: .1, duration: .52 }, .58);
    timeline.to(reelPivot.rotation, { z: -.2, y: Math.PI * 1.2, duration: .56 }, .58);
    timeline.to(ribbon.scale, { x: 1, y: 1, z: 1, duration: .6, ease: "power3.inOut" }, .58);
    timeline.to(camera.position, { x: 1.2, y: .2, z: 7.4, duration: .56 }, .58);
    timeline.to(veil, { opacity: .58, duration: .4 }, .58);
    posterCards.forEach((card, index) => {
      timeline.to(card.scale, { x: .68, y: .68, z: .68, duration: .4 }, .72 + index * .008);
    });
    timeline.to(callouts.slice(0, 2), { opacity: 1, x: 0, stagger: .1, duration: .22 }, .95);
    timeline.to(callouts.slice(0, 2), { opacity: 0, x: -14, stagger: .06, duration: .16 }, 1.4);

    // Scene 3: pull back to a larger curved poster wall and present the discovery CTA.
    const mobile = window.matchMedia("(max-width: 760px)").matches;
    timeline.to(camera.position, { x: 0, y: 0, z: mobile ? 15 : 11.6, duration: .48 }, 1.2);
    timeline.to(veil, { opacity: .24, duration: .35 }, 1.25);
    timeline.to(reelPivot.position, { x: -6.8, y: -.2, duration: .48 }, 1.25);
    timeline.to(reelPivot.scale, { x: .45, y: .45, z: .45, duration: .48 }, 1.25);
    posterCards.forEach((card, index) => {
      const columns = mobile ? 3 : 6;
      const rowCount = Math.ceil(posterCards.length / columns);
      const column = index % columns;
      const row = Math.floor(index / columns);
      const angle = ((column / Math.max(1, columns - 1)) - .5) * (mobile ? 1 : 1.15);
      const radius = mobile ? 2.7 : 5.1;
      const rowSpacing = mobile ? 1.3 : 1.85;
      const position = {
        x: Math.sin(angle) * radius + (row ? .18 : -.18) - (mobile ? 0 : .6),
        y: ((rowCount - 1) / 2 - row) * rowSpacing,
        z: Math.cos(angle) * radius - (mobile ? 1.8 : 3.5),
      };
      const arrival = 1.28 + index * .006;
      const cardScale = mobile ? 1.08 : 1.22;
      timeline.to(card.position, { ...position, duration: .4, ease: "power3.inOut" }, arrival);
      timeline.to(card.rotation, { y: -angle * .68, x: (row - (rowCount - 1) / 2) * -.025, duration: .4 }, arrival);
      timeline.to(card.scale, { x: cardScale, y: cardScale, z: cardScale, duration: .4 }, arrival);
    });
    timeline.to(ribbon.material, { opacity: .2, duration: .32 }, 1.68);
    timeline.to(callouts[2], { opacity: 1, x: 0, duration: .26 }, 1.68);
    timeline.to(cta, { opacity: 1, y: 0, duration: .3, onStart: () => { cta.style.pointerEvents = "auto"; } }, 1.98);
    ScrollTrigger.refresh();
  }
  return runtime;
}

function reconcile() {
  const root = document.querySelector(".cine-journey");
  const current = window.__cineHeroRuntime;
  if (current?.root === root && root?.isConnected) return;
  current?.dispose();
  window.__cineHeroRuntime = null;
  if (root?.isConnected) mount(root);
}

reconcile();
if (!window.__cineHeroObserver) {
  window.__cineHeroObserver = new MutationObserver(reconcile);
  window.__cineHeroObserver.observe(document.body, { childList: true, subtree: true });
}
