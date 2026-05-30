const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");
const navbar = document.querySelector(".navbar");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const isOpen = navLinks.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
}

const revealItems = document.querySelectorAll(".reveal");
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.2 }
);

revealItems.forEach((item) => observer.observe(item));

window.addEventListener("scroll", () => {
  if (!navbar) return;
  navbar.classList.toggle("scrolled", window.scrollY > 10);
});

const year = document.querySelector("#year");
if (year) {
  year.textContent = new Date().getFullYear();
}

const form = document.querySelector("#transportForm");
const message = document.querySelector("#formMessage");

if (form && message) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    message.textContent = window.__ ? window.__("form_thanks") : "Thanks! Our dispatch team will contact you shortly.";
    form.reset();
  });
}

const sidebarToggle = document.querySelector(".sidebar-toggle");
const sidebar = document.querySelector(".sidebar");

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });
}

// Close sidebar when clicking on a link
const sidebarLinks = document.querySelectorAll(".sidebar-nav a");
sidebarLinks.forEach(link => {
  link.addEventListener("click", () => {
    sidebar.classList.remove("open");
  });
});

// Global SMS Toast Notification Generator
window.showSmsToast = function(sender, message) {
  let toastContainer = document.getElementById("smsToastContainer");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "smsToastContainer";
    toastContainer.style.position = "fixed";
    toastContainer.style.top = "20px";
    toastContainer.style.right = "20px";
    toastContainer.style.zIndex = "9999";
    toastContainer.style.display = "flex";
    toastContainer.style.flexDirection = "column";
    toastContainer.style.gap = "10px";
    document.body.appendChild(toastContainer);
  }
  
  const toast = document.createElement("div");
  toast.className = "sms-toast-card";
  toast.style.background = "#0f1f16";
  toast.style.color = "#e1ebe3";
  toast.style.borderLeft = "5px solid #2f7d32";
  toast.style.padding = "14px 18px";
  toast.style.borderRadius = "10px";
  toast.style.boxShadow = "0 10px 30px rgba(0,0,0,0.25)";
  toast.style.maxWidth = "320px";
  toast.style.animation = "slide-in-right 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards";
  toast.style.fontFamily = "'Inter', sans-serif";
  
  toast.innerHTML = `
    <div style="display:flex; justify-content:space-between; margin-bottom: 6px; font-size:0.75rem; font-weight:700; color:#b7c6bc; letter-spacing: 0.05em;">
      <span>${window.__ ? window.__("sms_toast") : "💬 SIMULATED SMS"}</span>
      <span>${sender}</span>
    </div>
    <div style="font-size:0.85rem; line-height:1.4; font-weight: 500;">${message}</div>
  `;
  
  toastContainer.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = "slide-out-right 0.3s ease forwards";
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 6000);
};
