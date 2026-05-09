(function () {
  var storageKey = "poleposition-doc-font-size";
  var defaultSize = "default";
  var sizes = [
    { value: "small", label: "Small" },
    { value: "default", label: "Default" },
    { value: "large", label: "Large" },
    { value: "extra-large", label: "Extra large" },
  ];

  function isSupportedSize(value) {
    return sizes.some(function (size) {
      return size.value === value;
    });
  }

  function readStoredSize() {
    try {
      var stored = window.localStorage.getItem(storageKey);
      return isSupportedSize(stored) ? stored : defaultSize;
    } catch (_error) {
      return defaultSize;
    }
  }

  function applySize(value) {
    var selectedSize = isSupportedSize(value) ? value : defaultSize;
    document.documentElement.dataset.poleposFontSize = selectedSize;

    try {
      window.localStorage.setItem(storageKey, selectedSize);
    } catch (_error) {
      // Browsers can block storage in private or restricted contexts.
    }
  }

  function buildFontSizeControl() {
    if (document.querySelector(".polepos-font-size")) {
      return;
    }

    var headerInner = document.querySelector(".md-header__inner");
    if (!headerInner) {
      return;
    }

    var wrapper = document.createElement("div");
    wrapper.className = "polepos-font-size";

    var label = document.createElement("label");
    label.className = "polepos-font-size__label";
    label.htmlFor = "polepos-font-size-select";
    label.textContent = "Text";

    var select = document.createElement("select");
    select.id = "polepos-font-size-select";
    select.className = "polepos-font-size__select";
    select.setAttribute("aria-label", "Text size");

    sizes.forEach(function (size) {
      var option = document.createElement("option");
      option.value = size.value;
      option.textContent = size.label;
      select.appendChild(option);
    });

    select.value = readStoredSize();
    select.addEventListener("change", function (event) {
      applySize(event.target.value);
    });

    wrapper.appendChild(label);
    wrapper.appendChild(select);
    headerInner.appendChild(wrapper);
  }

  applySize(readStoredSize());

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildFontSizeControl);
  } else {
    buildFontSizeControl();
  }
})();
