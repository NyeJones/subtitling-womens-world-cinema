document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".site-navbar");

    if (!navbar) return;

    function updateNavbar() {
        navbar.classList.toggle("scrolled", window.scrollY > 50);
    }

    window.addEventListener("scroll", updateNavbar);
    updateNavbar();
});