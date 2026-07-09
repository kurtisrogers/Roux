document.body.addEventListener("htmx:configRequest", (event) => {
  const token = document.querySelector("[name=csrfmiddlewaretoken]");
  if (token) {
    event.detail.headers["X-CSRFToken"] = token.value;
  }
});

function initBookingCalendar() {
  const container = document.getElementById("booking-calendar");
  if (!container) {
    return;
  }

  let events = [];
  try {
    events = JSON.parse(container.dataset.events || "[]");
  } catch {
    events = [];
  }

  if (!events.length) {
    container.innerHTML = '<p class="empty-state">No sessions in this date range.</p>';
    return;
  }

  const fragment = document.createDocumentFragment();
  events.forEach((event) => {
    const link = document.createElement("a");
    link.className = "booking-calendar__event";
    link.href = event.url || "#";
    link.innerHTML = `<div><strong>${event.title}</strong><small>${event.start}</small></div><span class="status-pill">Register</span>`;
    fragment.appendChild(link);
  });
  container.appendChild(fragment);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initBookingCalendar);
} else {
  initBookingCalendar();
}
