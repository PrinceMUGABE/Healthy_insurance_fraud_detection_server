document.addEventListener("DOMContentLoaded", () => {
    const appDiv = document.getElementById("app");
    appDiv.innerHTML = "<p>Healthy Insurance Fraude Detection System</p>";

    const mobileMenuButton = document.querySelector(".mobile-menu-button");
    const mobileMenu = document.querySelector(".mobile-menu");

    mobileMenuButton.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
    });
});