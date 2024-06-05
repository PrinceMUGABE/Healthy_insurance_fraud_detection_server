/*===== FOCUS =====*/
const inputs = document.querySelectorAll(".form__input")

/*=== Add focus ===*/
function addfocus(){
    let parent = this.parentNode.parentNode
    parent.classList.add("focus")
}

/*=== Remove focus ===*/
function remfocus(){
    let parent = this.parentNode.parentNode
    if(this.value == ""){
        parent.classList.remove("focus")
    }
}

/*=== To call function===*/
inputs.forEach(input=>{
    input.addEventListener("focus",addfocus)
    input.addEventListener("blur",remfocus)
})

// Function to load sign-in page
function loadSignInPage() {
    fetch('/get_login_page/')
        .then(response => response.text())
        .then(html => {
            document.getElementById('main-content').innerHTML = html;
        })
        .catch(error => console.error('Error:', error));
}

// Event handler for sign-in page link
document.getElementById('signin-navbar').addEventListener('click', function(event) {
    event.preventDefault();
    // Remove event listener to prevent multiple clicks
    document.getElementById('signin-navbar').removeEventListener('click', signInPageHandler);
    // Load sign-in page
    loadSignInPage();
});

// Initial event listener setup
document.getElementById('signin-navbar').addEventListener('click', signInPageHandler);

// Function to load contact form
function loadContactForm() {
    document.getElementById('main-content').innerHTML = document.getElementById('contact-section').innerHTML;
}

// Event handler for contact link
document.getElementById('contact-navbar').addEventListener('click', function(event) {
    event.preventDefault();
    // Load contact form
    loadContactForm();
});

// Function to handle form submission
document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const jsonData = {};
    formData.forEach((value, key) => {jsonData[key] = value});
    fetch('/submit_contact_form/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(jsonData),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        alert('Form submitted successfully!');
        // Clear form fields after submission
        document.getElementById('contact-form').reset();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting the form. Please try again later.');
    });
});
