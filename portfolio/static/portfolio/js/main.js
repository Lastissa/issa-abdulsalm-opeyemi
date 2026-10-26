/* Small, dependency-free interactions for the whole site. */
(function () {
  "use strict";

  var root = document.documentElement;

  function safeStorageGet(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      /* Storage can be disabled; the toggle still works for this page. */
    }
  }

  function systemTheme() {
    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function syncThemeColor(theme) {
    var metas = document.querySelectorAll('meta[name="theme-color"]');
    metas.forEach(function (meta) {
      var media = meta.getAttribute("media") || "";
      if (
        (theme === "dark" && media.indexOf("dark") !== -1) ||
        (theme === "light" && media.indexOf("light") !== -1)
      ) {
        meta.setAttribute("content", theme === "dark" ? "#070b10" : "#ffffff");
      }
    });
  }

  function syncThemeButton(theme) {
    var button = document.querySelector("[data-theme-toggle]");
    if (!button) {
      return;
    }
    var isDark = theme === "dark";
    button.setAttribute("aria-pressed", isDark ? "true" : "false");
    button.setAttribute(
      "aria-label",
      isDark ? "Switch to light theme" : "Switch to dark theme"
    );
  }

  var currentTheme = root.getAttribute("data-theme") || systemTheme();
  syncThemeButton(currentTheme);
  syncThemeColor(currentTheme);

  var themeToggle = document.querySelector("[data-theme-toggle]");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var next =
        (root.getAttribute("data-theme") || systemTheme()) === "dark"
          ? "light"
          : "dark";
      root.setAttribute("data-theme", next);
      safeStorageSet("theme", next);
      syncThemeButton(next);
      syncThemeColor(next);
    });
  }

  if (window.matchMedia) {
    var media = window.matchMedia("(prefers-color-scheme: dark)");
    var onSystemChange = function (event) {
      if (safeStorageGet("theme")) {
        return;
      }
      var next = event.matches ? "dark" : "light";
      root.setAttribute("data-theme", next);
      syncThemeButton(next);
      syncThemeColor(next);
    };
    if (media.addEventListener) {
      media.addEventListener("change", onSystemChange);
    } else if (media.addListener) {
      media.addListener(onSystemChange);
    }
  }

  /* Mobile primary navigation */
  var navToggle = document.querySelector("[data-nav-toggle]");
  var primaryNav = document.getElementById("primary-nav");
  if (navToggle && primaryNav) {
    var closeNav = function () {
      primaryNav.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "Open menu");
      document.body.classList.remove("nav-open");
    };

    navToggle.addEventListener("click", function () {
      var isOpen = primaryNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      navToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
      document.body.classList.toggle("nav-open", isOpen);
    });

    primaryNav.addEventListener("click", function (event) {
      if (event.target.tagName === "A") {
        closeNav();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeNav();
      }
    });

    document.addEventListener("click", function (event) {
      if (
        primaryNav.classList.contains("is-open") &&
        !primaryNav.contains(event.target) &&
        !navToggle.contains(event.target)
      ) {
        closeNav();
      }
    });
  }

  /* Owner dashboard sidebar on small screens */
  var adminToggle = document.querySelector("[data-admin-toggle]");
  var adminSidebar = document.querySelector("[data-admin-sidebar]");
  if (adminToggle && adminSidebar) {
    adminToggle.addEventListener("click", function () {
      var isOpen = adminSidebar.classList.toggle("is-open");
      adminToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
    adminSidebar.addEventListener("click", function (event) {
      if (event.target.tagName === "A") {
        adminSidebar.classList.remove("is-open");
        adminToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* Password visibility */
  document.querySelectorAll("[data-password-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-password-toggle"));
      if (!target) {
        return;
      }
      var isPassword = target.getAttribute("type") === "password";
      target.setAttribute("type", isPassword ? "text" : "password");
      button.textContent = isPassword ? "Hide" : "Show";
      button.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
      );
    });
  });

  /* Auto-growing textareas */
  document.querySelectorAll("[data-autogrow]").forEach(function (field) {
    var resize = function () {
      field.style.height = "auto";
      field.style.height = Math.min(field.scrollHeight, 320) + "px";
    };
    field.addEventListener("input", resize);
    resize();
  });

  /* Composer character counter */
  document.querySelectorAll("[data-counter]").forEach(function (field) {
    var limit = parseInt(field.getAttribute("data-counter"), 10);
    var counter = document.getElementById(field.getAttribute("data-counter-target") || "");
    if (!counter) {
      counter = field.parentElement.querySelector("[data-counter-output]");
    }
    if (!counter || !limit) {
      return;
    }
    var update = function () {
      var remaining = limit - field.value.length;
      counter.textContent = remaining + " left";
      counter.classList.toggle("is-near-limit", remaining < 200);
    };
    field.addEventListener("input", update);
    update();
  });

  /* Toggle the image URL field in the feed composer */
  document.querySelectorAll("[data-toggle-image]").forEach(function (button) {
    button.addEventListener("click", function () {
      var targetId = button.getAttribute("data-toggle-image");
      var target = document.getElementById(targetId);
      if (!target) {
        return;
      }
      var isVisible = target.classList.toggle("is-visible");
      button.setAttribute("aria-expanded", isVisible ? "true" : "false");
      if (isVisible) {
        var input = target.querySelector("input");
        if (input) {
          input.focus();
        }
      }
    });
  });

  /* Remove broken external feed images without leaving a blank panel. */
  document.querySelectorAll("img[data-hide-on-error]").forEach(function (image) {
    image.addEventListener("error", function () {
      var wrapper = image.closest(".post-media");
      if (wrapper) {
        wrapper.remove();
      }
    });
  });

  /* Fullscreen iframe preview */
  document.querySelectorAll("[data-fullscreen]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-fullscreen"));
      if (!target) {
        return;
      }
      var frame = target.closest(".browser-frame") || target;
      if (frame.requestFullscreen) {
        frame.requestFullscreen();
      }
    });
  });

  /* Copy the current post link */
  document.querySelectorAll("[data-copy-link]").forEach(function (button) {
    button.addEventListener("click", function () {
      var url = button.getAttribute("data-copy-link") || window.location.href;
      var original = button.getAttribute("data-label") || button.textContent.trim();
      var done = function () {
        button.textContent = "Copied";
        window.setTimeout(function () {
          button.textContent = original;
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done).catch(function () {
          window.prompt("Copy this link:", url);
        });
      } else {
        window.prompt("Copy this link:", url);
      }
    });
  });

  /* Dismiss messages */
  document.querySelectorAll("[data-dismiss]").forEach(function (button) {
    button.addEventListener("click", function () {
      var message = button.closest(".message");
      if (message) {
        message.remove();
      }
    });
  });

  /* Confirm destructive actions */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var text = form.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(text)) {
        event.preventDefault();
      }
    });
  });

  /* Close open <details> menus when clicking elsewhere. */
  document.addEventListener("click", function (event) {
    document.querySelectorAll("details.post-menu[open]").forEach(function (menu) {
      if (!menu.contains(event.target)) {
        menu.removeAttribute("open");
      }
    });
  });
})();
