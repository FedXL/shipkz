document.addEventListener('DOMContentLoaded', function() {
    const url = '/your-endpoint/'; // Replace with your actual endpoint URL

    fetch(url, {
        method: 'GET', // or 'POST', 'PUT', etc.
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token if needed
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle the response data here
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}