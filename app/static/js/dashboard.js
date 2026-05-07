// Dashboard Tab Switching
function switchDashboardTab(tab, updateHash = true) {
  const validTabs = ['history', 'favorites', 'profile'];
  if (!validTabs.includes(tab)) {
    tab = 'history';
  }

  // Update sidebar navigation
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.remove('active');
    link.classList.add('text-gray-400');
  });
  const activeNav = document.getElementById('nav-' + tab);
  if (activeNav) {
    activeNav.classList.add('active');
    activeNav.classList.remove('text-gray-400');
  }

  // Update content
  document.querySelectorAll('.dashboard-tab').forEach(content => content.classList.add('hidden'));
  const activeTab = document.getElementById('tab-' + tab);
  if (activeTab) {
    activeTab.classList.remove('hidden');
  }

  if (updateHash) {
    const targetHash = '#' + tab;
    if (window.location.hash !== targetHash) {
      window.location.hash = targetHash;
    }
  }
}

function initializeDashboardTabFromHash() {
  const tabFromHash = (window.location.hash || '#history').replace('#', '');
  switchDashboardTab(tabFromHash, false);
}

window.addEventListener('hashchange', initializeDashboardTabFromHash);
document.addEventListener('DOMContentLoaded', initializeDashboardTabFromHash);

// Password Toggle for Profile
function togglePassword(inputId, button) {
  const input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    button.innerHTML = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
    </svg>`;
  } else {
    input.type = 'password';
    button.innerHTML = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
    </svg>`;
  }
}

// ── Partial Refund Modal ──────────────────────────────────────────────────────

async function showRefundModal(button) {
  const bookingId    = button.getAttribute('data-booking-id');
  const movieTitle   = button.getAttribute('data-movie-title');
  const movieCode    = button.getAttribute('data-movie-code');
  const bookingCode  = button.getAttribute('data-booking-code');
  const startTime    = button.getAttribute('data-start-time');

  // Reset modal state
  document.getElementById('refund-booking-id').value = bookingId;
  document.getElementById('modal-movie-title').textContent  = movieTitle || '—';
  document.getElementById('modal-movie-code').textContent   = movieCode  || '—';
  document.getElementById('modal-booking-code').textContent = bookingCode ? `#${bookingCode}` : '—';

  if (startTime) {
    const dt = new Date(startTime);
    document.getElementById('modal-datetime').textContent =
      dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' • ' +
      dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  }

  const loadingEl   = document.getElementById('modal-loading');
  const listEl      = document.getElementById('modal-ticket-list');
  const formFieldsEl= document.getElementById('modal-form-fields');
  const errorEl     = document.getElementById('modal-error');
  const submitBtn   = document.getElementById('refund-submit-btn');
  const checkboxes  = document.getElementById('modal-seat-checkboxes');

  loadingEl.classList.remove('hidden');
  listEl.classList.add('hidden');
  formFieldsEl.classList.add('hidden');
  errorEl.classList.add('hidden');
  submitBtn.disabled = true;
  if (checkboxes) checkboxes.innerHTML = '';

  const modal = document.getElementById('refund-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');

  try {
    const res  = await fetch(`/dashboard/booking-tickets/${bookingId}`);
    const data = await res.json();

    loadingEl.classList.add('hidden');

    if (!res.ok || data.error) {
      errorEl.textContent = data.error || 'Could not load tickets.';
      errorEl.classList.remove('hidden');
      return;
    }

    if (!data.tickets || data.tickets.length === 0) {
      errorEl.textContent = 'No active tickets found for this booking.';
      errorEl.classList.remove('hidden');
      return;
    }

    checkboxes.innerHTML = data.tickets.map(t => `
      <label class="flex items-center gap-3 p-3 bg-cinema-bg rounded-xl cursor-pointer hover:bg-cinema-surfaceLight/30 transition-colors">
        <input type="checkbox" name="refund_ticket" value="${t.ticket_code}"
               onchange="updateRefundSubmitBtn()"
               class="w-4 h-4 rounded border-white/20 bg-cinema-bg text-cinema-primary focus:ring-cinema-primary flex-shrink-0">
        <span class="font-mono font-bold text-white text-sm">Seat ${t.seat}</span>
        <span class="text-xs text-gray-500 ml-auto">${t.ticket_code}</span>
      </label>`).join('');

    listEl.classList.remove('hidden');
    formFieldsEl.classList.remove('hidden');
    document.getElementById('modal-select-all').checked = false;
  } catch (err) {
    loadingEl.classList.add('hidden');
    errorEl.textContent = 'Network error: ' + err.message;
    errorEl.classList.remove('hidden');
  }
}

function hideRefundModal() {
  const modal = document.getElementById('refund-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

function toggleModalSelectAll(checked) {
  document.querySelectorAll('input[name="refund_ticket"]').forEach(cb => { cb.checked = checked; });
  updateRefundSubmitBtn();
}

function updateRefundSubmitBtn() {
  const any = [...document.querySelectorAll('input[name="refund_ticket"]')].some(cb => cb.checked);
  document.getElementById('refund-submit-btn').disabled = !any;
}

async function submitRefund(event) {
  event.preventDefault();

  const bookingId    = document.getElementById('refund-booking-id').value;
  const reason       = document.getElementById('refund-reason').value;
  const ticketCodes  = [...document.querySelectorAll('input[name="refund_ticket"]:checked')]
                         .map(cb => cb.value);

  if (!reason) { alert('Please select a refund reason.'); return; }
  if (!ticketCodes.length) { alert('Please select at least one seat to refund.'); return; }

  const submitBtn = document.getElementById('refund-submit-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Processing…';

  try {
    const res  = await fetch('/dashboard/refund', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ ticket_codes: ticketCodes, reason }),
    });
    const data = await res.json();

    if (data.success) {
      hideRefundModal();
      location.reload();
    } else {
      alert('Refund failed: ' + (data.message || 'Unknown error'));
      submitBtn.disabled   = false;
      submitBtn.textContent = 'Confirm Refund';
    }
  } catch (err) {
    alert('Network error: ' + err.message);
    submitBtn.disabled   = false;
    submitBtn.textContent = 'Confirm Refund';
  }
}

// Dashboard Password Strength Indicator
document.getElementById('new-password')?.addEventListener('input', function(e) {
  const password = e.target.value;
  const bars = document.querySelectorAll('#password-strength div');
  if (!bars.length) return;

  let strength = 0;
  
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  
  bars.forEach((bar, index) => {
    if (index < strength) {
      bar.classList.remove('bg-gray-700');
      if (strength <= 1) bar.classList.add('bg-red-500');
      else if (strength <= 2) bar.classList.add('bg-amber');
      else bar.classList.add('bg-emerald-500');
    } else {
      bar.classList.add('bg-gray-700');
      bar.classList.remove('bg-red-500', 'bg-amber', 'bg-emerald-500');
    }
  });
});

// Refund Eligibility Check: Can refund anytime until 1 hour before screening
function isRefundEligible(startTimeIso) {
  if (!startTimeIso) return false;
  const startTime = new Date(startTimeIso);
  const now = new Date();
  const oneHourBefore = new Date(startTime.getTime() - 60 * 60 * 1000);
  
  // Refund allowed if current time is BEFORE 1 hour before screening
  return now < oneHourBefore;
}

// Update refund button eligibility on page load and dynamically
function updateRefundButtonStates() {
  document.querySelectorAll('.refund-btn').forEach(btn => {
    const startTime = btn.getAttribute('data-start-time');
    if (isRefundEligible(startTime)) {
      btn.classList.remove('opacity-50', 'cursor-not-allowed');
      btn.disabled = false;
      const startDate = new Date(startTime);
      const oneHourBefore = new Date(startDate.getTime() - 60 * 60 * 1000);
      const timeStr = oneHourBefore.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
      btn.title = `Refund closes at ${timeStr} (1 hour before screening)`;
    } else {
      btn.classList.add('opacity-50', 'cursor-not-allowed');
      btn.disabled = true;
      btn.title = 'Refund window has closed (within 1 hour of screening)';
    }
  });
}

// Bookings Filter and Sort
function filterAndSortBookings() {
  const table = document.querySelector('table tbody');
  if (!table) return;
  
  const sortValue = document.getElementById('sort-bookings').value;
  const statusValue = document.getElementById('filter-status').value;
  
  const rows = Array.from(table.querySelectorAll('.booking-row'));
  
  // Filtering
  rows.forEach(row => {
    const status = row.getAttribute('data-status');
    if (statusValue === 'all' || status === statusValue) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
  
  // Sorting (only visible rows)
  const visibleRows = rows.filter(row => row.style.display !== 'none');
  visibleRows.sort((a, b) => {
    if (sortValue === 'date-desc' || sortValue === 'date-asc') {
      const dateA = new Date(a.getAttribute('data-date') || 0);
      const dateB = new Date(b.getAttribute('data-date') || 0);
      return sortValue === 'date-desc' ? dateB - dateA : dateA - dateB;
    } else if (sortValue === 'price-desc' || sortValue === 'price-asc') {
      const priceA = parseFloat(a.getAttribute('data-price') || 0);
      const priceB = parseFloat(b.getAttribute('data-price') || 0);
      return sortValue === 'price-desc' ? priceB - priceA : priceA - priceB;
    }
    return 0;
  });
  
  // Re-append rows in new order
  visibleRows.forEach(row => table.appendChild(row));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  updateRefundButtonStates();
});
