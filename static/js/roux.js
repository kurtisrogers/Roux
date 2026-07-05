document.body.addEventListener("htmx:configRequest", (event) => {
  const token = document.querySelector("[name=csrfmiddlewaretoken]");
  if (token) {
    event.detail.headers["X-CSRFToken"] = token.value;
  }
});
