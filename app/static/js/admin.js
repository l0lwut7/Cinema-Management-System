document.addEventListener('DOMContentLoaded', () => {

    // Sidebar Navigation
    const sidebarTabs = document.querySelectorAll('.sidebar-tab');
    const contentPanels = document.querySelectorAll('.content-panel');
    
    sidebarTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            sidebarTabs.forEach(t => {
                t.classList.remove('active');
                t.classList.remove('text-white');
                t.classList.add('text-slate-300');
            });
            
            // Add active class to clicked tab
            tab.classList.add('active');
            tab.classList.add('text-white');
            tab.classList.remove('text-slate-300');
            
            // Hide all panels
            contentPanels.forEach(panel => panel.classList.remove('active'));
            
            // Show corresponding panel
            const tabName = tab.dataset.tab;
            const panel = document.getElementById(`panel-${tabName}`);
            if (panel) {
                panel.classList.add('active');
            }
        });
    });
    
    // Infrastructure Sub-tabs
    const infraTabs = document.querySelectorAll('.infra-tab');
    const infraContents = document.querySelectorAll('.infra-content');
    
    infraTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Reset all tabs
            infraTabs.forEach(t => {
                t.classList.remove('bg-crimson', 'text-white');
                t.classList.add('bg-slate-700', 'text-slate-300');
            });
            
            // Activate clicked tab
            tab.classList.remove('bg-slate-700', 'text-slate-300');
            tab.classList.add('bg-crimson', 'text-white');
            
            // Hide all contents
            infraContents.forEach(content => content.classList.add('hidden'));
            
            // Show corresponding content
            const subtab = tab.dataset.subtab;
            const content = document.getElementById(`infra-${subtab}`);
            if (content) {
                content.classList.remove('hidden');
            }
        });
    });
    
    // Genre Chips Toggle
    const genreChips = document.querySelectorAll('#genre-chips .chip');
    genreChips.forEach(chip => {
        chip.addEventListener('click', () => {
            chip.classList.toggle('selected');
            chip.classList.toggle('text-white');
            chip.classList.toggle('text-slate-300');
        });
    });
    
    // Screening Form Validation
    const screeningForm = document.getElementById('screening-form');
    if (screeningForm) {
        screeningForm.addEventListener('submit', (e) => {
            e.preventDefault();
            let isValid = true;
            
            // Validate movie
            const movie = document.getElementById('screening-movie');
            const movieError = document.getElementById('movie-error');
            if (!movie.value) {
                movieError.classList.remove('hidden');
                movie.classList.add('border-crimson');
                isValid = false;
            } else {
                movieError.classList.add('hidden');
                movie.classList.remove('border-crimson');
            }
            
            // Validate saloon
            const saloon = document.getElementById('screening-saloon');
            const saloonError = document.getElementById('saloon-error');
            if (!saloon.value) {
                saloonError.classList.remove('hidden');
                saloon.classList.add('border-crimson');
                isValid = false;
            } else {
                saloonError.classList.add('hidden');
                saloon.classList.remove('border-crimson');
            }
            
            // Validate date
            const date = document.getElementById('screening-date');
            const dateError = document.getElementById('date-error');
            if (!date.value) {
                dateError.classList.remove('hidden');
                date.classList.add('border-crimson');
                isValid = false;
            } else {
                dateError.classList.add('hidden');
                date.classList.remove('border-crimson');
            }
            
            // Validate time
            const time = document.getElementById('screening-time');
            const timeError = document.getElementById('time-error');
            if (!time.value) {
                timeError.classList.remove('hidden');
                time.classList.add('border-crimson');
                isValid = false;
            } else {
                timeError.classList.add('hidden');
                time.classList.remove('border-crimson');
            }
            
            // Validate price
            const price = document.getElementById('screening-price');
            const priceError = document.getElementById('price-error');
            if (!price.value || parseFloat(price.value) <= 0) {
                priceError.classList.remove('hidden');
                price.classList.add('border-crimson');
                isValid = false;
            } else {
                priceError.classList.add('hidden');
                price.classList.remove('border-crimson');
            }
            
            if (isValid) {
                alert('Screening added successfully!');
                screeningForm.reset();
            }
        });
    }
    
    // Movie Form Submit
    const movieForm = document.getElementById('movie-form');
    if (movieForm) {
        movieForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Movie saved successfully!');
        });
    }

});
