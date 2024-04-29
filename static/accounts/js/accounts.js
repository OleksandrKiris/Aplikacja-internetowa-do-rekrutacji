
    document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    menuToggle.addEventListener('click', function() {
    // This will toggle the 'active' class to show or hide the sidebar
    sidebar.classList.toggle('active');
});
});

