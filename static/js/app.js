/**
 * GitHub Trending Repositories - Frontend JavaScript
 * Handles theme toggle, search debouncing, sorting, and UI interactions.
 */

(function () {
  "use strict";

  // ========================================
  // Theme Management
  // ========================================
  const themeToggle = document.getElementById("theme-toggle");
  const htmlElement = document.documentElement;

  if (themeToggle) {
    const sunIcon = themeToggle.querySelector(".sun-icon");
    const moonIcon = themeToggle.querySelector(".moon-icon");

    function applyTheme(theme) {
      if (theme === "dark") {
        htmlElement.classList.add("dark");
        if (sunIcon) sunIcon.style.display = "none";
        if (moonIcon) moonIcon.style.display = "block";
        localStorage.setItem("theme", "dark");
      } else {
        htmlElement.classList.remove("dark");
        if (sunIcon) sunIcon.style.display = "block";
        if (moonIcon) moonIcon.style.display = "none";
        localStorage.setItem("theme", "light");
      }
    }

    // Initialize theme
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
      applyTheme("dark");
    } else {
      applyTheme("light");
    }

    // Toggle on click
    themeToggle.addEventListener("click", function () {
      const isDark = htmlElement.classList.contains("dark");
      applyTheme(isDark ? "light" : "dark");
    });

    // Listen for system theme changes (only if no saved preference)
    if (!savedTheme) {
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", (e) => {
          applyTheme(e.matches ? "dark" : "light");
        });
    }
  }

  // ========================================
  // Footer Year
  // ========================================
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // ========================================
  // Debounced Search
  // ========================================
  const searchInput = document.getElementById("search");
  const filterForm = document.getElementById("filter-form");

  if (searchInput && filterForm) {
    let searchTimeout;

    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function () {
        filterForm.submit();
      }, 500);
    });

    // Also submit on Enter key in search
    searchInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        clearTimeout(searchTimeout);
        filterForm.submit();
      }
    });
  }

  // ========================================
  // Client-Side Sorting
  // ========================================
  window.sortRepositories = function (sort) {
    const url = new URL(window.location);
    url.searchParams.set("sort", sort);
    url.searchParams.set("page", "1");
    window.location.href = url.toString();
  };

  // ========================================
  // Intersection Observer for Card Animations
  // ========================================
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Initialize card animations
  function initCardAnimations() {
    const cards = document.querySelectorAll(".repo-card");
    cards.forEach((card, index) => {
      card.style.opacity = "0";
      card.style.transform = "translateY(20px)";
      card.style.transition = `opacity 0.4s ease ${index * 0.05}s, transform 0.4s ease ${index * 0.05}s`;
      observer.observe(card);
    });
  }

  // Run on load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCardAnimations);
  } else {
    initCardAnimations();
  }

  // ========================================
  // Accessibility: Enhance focus states
  // ========================================
  const focusableElements = document.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  focusableElements.forEach((el) => {
    el.addEventListener("keydown", function (e) {
      if (e.key === "Tab") {
        this.classList.add("focus-visible");
      }
    });

    el.addEventListener("blur", function () {
      this.classList.remove("focus-visible");
    });
  });

})();
