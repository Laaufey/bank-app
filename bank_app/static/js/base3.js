// DROP DOWN FOR NAV BAR 

const dropDownButton = document.getElementById("drop-down-link")


dropDownButton.addEventListener("click", toggleHidden);

function toggleHidden() {
    const subMenu = document.querySelector(".sub-menu")
    subMenu.classList.toggle("hidden")
};