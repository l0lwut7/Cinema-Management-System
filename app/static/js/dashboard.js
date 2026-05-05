// Dashboard Tab Switching
function switchDashboardTab(tab) {
  // Update sidebar navigation
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.remove('active');
    link.classList.add('text-gray-400');
  });
  const activeNav = document.getElementById('nav-' + tab);
  activeNav.classList.add('active');
  activeNav.classList.remove('text-gray-400');

  // Update content
  document.querySelectorAll('.dashboard-tab').forEach(content => content.classList.add('hidden'));
  document.getElementById('tab-' + tab).classList.remove('hidden');
}

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

// Refund Modal
function showRefundModal() {
  const modal = document.getElementById('refund-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function hideRefundModal() {
  const modal = document.getElementById('refund-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

function submitRefund() {
  hideRefundModal();
  alert('Refund request submitted! You will receive confirmation via email.');
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

// Bookings Filter and Sort
function filterAndSortBookings() {
  const tbody = document.getElementById('bookings-tbody');
  if (!tbody) return;
  
  const sortValue = document.getElementById('sort-bookings').value;
  const statusValue = document.getElementById('filter-status').value;
  
  const rows = Array.from(tbody.querySelectorAll('.booking-row'));
  
  // Filtering
  rows.forEach(row => {
    const status = row.getAttribute('data-status');
    if (statusValue === 'all' || status === statusValue) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
  
  // Sorting
  rows.sort((a, b) => {
    if (sortValue === 'date-desc' || sortValue === 'date-asc') {
      const dateA = new Date(a.getAttribute('data-date'));
      const dateB = new Date(b.getAttribute('data-date'));
      return sortValue === 'date-desc' ? dateB - dateA : dateA - dateB;
    } else if (sortValue === 'price-desc' || sortValue === 'price-asc') {
      const priceA = parseFloat(a.getAttribute('data-price'));
      const priceB = parseFloat(b.getAttribute('data-price'));
      return sortValue === 'price-desc' ? priceB - priceA : priceA - priceB;
    }
    return 0;
  });
  
  // Re-append rows in new order
  rows.forEach(row => tbody.appendChild(row));
}
