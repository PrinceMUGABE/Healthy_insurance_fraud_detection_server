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


// Get the modal
const modal = document.getElementById('editUserModal');

// Get the button that opens the modal
const editButtons = document.querySelectorAll('.btn-primary');

// Get the <span> element that closes the modal
const closeBtn = document.getElementsByClassName('close')[0];

// When the user clicks on the button, open the modal
editButtons.forEach(button => {
  button.addEventListener('click', function() {
    modal.style.display = 'block';
  });
});

// When the user clicks on <span> (x), close the modal
closeBtn.onclick = function() {
  modal.style.display = 'none';
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target === modal) {
    modal.style.display = 'none';
  }
};



function editUser(userId) {
    // Fetch user data based on the userId
    fetch(`/user/${userId}/data/`)
        .then(response => response.json())
        .then(userData => {
            // Populate the form fields with user data
            document.getElementById('userId').value = userData.id;
            document.getElementById('editUsername').value = userData.username;
            document.getElementById('editEmail').value = userData.email;
            document.getElementById('role').value = userData.role;

            // Show the modal
            modal.style.display = 'block';
        })
        .catch(error => console.error('Error fetching user data:', error));
}



// Fetch and display today's users
function fetchTodayUsers() {
    fetch('/user/today/') // Assuming this endpoint returns today's users
        .then(response => response.json())
        .then(data => {
            const todayUsersList = document.getElementById('todayUsersList');
            todayUsersList.innerHTML = ''; // Clear existing content

            // Iterate through the today's users data and create list items
            data.users.forEach(user => {
                const li = document.createElement('li');
                li.textContent = `${user.username} - ${user.email}`;
                todayUsersList.appendChild(li);
            });

            // Display the today's users division
            document.querySelector('.today-users').style.display = 'block';
        })
        .catch(error => console.error('Error fetching today\'s users:', error));
}

// Call the function to fetch and display today's users
fetchTodayUsers();
