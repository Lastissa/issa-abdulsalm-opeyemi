/*
  main.js
  Deliberately tiny: mobile nav toggle + theme toggle. No framework,
  no bundler -- a single <script defer> tag is enough for a site this
  size. See workflow.md, decision C4.

  Note: the *initial* theme (dark vs. light, from localStorage or
  system preference) is applied by a small inline script in <head>,
  before this file even loads -- that's what prevents a flash of the
  wrong theme on page load. This file only handles the click.
*/
(function () {
  "use strict";

  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");

  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var isOpen = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    links.addEventListener("click", function (event) {
      if (event.target.tagName === "A") {
        links.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  var themeToggle = document.querySelector(".theme-toggle");

  if (themeToggle) {
    var syncThemeToggle = function (isLight) {
      themeToggle.setAttribute("aria-pressed", isLight ? "true" : "false");
      themeToggle.setAttribute(
        "aria-label",
        isLight ? "Switch to dark theme" : "Switch to light theme"
      );
    };

    // The inline anti-flicker script in <head> may already have set
    // data-theme="light" before this file ran -- sync the button's
    // a11y state to match on load, not just after a click.
    syncThemeToggle(document.documentElement.getAttribute("data-theme") === "light");

    themeToggle.addEventListener("click", function () {
      var root = document.documentElement;
      var goingLight = root.getAttribute("data-theme") !== "light";

      if (goingLight) {
        root.setAttribute("data-theme", "light");
      } else {
        root.removeAttribute("data-theme");
      }

      syncThemeToggle(goingLight);

      try {
        localStorage.setItem("theme", goingLight ? "light" : "dark");
      } catch (e) {
        /* Private browsing / storage disabled -- toggle still works
           for this page load, it just won't persist. */
      }
    });
  }
})();
