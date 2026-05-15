import React, {useEffect} from "react";

const STORAGE_KEY = "poleposition-doc-font-size";
const DEFAULT_SIZE = "default";
const SIZES = [
  {value: "small", label: "Small"},
  {value: "default", label: "Default"},
  {value: "large", label: "Large"},
  {value: "extra-large", label: "Extra large"},
];

function isSupportedSize(value) {
  return SIZES.some((size) => size.value === value);
}

function readStoredSize() {
  try {
    const storedSize = window.localStorage.getItem(STORAGE_KEY);
    return isSupportedSize(storedSize) ? storedSize : DEFAULT_SIZE;
  } catch (_error) {
    return DEFAULT_SIZE;
  }
}

function applySize(value) {
  const selectedSize = isSupportedSize(value) ? value : DEFAULT_SIZE;
  document.documentElement.dataset.poleposFontSize = selectedSize;

  try {
    window.localStorage.setItem(STORAGE_KEY, selectedSize);
  } catch (_error) {
    // Storage can be unavailable in private or restricted browser contexts.
  }
}

function buildFontSizeControl() {
  if (document.querySelector(".polepos-font-size")) {
    return true;
  }

  const navbarRight = document.querySelector(".navbar__items--right");
  if (!navbarRight) {
    return false;
  }

  const wrapper = document.createElement("div");
  wrapper.className = "polepos-font-size";

  const label = document.createElement("label");
  label.className = "polepos-font-size__label";
  label.htmlFor = "polepos-font-size-select";
  label.textContent = "Aa";

  const select = document.createElement("select");
  select.id = "polepos-font-size-select";
  select.className = "polepos-font-size__select";
  select.setAttribute("aria-label", "Text size");
  select.title = "Text size";

  SIZES.forEach((size) => {
    const option = document.createElement("option");
    option.value = size.value;
    option.textContent = size.label;
    select.appendChild(option);
  });

  select.value = readStoredSize();
  select.addEventListener("change", (event) => {
    applySize(event.target.value);
  });

  wrapper.appendChild(label);
  wrapper.appendChild(select);

  navbarRight.insertBefore(wrapper, navbarRight.firstChild);
  return true;
}

export default function Root({children}) {
  useEffect(() => {
    applySize(readStoredSize());

    if (buildFontSizeControl()) {
      return undefined;
    }

    const observer = new MutationObserver(() => {
      if (buildFontSizeControl()) {
        observer.disconnect();
      }
    });
    observer.observe(document.body, {childList: true, subtree: true});

    return () => observer.disconnect();
  }, []);

  return <>{children}</>;
}
