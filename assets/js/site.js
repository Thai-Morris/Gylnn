"use strict";

const mobileNavigation = document.querySelector(".mobile-nav");

if (mobileNavigation) {
  mobileNavigation.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.closest("a")) {
      mobileNavigation.removeAttribute("open");
    }
  });
}

const currentYear = document.querySelector("[data-current-year]");

if (currentYear) {
  const year = String(new Date().getFullYear());
  currentYear.dateTime = year;
  currentYear.textContent = year;
}
