(function () {
  var parts = window.location.pathname.split("/").filter(Boolean);
  var prefix = parts[0] === "Roux" ? "/Roux/" : "/";
  var file = parts[parts.length - 1];
  var base = document.createElement("base");
  // Point base at the current page so in-page #anchors stay on this document.
  base.href = file && file.includes(".") ? prefix + file : prefix;
  document.head.appendChild(base);
})();
