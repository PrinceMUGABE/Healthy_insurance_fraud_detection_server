const sidebar = document.getElementById('sidebar');
const sidebarCollapse = document.getElementById('sidebarCollapse');
const hamburgerIcon = document.querySelector('#sidebarCollapse i');

sidebarCollapse.addEventListener('click', () => {
    sidebar.classList.toggle('active');

    // Update hamburger icon color and position
    if (sidebar.classList.contains('active')) {
        hamburgerIcon.style.color = '#000'; // Set color to black when sidebar is active
        sidebarCollapse.style.left = `${sidebar.offsetWidth}px`; // Move hamburger to the right edge of the sidebar
    } else {
        hamburgerIcon.style.color = '#fff'; // Set color to white when sidebar is inactive
        sidebarCollapse.style.left = '20px'; // Move hamburger back to its original position
    }
});

// Get the button that opens the modal
const editButtons = document.querySelectorAll('.btn-primary');

// Get the <span> element that closes the modal
const closeBtn = document.getElementsByClassName('close')[0];


