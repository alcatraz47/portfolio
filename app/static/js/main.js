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

  const closeLightbox = function () {
    if (!lightbox || !lightboxImage || !lightboxCaption) {
      return;
    }
    lightbox.classList.add("hidden");
    lightbox.classList.remove("flex");
    lightboxImage.src = "";
    lightboxImage.alt = "";
    lightboxCaption.textContent = "";
  };

  if (lightbox && lightboxImage && lightboxCaption) {
    document.querySelectorAll("[data-lightbox-trigger]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        const src = trigger.getAttribute("data-lightbox-src");
        const alt = trigger.getAttribute("data-lightbox-alt") || "Photo";

        if (!src) {
          return;
        }

        lightboxImage.src = src;
        lightboxImage.alt = alt;
        lightboxCaption.textContent = alt;

        lightbox.classList.remove("hidden");
        lightbox.classList.add("flex");
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
