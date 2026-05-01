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

    // Format Chips Toggle
    const formatChips = document.querySelectorAll('#format-chips .chip');
    formatChips.forEach(chip => {
        chip.addEventListener('click', () => {
            chip.classList.toggle('selected');
            chip.classList.toggle('text-white');
            chip.classList.toggle('text-slate-300');
        });
    });

    // Consumable Icon Selector
    const iconBtns = document.querySelectorAll('#consumable-icons .icon-btn');
    iconBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            iconBtns.forEach(b => {
                b.classList.remove('border-2', 'border-emerald', 'shadow-[0_0_10px_rgba(16,185,129,0.2)]');
                b.classList.add('border', 'border-slate-700');
            });
            btn.classList.remove('border', 'border-slate-700');
            btn.classList.add('border-2', 'border-emerald', 'shadow-[0_0_10px_rgba(16,185,129,0.2)]');
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

    // Modal Logic
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        const content = document.getElementById(`${modalId}-content`);
        if (modal && content) {
            modal.classList.remove('hidden');
            // small delay to allow display:block to apply before animating opacity
            setTimeout(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }, 10);
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        const content = document.getElementById(`${modalId}-content`);
        if (modal && content) {
            content.classList.remove('scale-100', 'opacity-100');
            content.classList.add('scale-95', 'opacity-0');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 200); // Wait for transition
        }
    }

    // Bind Modals
    const btnAddConsumable = document.getElementById('btn-add-consumable');
    if (btnAddConsumable) {
        btnAddConsumable.addEventListener('click', () => openModal('modal-add-consumable'));
    }

    const btnAddSaloon = document.getElementById('btn-add-saloon');
    if (btnAddSaloon) {
        btnAddSaloon.addEventListener('click', () => openModal('modal-add-saloon'));
    }

    // Employee Modals
    const btnAddEmployee = document.getElementById('btn-add-employee');
    if (btnAddEmployee) {
        btnAddEmployee.addEventListener('click', () => {
            const title = document.getElementById('modal-employee-title');
            if (title) title.textContent = "ADD EMPLOYEE";
            openModal('modal-employee');
        });
    }

    document.querySelectorAll('.btn-edit-employee').forEach(btn => {
        btn.addEventListener('click', () => {
            const title = document.getElementById('modal-employee-title');
            if (title) title.textContent = "EDIT EMPLOYEE";
            openModal('modal-employee');
        });
    });

    // Business Modals
    document.querySelectorAll('.btn-edit-consumable').forEach(btn => {
        btn.addEventListener('click', () => openModal('modal-add-consumable'));
    });

    const btnAddDeal = document.getElementById('btn-add-deal');
    if (btnAddDeal) {
        btnAddDeal.addEventListener('click', () => {
            const title = document.getElementById('modal-deal-title');
            if (title) title.textContent = "CREATE DEAL";
            openModal('modal-deal');
        });
    }

    document.querySelectorAll('.btn-edit-deal').forEach(btn => {
        btn.addEventListener('click', () => {
            const title = document.getElementById('modal-deal-title');
            if (title) title.textContent = "EDIT DEAL";
            openModal('modal-deal');
        });
    });

    const btnEditTier = document.getElementById('btn-edit-tier');
    if (btnEditTier) {
        btnEditTier.addEventListener('click', () => openModal('modal-tier'));
    }

    // Bind Close Buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.fixed.inset-0');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });

    // Layout Radio Logic in Saloon Modal
    const layoutRadios = document.querySelectorAll('input[name="layout"]');
    if (layoutRadios) {
        layoutRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                // Reset all
                layoutRadios.forEach(r => {
                    const label = r.closest('label');
                    label.classList.remove('border-emerald/50', 'bg-emerald/10');
                    label.classList.add('border-slate-700', 'bg-slate-900', 'hover:border-slate-500');
                });
                // Highlight selected
                if (radio.checked) {
                    const label = radio.closest('label');
                    label.classList.remove('border-slate-700', 'bg-slate-900', 'hover:border-slate-500');
                    label.classList.add('border-emerald/50', 'bg-emerald/10');
                }
            });
        });
    }

    // Initialize Chart.js for Revenue
    const ctx = document.getElementById('revenueChart');
    if (ctx) {
        // Sample mock data for prototype
        const data = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Saloon A (IMAX)',
                data: [1200, 1900, 3000, 2500, 4200, 5800, 4900],
                borderColor: '#10B981', // emerald
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Saloon B (Standard)',
                data: [800, 1200, 1500, 1800, 2900, 3500, 3000],
                borderColor: '#0EA5E9', // sky
                backgroundColor: 'rgba(14, 165, 233, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#94A3B8' // slate-400
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#334155' // slate-700
                        },
                        ticks: {
                            color: '#94A3B8'
                        }
                    },
                    x: {
                        grid: {
                            color: '#334155'
                        },
                        ticks: {
                            color: '#94A3B8'
                        }
                    }
                }
            }
        });
    }

    // Top Spenders Sort and Filter Logic
    const spendersFilter = document.getElementById('spenders-filter');
    const spendersSort = document.getElementById('spenders-sort');
    const spendersTbody = document.getElementById('spenders-tbody');

    function updateSpendersTable() {
        if (!spendersFilter || !spendersSort || !spendersTbody) return;

        const filterValue = spendersFilter.value; // "all", "vip", "standard"
        const sortValue = spendersSort.value;     // "amount_desc", "amount_asc", "visits_desc"
        const rows = Array.from(spendersTbody.querySelectorAll('.spender-row'));

        // Filter
        rows.forEach(row => {
            const tier = row.dataset.tier;
            if (filterValue === 'all') {
                row.style.display = '';
            } else if (filterValue === 'vip' && tier === 'vip') {
                row.style.display = '';
            } else if (filterValue === 'standard' && tier === 'standard') {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });

        // Sort
        const visibleRows = rows.filter(row => row.style.display !== 'none');
        
        visibleRows.sort((a, b) => {
            const aAmount = parseFloat(a.dataset.amount);
            const bAmount = parseFloat(b.dataset.amount);
            const aVisits = parseInt(a.dataset.visits);
            const bVisits = parseInt(b.dataset.visits);

            if (sortValue === 'amount_desc') return bAmount - aAmount;
            if (sortValue === 'amount_asc') return aAmount - bAmount;
            if (sortValue === 'visits_desc') return bVisits - aVisits;
            return 0;
        });

        // Re-append to DOM in new order
        visibleRows.forEach(row => spendersTbody.appendChild(row));
    }

    if (spendersFilter) spendersFilter.addEventListener('change', updateSpendersTable);
    if (spendersSort) spendersSort.addEventListener('change', updateSpendersTable);

});
