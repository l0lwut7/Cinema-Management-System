document.addEventListener('DOMContentLoaded', () => {

    // ── Flash message: close button + 5-second auto-dismiss ──────────────────
    document.querySelectorAll('.flash-message').forEach(msg => {
        const closeBtn = msg.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                msg.style.transition = 'opacity 0.3s ease';
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 300);
            });
        }
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s ease';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // Movie Edit Logic
const movieForm = document.getElementById("movie-form");
const movieFormTitle = document.getElementById("movie-form-title");
const movieSubmitButton = document.getElementById("movie-submit-button");
const movieCancelButton = document.getElementById("movie-cancel-button");

const movieTitleInput = document.getElementById("movie-title");
const movieDirectorInput = document.getElementById("movie-director");
const movieDurationInput = document.getElementById("movie-duration");
const movieRatingAgeInput = document.getElementById("movie-rating-age");
const movieReleaseDateInput = document.getElementById("movie-release-date");
const ratingChips = document.querySelectorAll("#rating-chips .chip");
const moviePosterInput = document.getElementById("movie-poster-input");
const moviePosterPreview = document.getElementById("movie-poster-preview");
const moviePosterPlaceholder = document.getElementById("movie-poster-placeholder");
const movieSummaryInput = document.getElementById("movie-summary");

const castContainer = document.getElementById("cast-inputs-container");
const btnAddCast = document.getElementById("btn-add-cast");
const MAX_CAST = 5;

const movieCatalogList = document.getElementById("movie-catalog-list");
const genreCheckboxes = document.querySelectorAll(".movie-genre-checkbox");
const formatCheckboxes = document.querySelectorAll(".movie-format-checkbox");
const movieVisibilityStatusSelect = document.getElementById("movie-visibility-status");

function clearMovieChipSelection() {
    document.querySelectorAll("#genre-chips .chip, #format-chips .chip").forEach((chip) => {
        chip.classList.remove("selected", "text-white");
        chip.classList.add("text-slate-300");

        const checkbox = chip.querySelector(".chip-checkbox");
        if (checkbox) {
            checkbox.checked = false;
        }
    });
    ratingChips.forEach(chip => {
        chip.classList.remove("selected", "text-white");
        chip.classList.add("text-slate-300");
    });
    if (movieRatingAgeInput) movieRatingAgeInput.value = "";
}

function setMovieFormToAddMode() {
    if (!movieForm) return;

    movieForm.action = "/admin/movies/add";
    movieForm.reset();
    clearMovieChipSelection();

    if (movieFormTitle) movieFormTitle.textContent = "MOVIE EDITOR";
    if (movieSubmitButton) movieSubmitButton.textContent = "Save Movie";

    clearCastInputs();

    if (movieVisibilityStatusSelect) movieVisibilityStatusSelect.value = "catalog_only";

    if (moviePosterPreview) {
        moviePosterPreview.src = '';
        moviePosterPreview.classList.add('hidden');
    }
    if (moviePosterPlaceholder) {
        moviePosterPlaceholder.classList.remove('hidden');
    }
}

function markSelectedMovieChips(selectedGenreIds, selectedFormatIds) {
    clearMovieChipSelection();

    genreCheckboxes.forEach((checkbox) => {
        if (selectedGenreIds.includes(checkbox.value)) {
            checkbox.checked = true;
            const chip = checkbox.closest(".chip");
            chip.classList.add("selected", "text-white");
            chip.classList.remove("text-slate-300");
        }
    });

    formatCheckboxes.forEach((checkbox) => {
        if (selectedFormatIds.includes(checkbox.value)) {
            checkbox.checked = true;
            const chip = checkbox.closest(".chip");
            chip.classList.add("selected", "text-white");
            chip.classList.remove("text-slate-300");
        }
    });
}

function selectRatingChip(value) {
    const strVal = String(value);
    ratingChips.forEach(chip => {
        if (chip.dataset.value === strVal) {
            chip.classList.add("selected", "text-white");
            chip.classList.remove("text-slate-300");
        } else {
            chip.classList.remove("selected", "text-white");
            chip.classList.add("text-slate-300");
        }
    });
    if (movieRatingAgeInput) movieRatingAgeInput.value = strVal;
}

// ── Cast member dynamic inputs ────────────────────────────────────────────────
function _castRowCount() {
    return castContainer ? castContainer.querySelectorAll('.cast-input-row').length : 0;
}

function _updateCastBtn() {
    if (!btnAddCast) return;
    if (_castRowCount() >= MAX_CAST) {
        btnAddCast.classList.add('hidden');
    } else {
        btnAddCast.classList.remove('hidden');
    }
}

function addCastInput(value = '') {
    if (!castContainer || _castRowCount() >= MAX_CAST) return;
    const row = document.createElement('div');
    row.className = 'cast-input-row flex gap-2';
    row.innerHTML =
        `<input type="text" name="cast[]" value="${value.replace(/"/g, '&quot;')}" placeholder="e.g. Actor Name"
                class="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-400 text-sm">` +
        `<button type="button" class="btn-remove-cast shrink-0 px-3 py-2 text-slate-400 hover:text-crimson transition-colors text-xl leading-none" title="Remove">&times;</button>`;
    row.querySelector('.btn-remove-cast').addEventListener('click', () => {
        row.remove();
        _updateCastBtn();
    });
    castContainer.appendChild(row);
    _updateCastBtn();
}

function clearCastInputs() {
    if (!castContainer) return;
    castContainer.innerHTML =
        `<div class="cast-input-row flex gap-2">` +
        `<input type="text" name="cast[]" placeholder="e.g. Timothée Chalamet"` +
        ` class="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-400 text-sm">` +
        `</div>`;
    _updateCastBtn();
}

function populateMovieFormForEdit(item) {
    const movieId = item.dataset.id;

    movieForm.action = `/admin/movies/edit/${movieId}`;

    movieTitleInput.value = item.dataset.title || "";
    movieDirectorInput.value = item.dataset.director || "";
    movieDurationInput.value = item.dataset.duration || "";
    selectRatingChip(item.dataset.ratingAge || "");
    movieReleaseDateInput.value = item.dataset.releaseDate || "";
    movieSummaryInput.value = item.dataset.summary || "";

    const selectedGenreIds = item.dataset.genreIds
        ? item.dataset.genreIds.split(",")
        : [];

    const selectedFormatIds = item.dataset.formatIds
        ? item.dataset.formatIds.split(",")
        : [];

    markSelectedMovieChips(selectedGenreIds, selectedFormatIds);

    // Populate cast inputs
    const castData = item.dataset.cast || "";
    clearCastInputs();
    if (castData) {
        const castMembers = castData.split(",").map(c => c.trim()).filter(Boolean);
        if (castMembers.length > 0) {
            castContainer.querySelector('.cast-input-row input').value = castMembers[0];
            for (let i = 1; i < castMembers.length; i++) {
                addCastInput(castMembers[i]);
            }
        }
    }

    // Populate visibility status
    if (movieVisibilityStatusSelect) {
        movieVisibilityStatusSelect.value = item.dataset.visibilityStatus || "catalog_only";
    }

    // Show existing poster in the preview
    const existingPosterUrl = item.dataset.posterUrl || "";
    if (existingPosterUrl && moviePosterPreview && moviePosterPlaceholder) {
        moviePosterPreview.src = existingPosterUrl;
        moviePosterPreview.classList.remove('hidden');
        moviePosterPlaceholder.classList.add('hidden');
    } else if (moviePosterPreview && moviePosterPlaceholder) {
        moviePosterPreview.src = '';
        moviePosterPreview.classList.add('hidden');
        moviePosterPlaceholder.classList.remove('hidden');
    }

    if (movieFormTitle) movieFormTitle.textContent = "EDIT MOVIE";
    if (movieSubmitButton) movieSubmitButton.textContent = "Update Movie";

    // Scroll the form into view on small screens
    movieForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Event delegation on the catalog list for Edit and Delete buttons
if (movieCatalogList) {
    movieCatalogList.addEventListener("click", (e) => {
        const editBtn = e.target.closest(".btn-edit-movie");
        const deleteBtn = e.target.closest(".btn-delete-movie");

        if (editBtn) {
            const item = editBtn.closest(".movie-list-item");
            if (item) populateMovieFormForEdit(item);
            return;
        }

        if (deleteBtn) {
            const item = deleteBtn.closest(".movie-list-item");
            if (!item) return;
            const movieTitle = item.dataset.title || "this movie";
            if (!confirm(`Are you sure you want to delete "${movieTitle}"? This action cannot be undone.`)) return;
            const form = document.createElement("form");
            form.method = "POST";
            form.action = `/admin/movies/delete/${item.dataset.id}`;
            document.body.appendChild(form);
            form.submit();
        }
    });
}

if (movieCancelButton) {
    movieCancelButton.addEventListener("click", () => {
        setMovieFormToAddMode();
    });
}
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

    // Initial active tab is set server-side by Jinja (see dashboard.html).
    // No JS click needed on load — doing so would cause a visible FOUC.
    
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

    // ── Screening form: date min + price validation ───────────────────────────
    const screeningDateInput = document.getElementById('screening-date');
    if (screeningDateInput) {
        screeningDateInput.min = new Date().toISOString().split('T')[0];
    }

    const screeningPriceInput = document.getElementById('screening-price');
    if (screeningPriceInput) {
        screeningPriceInput.addEventListener('input', function () {
            // Strip anything that is not a digit or dot
            let val = this.value.replace(/[^0-9.]/g, '');
            // Allow at most one decimal point
            const dotIndex = val.indexOf('.');
            if (dotIndex !== -1) {
                val = val.slice(0, dotIndex + 1) + val.slice(dotIndex + 1).replace(/\./g, '');
            }
            this.value = val;
        });
    }

    // ── Rating chips (single-select) ─────────────────────────────────────────
    ratingChips.forEach(chip => {
        chip.addEventListener('click', () => selectRatingChip(chip.dataset.value));
    });

    // ── Cast: "Add Cast Member" button ────────────────────────────────────────
    if (btnAddCast) {
        btnAddCast.addEventListener('click', () => addCastInput());
    }

    // ── Duration: digits only ────────────────────────────────────────────────
    if (movieDurationInput) {
        movieDurationInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    // ── Poster: local file preview via FileReader ─────────────────────────────
    if (moviePosterInput) {
        moviePosterInput.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function (e) {
                if (moviePosterPreview) {
                    moviePosterPreview.src = e.target.result;
                    moviePosterPreview.classList.remove('hidden');
                }
                if (moviePosterPlaceholder) {
                    moviePosterPlaceholder.classList.add('hidden');
                }
            };
            reader.readAsDataURL(file);
        });
    }

    // Genre and Format Chips Toggle
document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        const checkbox = chip.querySelector(".chip-checkbox");

        if (!checkbox) return;

        setTimeout(() => {
            if (checkbox.checked) {
                chip.classList.add("selected", "text-white");
                chip.classList.remove("text-slate-300");
            } else {
                chip.classList.remove("selected", "text-white");
                chip.classList.add("text-slate-300");
            }
        }, 0);
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

    const btnAddSaloon = document.getElementById('btn-add-saloon');
    if (btnAddSaloon) {
        btnAddSaloon.addEventListener('click', () => openModal('modal-add-saloon'));
    }
    // Consumable Add/Edit Logic
const btnAddConsumable = document.getElementById("btn-add-consumable");
const consumableForm = document.getElementById("form-consumable");
const consumableModalTitle = document.getElementById("consumable-modal-title");
const consumableSubmitButton = document.getElementById("consumable-submit-button");

const consumableNameInput = document.getElementById("consumable-name");
const consumableUnitPriceInput = document.getElementById("consumable-unit-price");
const consumableStockQuantityInput = document.getElementById("consumable-stock-quantity");

function resetConsumableFormForAdd() {
    if (!consumableForm) return;

    consumableForm.action = "/admin/consumables/add";
    consumableForm.reset();

    if (consumableModalTitle) {
        consumableModalTitle.textContent = "ADD CONSUMABLE";
    }

    if (consumableSubmitButton) {
        consumableSubmitButton.textContent = "Save Item";
    }
}

if (btnAddConsumable) {
    btnAddConsumable.addEventListener("click", () => {
        resetConsumableFormForAdd();
        openModal("modal-add-consumable");
    });
}

document.querySelectorAll(".btn-edit-consumable").forEach((button) => {
    button.addEventListener("click", () => {
        const card = button.closest(".consumable-card");

        if (!card || !consumableForm) return;

        const consumableId = card.dataset.id;

        consumableForm.action = `/admin/consumables/edit/${consumableId}`;

        if (consumableModalTitle) {
            consumableModalTitle.textContent = "EDIT CONSUMABLE";
        }

        if (consumableSubmitButton) {
            consumableSubmitButton.textContent = "Update Item";
        }

        consumableNameInput.value = card.dataset.name || "";
        consumableUnitPriceInput.value = card.dataset.unitPrice || "";
        consumableStockQuantityInput.value = card.dataset.stockQuantity || "";

        openModal("modal-add-consumable");
    });
});

    // Deal Add/Edit Logic
const btnAddDeal = document.getElementById("btn-add-deal");
const dealForm = document.getElementById("form-deal");
const dealModalTitle = document.getElementById("modal-deal-title");
const dealSubmitButton = document.getElementById("deal-submit-button");

const dealNameInput = document.getElementById("deal-name");
const dealDiscountInput = document.getElementById("deal-discount-percent");
const dealValidUntilInput = document.getElementById("deal-valid-until");

function resetDealFormForAdd() {
    if (!dealForm) return;

    dealForm.action = "/admin/deals/add";
    dealForm.reset();

    if (dealModalTitle) {
        dealModalTitle.textContent = "CREATE DEAL";
    }

    if (dealSubmitButton) {
        dealSubmitButton.textContent = "Save Deal";
    }
}

if (btnAddDeal) {
    btnAddDeal.addEventListener("click", () => {
        resetDealFormForAdd();
        openModal("modal-deal");
    });
}

document.querySelectorAll(".btn-edit-deal").forEach((button) => {
    button.addEventListener("click", () => {
        const card = button.closest(".deal-card");

        if (!card || !dealForm) return;

        const dealId = card.dataset.id;

        dealForm.action = `/admin/deals/edit/${dealId}`;

        if (dealModalTitle) {
            dealModalTitle.textContent = "EDIT DEAL";
        }

        if (dealSubmitButton) {
            dealSubmitButton.textContent = "Update Deal";
        }

        if (dealNameInput) {
            dealNameInput.value = card.dataset.name || "";
        }

        if (dealDiscountInput) {
            dealDiscountInput.value = card.dataset.discountPercent || "";
        }

        if (dealValidUntilInput) {
            dealValidUntilInput.value = card.dataset.validUntil || "";
        }

        openModal("modal-deal");
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
const ctx = document.getElementById("revenueChart");
let revenueChartInstance = null;

if (ctx) {
    let labels = [];
    let values = [];

    const revenueDataScript = document.getElementById("revenue-by-theater-data");

    if (revenueDataScript) {
        try {
            const revenueData = JSON.parse(revenueDataScript.textContent);
            labels = revenueData.labels || [];
            values = revenueData.values || [];
        } catch (error) {
            console.error("Could not parse revenue chart data:", error);
        }
    }

    revenueChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Revenue by Theater",
                data: values,
                backgroundColor: "rgba(16, 185, 129, 0.2)",
                borderColor: "#10B981",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#94A3B8"
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: "#334155"
                    },
                    ticks: {
                        color: "#94A3B8",
                        callback: (v) => "$" + v.toLocaleString()
                    }
                },
                x: {
                    grid: {
                        color: "#334155"
                    },
                    ticks: {
                        color: "#94A3B8"
                    }
                }
            }
        }
    });
}

    // Live analytics polling — refreshes KPI cards and chart every 30 seconds
    function refreshAnalytics() {
        fetch("/admin/api/analytics")
            .then((res) => {
                if (!res.ok) return;
                return res.json();
            })
            .then((data) => {
                if (!data || data.error) return;

                const { summary, chart } = data;

                const elRevenue   = document.getElementById("kpi-total-revenue");
                const elOccupancy = document.getElementById("kpi-occupancy-rate");
                const elTickets   = document.getElementById("kpi-tickets-sold");
                const elAlerts    = document.getElementById("kpi-inventory-alerts");

                if (elRevenue)   elRevenue.textContent   = summary.total_revenue;
                if (elOccupancy) elOccupancy.textContent = summary.occupancy_rate;
                if (elTickets)   elTickets.textContent   = summary.tickets_sold;
                if (elAlerts)    elAlerts.textContent    = summary.inventory_alerts;

                if (revenueChartInstance && chart) {
                    revenueChartInstance.data.labels              = chart.labels || [];
                    revenueChartInstance.data.datasets[0].data    = chart.values || [];
                    revenueChartInstance.update();
                }
            })
            .catch(() => {});
    }

    setInterval(refreshAnalytics, 30000);

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

  const employeeModal = document.getElementById("modal-employee");
  const employeeModalContent = document.getElementById("modal-employee-content");
  const employeeTitle = document.getElementById("modal-employee-title");
  const employeeForm = document.getElementById("form-employee");

  const addEmployeeButton = document.getElementById("btn-add-employee");
  const editEmployeeButtons = document.querySelectorAll(".btn-edit-employee");

  const firstNameInput = document.getElementById("employee-first-name");
  const lastNameInput = document.getElementById("employee-last-name");
  const emailInput = document.getElementById("employee-email");
  const phoneInput = document.getElementById("employee-phone-number");
  const passwordWrapper = document.getElementById("employee-password-wrapper");
  const passwordInput = document.getElementById("employee-password");
  const roleInput = document.getElementById("employee-role");
  const authLevelInput = document.getElementById("employee-auth-level");
  const salaryInput = document.getElementById("employee-salary");
  const statusInput = document.getElementById("employee-account-status");
  const shiftInput = document.getElementById("employee-work-shift");
  const theaterInput = document.getElementById("employee-theater-id");
  const submitButton = document.getElementById("employee-submit-button");

  // ── Input validators ─────────────────────────────────────────────────────
  // Letters + spaces only, including Turkish characters (ç ğ ı ö ş ü İ etc.)
  const lettersOnlyRe = /[^a-zA-ZçğışöüÇĞİÖŞÜ\s]/g;
  [firstNameInput, lastNameInput].forEach(input => {
      if (!input) return;
      input.addEventListener('input', function () {
          const pos = this.selectionStart;
          const cleaned = this.value.replace(lettersOnlyRe, '');
          if (cleaned !== this.value) {
              this.value = cleaned;
              this.setSelectionRange(pos - 1, pos - 1);
          }
      });
  });

  // Digits only — phone number
  if (phoneInput) {
      phoneInput.addEventListener('input', function () {
          const pos = this.selectionStart;
          const cleaned = this.value.replace(/[^0-9]/g, '');
          if (cleaned !== this.value) {
              this.value = cleaned;
              this.setSelectionRange(pos - 1, pos - 1);
          }
      });
  }

  // Digits only — salary (no dots, commas, or letters)
  if (salaryInput) {
      salaryInput.addEventListener('input', function () {
          const pos = this.selectionStart;
          const cleaned = this.value.replace(/[^0-9]/g, '');
          if (cleaned !== this.value) {
              this.value = cleaned;
              this.setSelectionRange(pos - 1, pos - 1);
          }
      });
  }

  function openEmployeeModal() {
    employeeModal.classList.remove("hidden");

    setTimeout(() => {
      employeeModalContent.classList.remove("scale-95", "opacity-0");
      employeeModalContent.classList.add("scale-100", "opacity-100");
    }, 10);
  }

  function resetEmployeeFormForAdd() {
    employeeTitle.textContent = "ADD EMPLOYEE";
    employeeForm.action = "/admin/employees/add";
    employeeForm.reset();

    passwordWrapper.classList.remove("hidden");
    passwordInput.required = true;
    submitButton.textContent = "Save Employee";
  }

  if (addEmployeeButton) {
    addEmployeeButton.addEventListener("click", function () {
      resetEmployeeFormForAdd();
      openEmployeeModal();
    });
  }

  editEmployeeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const row = button.closest("tr");

      const employeeId = row.dataset.id;

      employeeTitle.textContent = "EDIT EMPLOYEE";
      employeeForm.action = `/admin/employees/edit/${employeeId}`;

      firstNameInput.value = row.dataset.firstName || "";
      lastNameInput.value = row.dataset.lastName || "";
      emailInput.value = row.dataset.email || "";
      phoneInput.value = row.dataset.phoneNumber || "";
      roleInput.value = row.dataset.role || "";
      authLevelInput.value = row.dataset.authLevel || "1";
      salaryInput.value = row.dataset.salary || "";
      statusInput.value = row.dataset.accountStatus || "Active";
      shiftInput.value = row.dataset.workShift || "";
      theaterInput.value = row.dataset.theaterId || "";

      passwordWrapper.classList.add("hidden");
      passwordInput.required = false;
      passwordInput.value = "";

      submitButton.textContent = "Update Employee";

      openEmployeeModal();
    });
  });
});
