(function () {
  const toc = document.getElementById("docs-toc");
  const mobileToc = document.getElementById("docs-toc-mobile");
  const sheet = document.getElementById("docs-mobile-sheet");
  const toggle = document.getElementById("docs-toc-toggle");
  const dock = document.getElementById("docs-mobile-dock");
  const currentLabel = document.getElementById("docs-current-section");

  if (!toc || !mobileToc || !sheet || !toggle) {
    return;
  }

  mobileToc.innerHTML = toc.innerHTML;

  const sectionLinks = Array.from(mobileToc.querySelectorAll("a[href^='#']"));
  const sections = sectionLinks
    .map((link) => {
      const id = link.getAttribute("href")?.slice(1);
      return id ? document.getElementById(id) : null;
    })
    .filter(Boolean);

  function setActiveSection(id) {
    const activeLink = sectionLinks.find((link) => link.getAttribute("href") === `#${id}`);
    const label = activeLink?.textContent?.trim() || "Overview";

    sectionLinks.forEach((link) => {
      const isActive = link.getAttribute("href") === `#${id}`;
      link.classList.toggle("is-active", isActive);
      if (isActive) {
        link.setAttribute("aria-current", "true");
      } else {
        link.removeAttribute("aria-current");
      }
    });

    toc.querySelectorAll("a[href^='#']").forEach((link) => {
      const isActive = link.getAttribute("href") === `#${id}`;
      link.classList.toggle("is-active", isActive);
    });

    if (currentLabel) {
      currentLabel.textContent = label;
    }
  }

  function openSheet() {
    sheet.hidden = false;
    requestAnimationFrame(() => {
      sheet.classList.add("is-open");
    });
    toggle.setAttribute("aria-expanded", "true");
    dock?.classList.add("is-hidden");
    document.body.classList.add("sheet-open");
    sheet.querySelector('button[data-docs-close]')?.focus();
  }

  function closeSheet() {
    sheet.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    dock?.classList.remove("is-hidden");
    document.body.classList.remove("sheet-open");
    window.setTimeout(() => {
      if (!sheet.classList.contains("is-open")) {
        sheet.hidden = true;
      }
    }, 260);
    toggle.focus();
  }

  function initObserver() {
    if (!sections.length || !("IntersectionObserver" in window)) {
      setActiveSection(sections[0]?.id || "overview");
      return;
    }

    const visible = new Map();

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          visible.set(entry.target.id, entry.intersectionRatio);
        });

        let bestId = sections[0].id;
        let bestRatio = -1;
        visible.forEach((ratio, id) => {
          if (ratio > bestRatio) {
            bestRatio = ratio;
            bestId = id;
          }
        });

        if (bestRatio > 0) {
          setActiveSection(bestId);
        }
      },
      {
        rootMargin: "-20% 0px -55% 0px",
        threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
      }
    );

    sections.forEach((section) => observer.observe(section));
    setActiveSection(sections[0].id);
  }

  toggle.addEventListener("click", () => {
    if (sheet.classList.contains("is-open")) {
      closeSheet();
    } else {
      openSheet();
    }
  });

  sheet.querySelectorAll("[data-docs-close]").forEach((el) => {
    el.addEventListener("click", closeSheet);
  });

  sectionLinks.forEach((link) => {
    link.addEventListener("click", () => {
      closeSheet();
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && sheet.classList.contains("is-open")) {
      closeSheet();
    }
  });

  initObserver();
})();
