(function () {
  const toggleButton = document.querySelector("[data-nav-toggle]");
  const navMenu = document.querySelector("[data-nav-menu]");

  if (toggleButton && navMenu) {
    toggleButton.addEventListener("click", function () {
      const expanded = toggleButton.getAttribute("aria-expanded") === "true";
      toggleButton.setAttribute("aria-expanded", String(!expanded));
      navMenu.classList.toggle("hidden");
    });

    navMenu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.innerWidth < 1024) {
          navMenu.classList.add("hidden");
          toggleButton.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  const lightbox = document.querySelector("[data-lightbox]");
  const lightboxImage = document.querySelector("[data-lightbox-image]");
  const lightboxCaption = document.querySelector("[data-lightbox-caption]");
  const closeButton = document.querySelector("[data-lightbox-close]");
  const rootElement = document.documentElement;
  let lastTrigger = null;

  const closeLightbox = function () {
    if (!lightbox || !lightboxImage || !lightboxCaption) {
      return;
    }
    lightbox.classList.add("hidden");
    lightbox.classList.remove("flex");
    lightbox.setAttribute("aria-hidden", "true");
    rootElement.classList.remove("overflow-hidden");
    lightboxImage.src = "";
    lightboxImage.alt = "";
    lightboxCaption.textContent = "";
    lightboxCaption.classList.add("hidden");
    if (lastTrigger && typeof lastTrigger.focus === "function") {
      lastTrigger.focus();
    }
    lastTrigger = null;
  };

  if (lightbox && lightboxImage && lightboxCaption) {
    lightbox.setAttribute("aria-hidden", "true");
    document.querySelectorAll("[data-lightbox-trigger]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        const src = trigger.getAttribute("data-lightbox-src");
        const alt = trigger.getAttribute("data-lightbox-alt") || "Photo";
        const caption = trigger.getAttribute("data-lightbox-caption") || alt;

        if (!src) {
          return;
        }

        lastTrigger = trigger;
        lightboxImage.src = src;
        lightboxImage.alt = alt;
        lightboxCaption.textContent = caption;
        lightboxCaption.classList.toggle("hidden", !caption);

        lightbox.classList.remove("hidden");
        lightbox.classList.add("flex");
        lightbox.setAttribute("aria-hidden", "false");
        rootElement.classList.add("overflow-hidden");
        if (closeButton) {
          closeButton.focus();
        }
      });
    });

    if (closeButton) {
      closeButton.addEventListener("click", closeLightbox);
    }

    lightbox.addEventListener("click", function (event) {
      if (event.target === lightbox) {
        closeLightbox();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeLightbox();
      }
    });
  }

  const revealObserver = new IntersectionObserver(
    function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.remove("opacity-0", "translate-y-4");
          entry.target.classList.add("opacity-100", "translate-y-0");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.16 }
  );

  document.querySelectorAll("[data-reveal]").forEach(function (element) {
    element.classList.add("opacity-0", "translate-y-4", "transition", "duration-700");
    revealObserver.observe(element);
  });
})();
