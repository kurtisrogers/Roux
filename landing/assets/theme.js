(function () {
  const storageKey = "roux-theme";
  const root = document.documentElement;

  function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    const toggle = document.getElementById("theme-toggle");
    if (toggle) {
      const isDark = theme === "dark";
      toggle.setAttribute("aria-pressed", String(isDark));
      toggle.setAttribute(
        "aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode"
      );
      toggle.querySelector(".theme-icon-light")?.toggleAttribute("hidden", isDark);
      toggle.querySelector(".theme-icon-dark")?.toggleAttribute("hidden", !isDark);
    }
  }

  function initTheme() {
    const stored = localStorage.getItem(storageKey);
    applyTheme(stored || getSystemTheme());
  }

  function toggleTheme() {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(storageKey, next);
    applyTheme(next);
  }

  function initNav() {
    const toggle = document.getElementById("nav-toggle");
    const menu = document.getElementById("site-nav");
    if (!toggle || !menu) return;

    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
    });

    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menu.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open navigation menu");
      });
    });
  }

  document.getElementById("theme-toggle")?.addEventListener("click", toggleTheme);

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (event) => {
      if (!localStorage.getItem(storageKey)) {
        applyTheme(event.matches ? "dark" : "light");
      }
    });

  initTheme();
  initNav();
})();
