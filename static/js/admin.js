(function () {
  "use strict";

  function openAdminTab(tabId) {
    document.querySelectorAll(".admin-tab-panel").forEach((panel) => {
      panel.classList.remove("active");
    });
    document.querySelectorAll(".admin-tab-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    document.getElementById(tabId)?.classList.add("active");
    document.getElementById("btn-" + tabId)?.classList.add("active");
    localStorage.setItem("activeAdminTab", tabId);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("admin-dashboard");
    if (!root) return;

    const tabMap = { prices: "prices-tab", buyers: "buyers-tab" };
    const serverTab = root.dataset.activeTab;
    const savedTab = localStorage.getItem("activeAdminTab");
    const initialTab = tabMap[serverTab] || savedTab || "prices-tab";
    openAdminTab(initialTab === "requests-tab" ? "prices-tab" : initialTab);

    document.querySelectorAll(".admin-tab-btn[data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => openAdminTab(btn.dataset.tab));
    });

    const darkModeToggle = document.getElementById("darkModeToggle");
    if (darkModeToggle) {
      darkModeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"));
      });
    }
  });
})();
