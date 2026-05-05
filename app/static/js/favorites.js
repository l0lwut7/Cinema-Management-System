/**
 * Handles favorite button functionality across the application.
 * - Unauthenticated users: Redirect to login page
 * - Authenticated users: Toggle favorite via AJAX
 */

document.addEventListener('DOMContentLoaded', function () {
    const favoriteBtns = document.querySelectorAll('.favorite-btn');
    const loginUrl = '/auth/login'; // Update this to your actual login route if different
    const favoritesGrid = document.querySelector('#favorites-grid');

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

    function renderFavoritesEmptyState() {
        if (!favoritesGrid) {
            return;
        }

        favoritesGrid.innerHTML = `
            <div class="favorites-empty-state col-span-full rounded-3xl border border-white/10 bg-cinema-surface p-10 text-center">
                <p class="text-xl font-semibold mb-3">You haven't added any favorite movies yet.</p>
                <p class="text-cinema-muted mb-6">Explore our catalog and find your next watch!</p>
                <a href="/" class="inline-flex items-center justify-center rounded-full bg-cinema-primary px-6 py-3 text-sm font-semibold text-white hover:bg-red-700 transition-colors">
                    Browse movies
                </a>
            </div>
        `;
    }

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
            const isFavorited = data.is_favorited || data.favorited;
            const favoriteCard = button.closest('.favorite-card');
            const isFavoritesView = Boolean(favoritesGrid);

            if (isFavorited) {
                heartIcon.classList.remove('fill-none');
                heartIcon.classList.add('fill-cinema-primary');
                button.setAttribute('data-is-favorited', 'true');
            } else {
                heartIcon.classList.remove('fill-cinema-primary');
                heartIcon.classList.add('fill-none');
                button.setAttribute('data-is-favorited', 'false');

                if (favoriteCard && isFavoritesView) {
                    favoriteCard.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                    favoriteCard.style.opacity = '0';
                    favoriteCard.style.transform = 'scale(0.98)';

                    window.setTimeout(() => {
                        favoriteCard.remove();
                        if (!favoritesGrid.querySelector('.favorite-card')) {
                            renderFavoritesEmptyState();
                        }
                    }, 250);
                }
            }
        })
        .catch(error => {
            console.error('Error toggling favorite:', error);
            alert('Failed to update favorite. Please try again.');
        });
    }
});
