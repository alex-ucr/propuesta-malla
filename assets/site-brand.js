/**
 * Inserta la barra de logos UCR / Escuela de Matemática en todas las páginas.
 * Incluir en el <head>: <script src="assets/site-brand.js" defer></script>
 */
(function () {
  var scriptEl = document.currentScript;
  var base = "assets/";
  if (scriptEl && scriptEl.src) {
    base = scriptEl.src.replace(/\/[^/]*$/, "/");
  }
  var logos = base + "logos/";

  function inject() {
    if (document.querySelector("header.site-brand")) return;
    if (!document.body) return;

    var header = document.createElement("header");
    header.className = "site-brand";
    header.setAttribute("role", "banner");
    header.innerHTML =
      '<div class="site-brand-inner">' +
      '<a href="https://www.ucr.ac.cr/" target="_blank" rel="noopener noreferrer" title="Universidad de Costa Rica">' +
      '<img class="logo-ucr logo-desktop" src="' +
      logos +
      'firma-ucr-blanco.png" alt="Universidad de Costa Rica" width="280" height="48" />' +
      '<img class="logo-ucr logo-mobile" src="' +
      logos +
      'firma-ucr-blanco-movil.png" alt="Universidad de Costa Rica" width="200" height="40" />' +
      "</a>" +
      '<a href="https://emate.ucr.ac.cr/" target="_blank" rel="noopener noreferrer" title="Escuela de Matemática">' +
      '<img class="logo-mate logo-desktop" src="' +
      logos +
      'logo-mate.png" alt="Escuela de Matemática, Universidad de Costa Rica" width="220" height="56" />' +
      '<img class="logo-mate logo-mobile" src="' +
      logos +
      'acronimo-blanco-movil.png" alt="Escuela de Matemática, Universidad de Costa Rica" width="160" height="40" />' +
      "</a>" +
      "</div>";

    document.body.insertBefore(header, document.body.firstChild);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();
