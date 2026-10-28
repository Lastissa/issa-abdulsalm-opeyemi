/* Site interactions: theme, navigation, toasts, JSON forms, and HTMX glue. */
(function () {
  "use strict";

  var root = document.documentElement;
  var toastTitles = {
    success: "Done",
    error: "Something went wrong",
    warning: "Heads up",
    info: "Note",
    debug: "Debug",
  };

  function hideSplash() {
    var splash = document.getElementById("splash");
    if (splash) {
      splash.classList.add("is-hidden");
    }
    try {
      window.sessionStorage.setItem("splashSeen", "1");
    } catch (error) {
      /* Storage can be disabled; the splash still closes. */
    }

    window.setTimeout(function () {
      root.classList.remove("is-loading");
      if (splash) {
        splash.classList.add("is-gone");
        splash.setAttribute("aria-hidden", "true");
      }
    }, 320);
  }

  if (document.readyState === "complete") {
    hideSplash();
  } else {
    window.addEventListener("load", hideSplash, { once: true });
  }

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
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (meta) {
      var media = meta.getAttribute("media") || "";
      if (
        (theme === "dark" && media.indexOf("dark") !== -1) ||
        (theme === "light" && media.indexOf("light") !== -1)
      ) {
        meta.setAttribute("content", theme === "dark" ? "#070b10" : "#f7f9fc");
      }
    });
  }

  function syncThemeButton(theme) {
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      var isDark = theme === "dark";
      button.setAttribute("aria-pressed", isDark ? "true" : "false");
      button.setAttribute(
        "aria-label",
        isDark ? "Switch to light theme" : "Switch to dark theme"
      );
    });
  }

  function normalizeStatus(status) {
    var value = String(status || "info").toLowerCase();
    if (value === "danger") {
      return "error";
    }
    return toastTitles[value] ? value : "info";
  }

  window.showToast = function (status, detail, title) {
    if (!detail) {
      return;
    }
    window.dispatchEvent(
      new CustomEvent("toast", {
        detail: {
          status: normalizeStatus(status),
          detail: String(detail),
          title: title || "",
        },
      })
    );
  };

  /* ---------- Theme ---------- */

  var currentTheme = root.getAttribute("data-theme") || systemTheme();
  syncThemeButton(currentTheme);
  syncThemeColor(currentTheme);

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-theme-toggle]");
    if (!toggle) {
      return;
    }
    var next =
      (root.getAttribute("data-theme") || systemTheme()) === "dark"
        ? "light"
        : "dark";
    root.setAttribute("data-theme", next);
    safeStorageSet("theme", next);
    syncThemeButton(next);
    syncThemeColor(next);
  });

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

  /* ---------- Mobile navigation ---------- */

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

  /* ---------- Dashboard sidebar ---------- */

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

  /* ---------- Delegated interactions (also work after HTMX swaps) ---------- */

  document.addEventListener("click", function (event) {
    var passwordButton = event.target.closest("[data-password-toggle]");
    if (passwordButton) {
      var target = document.getElementById(
        passwordButton.getAttribute("data-password-toggle")
      );
      if (target) {
        var isPassword = target.getAttribute("type") === "password";
        target.setAttribute("type", isPassword ? "text" : "password");
        passwordButton.textContent = isPassword ? "Hide" : "Show";
        passwordButton.setAttribute(
          "aria-label",
          isPassword ? "Hide password" : "Show password"
        );
      }
      return;
    }

    var imageButton = event.target.closest("[data-toggle-image]");
    if (imageButton) {
      var imageTarget = document.getElementById(
        imageButton.getAttribute("data-toggle-image")
      );
      if (imageTarget) {
        var isVisible = imageTarget.classList.toggle("is-visible");
        imageButton.setAttribute(
          "aria-expanded",
          isVisible ? "true" : "false"
        );
        if (isVisible) {
          var input = imageTarget.querySelector("input");
          if (input) {
            input.focus();
          }
        }
      }
      return;
    }

    var fullscreenButton = event.target.closest("[data-fullscreen]");
    if (fullscreenButton) {
      var frameTarget = document.getElementById(
        fullscreenButton.getAttribute("data-fullscreen")
      );
      if (frameTarget) {
        var frame = frameTarget.closest(".browser-frame") || frameTarget;
        if (frame.requestFullscreen) {
          frame.requestFullscreen();
        }
      }
      return;
    }

    var copyButton = event.target.closest("[data-copy-link]");
    if (copyButton) {
      var url = copyButton.getAttribute("data-copy-link") || window.location.href;
      var original =
        copyButton.getAttribute("data-label") || copyButton.textContent.trim();
      var done = function () {
        copyButton.textContent = "Copied";
        window.setTimeout(function () {
          copyButton.textContent = original;
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done).catch(function () {
          window.prompt("Copy this link:", url);
        });
      } else {
        window.prompt("Copy this link:", url);
      }
      return;
    }

    var dismissButton = event.target.closest("[data-dismiss]");
    if (dismissButton) {
      var message = dismissButton.closest(".message");
      if (message) {
        message.remove();
      }
    }
  });

  document.addEventListener(
    "error",
    function (event) {
      var image = event.target;
      if (image && image.matches && image.matches("img[data-hide-on-error]")) {
        var wrapper = image.closest(".post-media");
        if (wrapper) {
          wrapper.remove();
        }
      }
    },
    true
  );

  document.addEventListener("input", function (event) {
    var field = event.target;
    if (field.matches && field.matches("[data-autogrow]")) {
      field.style.height = "auto";
      field.style.height = Math.min(field.scrollHeight, 320) + "px";
    }

    if (field.matches && field.matches("[data-counter]")) {
      var limit = parseInt(field.getAttribute("data-counter"), 10);
      var counter =
        document.getElementById(
          field.getAttribute("data-counter-target") || ""
        ) || field.parentElement.querySelector("[data-counter-output]");
      if (counter && limit) {
        var remaining = limit - field.value.length;
        counter.textContent = remaining + " left";
        counter.classList.toggle("is-near-limit", remaining < 200);
      }
    }
  });

  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!form.matches || !form.matches("form[data-confirm]")) {
      return;
    }
    var text = form.getAttribute("data-confirm") || "Are you sure?";
    if (!window.confirm(text)) {
      event.preventDefault();
    }
  });

  function initAutogrow() {
    document.querySelectorAll("[data-autogrow]").forEach(function (field) {
      field.style.height = "auto";
      field.style.height = Math.min(field.scrollHeight, 320) + "px";
    });
  }

  function initCounters() {
    document.querySelectorAll("[data-counter]").forEach(function (field) {
      var limit = parseInt(field.getAttribute("data-counter"), 10);
      var counter =
        document.getElementById(
          field.getAttribute("data-counter-target") || ""
        ) || field.parentElement.querySelector("[data-counter-output]");
      if (!counter || !limit) {
        return;
      }
      var remaining = limit - field.value.length;
      counter.textContent = remaining + " left";
      counter.classList.toggle("is-near-limit", remaining < 200);
    });
  }

  initAutogrow();
  initCounters();

  /* Close open <details> menus when clicking elsewhere. */
  document.addEventListener("click", function (event) {
    document.querySelectorAll("details.post-menu[open]").forEach(function (menu) {
      if (!menu.contains(event.target)) {
        menu.removeAttribute("open");
      }
    });
  });

  /* ---------- Alpine components ---------- */

  document.addEventListener("alpine:init", function () {
    if (!window.Alpine) {
      return;
    }

    window.Alpine.data("toastRegion", function () {
      return {
        toasts: [],
        _nextId: 0,
        _timers: {},
        init: function () {
          var self = this;
          document
            .querySelectorAll("[data-toast-source] [data-toast-status]")
            .forEach(function (node) {
              self.push({
                status: node.getAttribute("data-toast-status"),
                detail: node.getAttribute("data-toast-detail"),
              });
            });
          var source = document.querySelector("[data-toast-source]");
          if (source) {
            source.remove();
          }
        },
        push: function (payload) {
          if (!payload || !payload.detail) {
            return;
          }
          var status = normalizeStatus(payload.status);
          var id = ++this._nextId;
          this.toasts.push({
            id: id,
            status: status,
            title: payload.title || toastTitles[status],
            detail: String(payload.detail),
          });
          this._timers[id] = window.setTimeout(
            this.dismiss.bind(this, id),
            5600
          );
        },
        pause: function (id) {
          if (this._timers[id]) {
            window.clearTimeout(this._timers[id]);
            delete this._timers[id];
          }
        },
        resume: function (id) {
          if (this._timers[id]) {
            return;
          }
          this._timers[id] = window.setTimeout(
            this.dismiss.bind(this, id),
            3200
          );
        },
        dismiss: function (id) {
          if (this._timers[id]) {
            window.clearTimeout(this._timers[id]);
            delete this._timers[id];
          }
          this.toasts = this.toasts.filter(function (toast) {
            return toast.id !== id;
          });
        },
      };
    });

    function formBody(form) {
      var hasFile = false;
      form.querySelectorAll('input[type="file"]').forEach(function (input) {
        if (input.files && input.files.length) {
          hasFile = true;
        }
      });
      if (hasFile) {
        return new FormData(form);
      }
      // JSON endpoints only need text fields. URL-encoding avoids a multipart
      // request, which is unnecessary and can stall behind some dev servers.
      return new URLSearchParams(new FormData(form));
    }

    window.Alpine.data("loginForm", function (options) {
      return {
        loading: false,
        error: "",
        submit: async function (event) {
          if (this.loading) {
            return;
          }
          this.loading = true;
          this.error = "";
          var succeeded = false;

          var form = event.currentTarget;
          var button = form.querySelector('button[type="submit"]');
          if (document.activeElement instanceof HTMLElement) {
            document.activeElement.blur();
          }
          if (button) {
            button.disabled = true;
            button.setAttribute("aria-busy", "true");
          }

          try {
            var csrfField = form.querySelector("[name=csrfmiddlewaretoken]");
            var response = await fetch(form.action || window.location.href, {
              method: "POST",
              body: formBody(form),
              headers: {
                "X-Requested-With": "XMLHttpRequest",
                Accept: "application/json",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "X-CSRFToken": csrfField ? csrfField.value : "",
              },
              credentials: "same-origin",
            });
            var data = await response.json().catch(function () {
              return {
                status: "error",
                detail: "The server returned an unexpected response.",
              };
            });

            if (data.status === "ok") {
              succeeded = true;
              window.showToast("success", data.detail || "Signed in.");
              window.location.assign(
                data.redirect || (options && options.next) || "/custom-admin/"
              );
              return;
            }

            this.error = data.detail || "Those credentials did not work.";
            window.showToast("error", this.error);
          } catch (error) {
            this.error =
              "Network error. Check your connection and try again.";
            window.showToast("error", this.error);
          } finally {
            // Keep the button locked while the browser follows a successful
            // redirect so a second click cannot submit the form again.
            if (!succeeded) {
              this.loading = false;
              if (button) {
                button.disabled = false;
                button.removeAttribute("aria-busy");
              }
            }
          }
        },
      };
    });

    window.Alpine.data("asyncForm", function (options) {
      return {
        loading: false,
        submit: async function (event) {
          if (this.loading) {
            return;
          }
          this.loading = true;
          var succeeded = false;

          var form = event.currentTarget;
          var button = form.querySelector('button[type="submit"]');
          if (document.activeElement instanceof HTMLElement) {
            document.activeElement.blur();
          }
          if (button) {
            button.disabled = true;
            button.setAttribute("aria-busy", "true");
          }

          try {
            var csrfField = form.querySelector("[name=csrfmiddlewaretoken]");
            var response = await fetch(form.action, {
              method: "POST",
              body: formBody(form),
              headers: {
                "X-Requested-With": "XMLHttpRequest",
                Accept: "application/json",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "X-CSRFToken": csrfField ? csrfField.value : "",
              },
              credentials: "same-origin",
            });
            var data = await response.json().catch(function () {
              return {
                status: "error",
                detail: "The server returned an unexpected response.",
              };
            });

            if (data.status === "ok") {
              succeeded = true;
              window.showToast("success", data.detail || "Done.");
              window.location.assign(
                data.redirect || (options && options.redirect) || "/"
              );
              return;
            }

            window.showToast(
              "error",
              data.detail || "The request could not be completed."
            );
          } catch (error) {
            window.showToast(
              "error",
              "Network error. Check your connection and try again."
            );
          } finally {
            if (!succeeded) {
              this.loading = false;
              if (button) {
                button.disabled = false;
                button.removeAttribute("aria-busy");
              }
            }
          }
        },
      };
    });
  });

  /* ---------- HTMX glue ---------- */

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    var element = event.detail.elt;
    if (!element || !element.getAttribute || !element.getAttribute("hx-post")) {
      return;
    }
    var button = element.querySelector('button[type="submit"]');
    if (button) {
      button.disabled = true;
      button.setAttribute("aria-busy", "true");
    }
  });

  document.body.addEventListener("htmx:afterRequest", function (event) {
    var element = event.detail.elt;
    if (!element || !element.querySelector) {
      return;
    }
    var button = element.querySelector('button[type="submit"]');
    if (button) {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  });

  document.body.addEventListener("htmx:afterSwap", function () {
    initAutogrow();
    initCounters();
  });

  document.body.addEventListener("htmx:responseError", function () {
    window.showToast("error", "The request failed. Please try again.");
  });

  document.body.addEventListener("htmx:sendError", function () {
    window.showToast("error", "Network error. Check your connection.");
  });
})();
