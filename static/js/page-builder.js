function getCsrfToken() {
  const el = document.querySelector("[name=csrfmiddlewaretoken]");
  return el ? el.value : "";
}

function initPageBuilderSortable() {
  const container = document.getElementById("sortable-blocks");
  if (!container || typeof Sortable === "undefined") return;

  if (container._sortable) {
    container._sortable.destroy();
  }

  container._sortable = Sortable.create(container, {
    handle: ".drag-handle",
    animation: 150,
    ghostClass: "block-ghost",
    onEnd() {
      const pageId = container.dataset.pageId;
      const reorderUrl = container.dataset.reorderUrl;
      const blockOrder = [...container.querySelectorAll("[data-block-id]")].map(
        (el) => el.dataset.blockId
      );

      fetch(reorderUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ block_order: blockOrder }),
      });
    },
  });
}

document.addEventListener("DOMContentLoaded", initPageBuilderSortable);
document.body.addEventListener("htmx:afterSwap", (event) => {
  if (event.target.id === "sortable-blocks" || event.target.querySelector?.("#sortable-blocks")) {
    initPageBuilderSortable();
  }
});
