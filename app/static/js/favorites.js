/**
 * Handles favorite button functionality across the application.
 * - Unauthenticated users: Redirect to login page
 * - Authenticated users: Toggle favorite via AJAX
 */

document.addEventListener('DOMContentLoaded', function () {
    const favoriteBtns = document.querySelectorAll('.favorite-btn');
    const loginUrl = '/auth/login'; // Update this to your actual login route if different

    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const movieId = this.getAttribute('data-movie-id');
            const isAuthenticated = this.getAttribute('data-is-authenticated') === 'true';
            const heartIcon = this.querySelector('.heart-icon');

            // Redirect to login if not authenticated
            if (!isAuthenticated) {
                window.location.href = loginUrl;
                return;
            }

            // Toggle favorite via AJAX
            toggleFavorite(movieId, heartIcon, this);
        });
    });

    /**
     * Toggle favorite status for a movie via AJAX
     * @param {string} movieId - The ID of the movie
     * @param {HTMLElement} heartIcon - The heart SVG icon element
     * @param {HTMLElement} button - The favorite button element
     */
    function toggleFavorite(movieId, heartIcon, button) {
        const url = `/api/favorites/toggle/${movieId}`; // Update endpoint as needed

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to toggle favorite');
            }
            return response.json();
        })
        .then(data => {
            // Update UI based on response
            const isFavorited = data.is_favorited || data.favorited;
            
            if (isFavorited) {
                heartIcon.classList.remove('fill-none');
                heartIcon.classList.add('fill-cinema-primary');
                button.setAttribute('data-is-favorited', 'true');
            } else {
                heartIcon.classList.remove('fill-cinema-primary');
                heartIcon.classList.add('fill-none');
                button.setAttribute('data-is-favorited', 'false');
            }
        })
        .catch(error => {
            console.error('Error toggling favorite:', error);
            alert('Failed to update favorite. Please try again.');
        });
    }
});
