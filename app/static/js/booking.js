// ==================== STATE ====================
const state = {
  currentStep: 1,
  theater: '',
  movie: '',
  showtime: '',
  selectedSeats: [],
  tickets: { adult: 0, child: 0, senior: 0 },
  consumables: { popcorn: 0, soda: 0, candy: 0, hotdog: 0 },
};

const prices = {
  adult: 15.00,
  child: 10.00,
  senior: 12.00,
  popcorn: 8.50,
  soda: 6.00,
  candy: 5.00,
  hotdog: 7.00,
  serviceFee: 2.50
};

const movieNames = {
  dune2: 'Dune: Part Two',
  oppenheimer: 'Oppenheimer',
  barbie: 'Barbie',
  mission: 'Mission: Impossible - Dead Reckoning'
};

const theaterNames = {
  downtown: 'CineBook Downtown IMAX',
  westside: 'CineBook Westside Multiplex',
  central: 'CineBook Central Plaza'
};

const showtimes = ['10:00 AM', '12:30 PM', '3:00 PM', '5:30 PM', '7:30 PM', '9:45 PM'];

// Seat map configuration
const seatRows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const seatsPerRow = 12;
const occupiedSeats = ['A3', 'A4', 'B5', 'B6', 'B7', 'C8', 'D5', 'D6', 'E2', 'E3', 'F7', 'F8', 'G4', 'H1', 'H12'];
const disabledSeats = ['A1', 'A12', 'H2', 'H11'];

// ==================== DOM ELEMENTS ====================
const steps = {
  1: document.getElementById('step1'),
  2: document.getElementById('step2'),
  3: document.getElementById('step3'),
  4: document.getElementById('step4')
};

const indicators = {
  1: document.getElementById('step1Indicator'),
  2: document.getElementById('step2Indicator'),
  3: document.getElementById('step3Indicator'),
  4: document.getElementById('step4Indicator')
};

const progressLine = document.getElementById('progressLine');

// ==================== NAVIGATION ====================
function goToStep(step) {
  // Hide all steps
  Object.values(steps).forEach(s => {
    s.classList.remove('step-active');
    s.classList.add('step-hidden');
  });

  // Show current step
  steps[step].classList.remove('step-hidden');
  steps[step].classList.add('step-active');

  // Update indicators
  Object.entries(indicators).forEach(([num, el]) => {
    if (parseInt(num) <= step) {
      el.classList.remove('bg-surface');
      el.classList.add('bg-crimson');
    } else {
      el.classList.remove('bg-crimson');
      el.classList.add('bg-surface');
    }
  });

  // Update progress line
  const progress = ((step - 1) / 3) * 100;
  progressLine.style.width = `${progress}%`;

  state.currentStep = step;

  // Step-specific updates
  if (step === 2) {
    renderSeatMap();
    updateSeatInfo();
  }
  if (step === 3) {
    updateStep3Summary();
    autoDistributeTickets();
  }
  if (step === 4) {
    updateReview();
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== STEP 1: SELECTION ====================
const theaterSelect = document.getElementById('theaterSelect');
const movieSelect = document.getElementById('movieSelect');
const emptyState = document.getElementById('emptyState');
const noScreenings = document.getElementById('noScreenings');
const showtimesGrid = document.getElementById('showtimesGrid');
const showtimesList = document.getElementById('showtimesList');
const step1Next = document.getElementById('step1Next');

function updateShowtimes() {
  state.theater = theaterSelect.value;
  state.movie = movieSelect.value;
  state.showtime = '';
  step1Next.disabled = true;

  if (!state.theater || !state.movie) {
    emptyState.classList.remove('hidden');
    noScreenings.classList.add('hidden');
    showtimesGrid.classList.add('hidden');
    return;
  }

  // Simulate no screenings for certain combinations
  if (state.theater === 'central' && state.movie === 'dune2') {
    emptyState.classList.add('hidden');
    noScreenings.classList.remove('hidden');
    showtimesGrid.classList.add('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  noScreenings.classList.add('hidden');
  showtimesGrid.classList.remove('hidden');

  // Render showtimes
  showtimesList.innerHTML = showtimes.map(time => `
        <button class="showtime-btn bg-background hover:bg-crimson/20 border border-surfaceLight hover:border-crimson text-white px-4 py-3 rounded-lg text-center transition-all" data-time="${time}">
          <span class="block font-semibold">${time}</span>
          <span class="block text-xs text-slate-400 mt-1">${state.theater === 'downtown' ? 'IMAX' : 'Standard'}</span>
        </button>
      `).join('');

  // Add click handlers
  document.querySelectorAll('.showtime-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.showtime-btn').forEach(b => {
        b.classList.remove('bg-crimson', 'border-crimson');
        b.classList.add('bg-background', 'border-surfaceLight');
      });
      btn.classList.remove('bg-background', 'border-surfaceLight');
      btn.classList.add('bg-crimson', 'border-crimson');
      state.showtime = btn.dataset.time;
      step1Next.disabled = false;
    });
  });
}

theaterSelect.addEventListener('change', updateShowtimes);
movieSelect.addEventListener('change', updateShowtimes);

step1Next.addEventListener('click', () => {
  if (state.showtime) goToStep(2);
});

// ==================== STEP 2: SEAT MAP ====================
const seatMap = document.getElementById('seatMap');
const selectedSeatsDisplay = document.getElementById('selectedSeatsDisplay');
const seatsSubtotal = document.getElementById('seatsSubtotal');
const step2Next = document.getElementById('step2Next');

function renderSeatMap() {
  seatMap.innerHTML = seatRows.map(row => `
        <div class="flex items-center gap-2">
          <span class="w-6 text-center text-slate-400 font-medium">${row}</span>
          <div class="flex gap-1">
            ${Array.from({ length: seatsPerRow }, (_, i) => {
    const seatId = `${row}${i + 1}`;
    const isOccupied = occupiedSeats.includes(seatId);
    const isDisabled = disabledSeats.includes(seatId);
    const isSelected = state.selectedSeats.includes(seatId);

    let classes = 'seat w-8 h-8 rounded text-xs font-medium flex items-center justify-center cursor-pointer';

    if (isDisabled) {
      classes += ' bg-slate-700 opacity-30 cursor-not-allowed disabled';
    } else if (isOccupied) {
      classes += ' bg-slate-600 opacity-50 cursor-not-allowed occupied';
    } else if (isSelected) {
      classes += ' bg-crimson text-white';
    } else {
      classes += ' bg-surfaceLight hover:bg-slate-500';
    }

    return `<button class="${classes}" data-seat="${seatId}" ${isOccupied || isDisabled ? 'disabled' : ''}>${i + 1}</button>`;
  }).join('')}
          </div>
          <span class="w-6 text-center text-slate-400 font-medium">${row}</span>
        </div>
      `).join('');

  // Add click handlers
  document.querySelectorAll('.seat:not(.occupied):not(.disabled)').forEach(seat => {
    seat.addEventListener('click', () => toggleSeat(seat.dataset.seat));
  });
}

function toggleSeat(seatId) {
  const index = state.selectedSeats.indexOf(seatId);
  if (index > -1) {
    state.selectedSeats.splice(index, 1);
  } else {
    if (state.selectedSeats.length < 10) {
      state.selectedSeats.push(seatId);
    }
  }

  // Sort seats
  state.selectedSeats.sort((a, b) => {
    const rowA = a[0], rowB = b[0];
    const numA = parseInt(a.slice(1)), numB = parseInt(b.slice(1));
    if (rowA !== rowB) return rowA.localeCompare(rowB);
    return numA - numB;
  });

  renderSeatMap();
  updateSeatDisplay();
}

function updateSeatDisplay() {
  if (state.selectedSeats.length === 0) {
    selectedSeatsDisplay.textContent = 'None selected';
    seatsSubtotal.textContent = '$0.00';
    step2Next.disabled = true;
  } else {
    selectedSeatsDisplay.textContent = state.selectedSeats.join(', ');
    const subtotal = state.selectedSeats.length * prices.adult;
    seatsSubtotal.textContent = `$${subtotal.toFixed(2)}`;
    step2Next.disabled = false;
  }
}

function updateSeatInfo() {
  document.getElementById('seatMovieInfo').textContent = movieNames[state.movie] || 'Movie';
  document.getElementById('seatShowtimeInfo').textContent = `${state.showtime} - ${state.theater === 'downtown' ? 'IMAX' : 'Standard'}`;
  document.getElementById('seatTheaterInfo').textContent = theaterNames[state.theater] || 'Theater';
}

document.getElementById('step2Back').addEventListener('click', () => goToStep(1));
step2Next.addEventListener('click', () => {
  if (state.selectedSeats.length > 0) goToStep(3);
});

// ==================== STEP 3: CART/CONSUMABLES ====================
function autoDistributeTickets() {
  // Auto-assign all seats as adult tickets
  state.tickets.adult = state.selectedSeats.length;
  state.tickets.child = 0;
  state.tickets.senior = 0;
  updateTicketDisplay();
  updateConsumableDisplay();
  updateTotals();
}

function updateTicketDisplay() {
  document.getElementById('adultCount').textContent = state.tickets.adult;
  document.getElementById('childCount').textContent = state.tickets.child;
  document.getElementById('seniorCount').textContent = state.tickets.senior;
}

function updateConsumableDisplay() {
  document.getElementById('popcornCount').textContent = state.consumables.popcorn;
  document.getElementById('sodaCount').textContent = state.consumables.soda;
  document.getElementById('candyCount').textContent = state.consumables.candy;
  document.getElementById('hotdogCount').textContent = state.consumables.hotdog;
}

function updateTotals() {
  const ticketTotal =
    state.tickets.adult * prices.adult +
    state.tickets.child * prices.child +
    state.tickets.senior * prices.senior;

  const consumableTotal =
    state.consumables.popcorn * prices.popcorn +
    state.consumables.soda * prices.soda +
    state.consumables.candy * prices.candy +
    state.consumables.hotdog * prices.hotdog;

  const grandTotal = ticketTotal + consumableTotal + prices.serviceFee;

  document.getElementById('ticketTotal').textContent = `$${ticketTotal.toFixed(2)}`;
  document.getElementById('consumableTotal').textContent = `$${consumableTotal.toFixed(2)}`;
  document.getElementById('grandTotal').textContent = `$${grandTotal.toFixed(2)}`;

  // Update ticket summary
  const ticketSummary = document.getElementById('ticketSummary');
  let ticketHtml = '';
  if (state.tickets.adult > 0) ticketHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.tickets.adult}x Adult</span><span>$${(state.tickets.adult * prices.adult).toFixed(2)}</span></div>`;
  if (state.tickets.child > 0) ticketHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.tickets.child}x Child</span><span>$${(state.tickets.child * prices.child).toFixed(2)}</span></div>`;
  if (state.tickets.senior > 0) ticketHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.tickets.senior}x Senior</span><span>$${(state.tickets.senior * prices.senior).toFixed(2)}</span></div>`;
  ticketSummary.innerHTML = ticketHtml || '<div class="text-sm text-slate-500">No tickets selected</div>';

  // Update consumable summary
  const consumableSummary = document.getElementById('consumableSummary');
  let consumableHtml = '';
  if (state.consumables.popcorn > 0) consumableHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.consumables.popcorn}x Popcorn</span><span>$${(state.consumables.popcorn * prices.popcorn).toFixed(2)}</span></div>`;
  if (state.consumables.soda > 0) consumableHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.consumables.soda}x Soda</span><span>$${(state.consumables.soda * prices.soda).toFixed(2)}</span></div>`;
  if (state.consumables.candy > 0) consumableHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.consumables.candy}x Candy</span><span>$${(state.consumables.candy * prices.candy).toFixed(2)}</span></div>`;
  if (state.consumables.hotdog > 0) consumableHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.consumables.hotdog}x Hot Dog</span><span>$${(state.consumables.hotdog * prices.hotdog).toFixed(2)}</span></div>`;
  consumableSummary.innerHTML = consumableHtml || '<div class="text-sm text-slate-500">No extras added</div>';

  // Enable/disable next button based on ticket count matching seats
  const totalTickets = state.tickets.adult + state.tickets.child + state.tickets.senior;
  document.getElementById('step3Next').disabled = totalTickets !== state.selectedSeats.length;
}

function updateStep3Summary() {
  document.getElementById('summarySeats').textContent = state.selectedSeats.join(', ') || '-';
}

// Ticket controls
document.querySelectorAll('.ticket-minus').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    if (state.tickets[type] > 0) {
      state.tickets[type]--;
      updateTicketDisplay();
      updateTotals();
    }
  });
});

document.querySelectorAll('.ticket-plus').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    const totalTickets = state.tickets.adult + state.tickets.child + state.tickets.senior;
    if (totalTickets < state.selectedSeats.length) {
      state.tickets[type]++;
      updateTicketDisplay();
      updateTotals();
    }
  });
});

// Consumable controls
document.querySelectorAll('.consumable-minus').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.dataset.item;
    if (state.consumables[item] > 0) {
      state.consumables[item]--;
      updateConsumableDisplay();
      updateTotals();
    }
  });
});

document.querySelectorAll('.consumable-plus').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.dataset.item;
    if (state.consumables[item] < 10) {
      state.consumables[item]++;
      updateConsumableDisplay();
      updateTotals();
    }
  });
});

document.getElementById('step3Back').addEventListener('click', () => goToStep(2));
document.getElementById('step3Next').addEventListener('click', () => goToStep(4));

// ==================== STEP 4: CHECKOUT ====================
const checkoutForm = document.getElementById('checkoutForm');
const confirmationScreen = document.getElementById('confirmationScreen');

function updateReview() {
  document.getElementById('reviewMovie').textContent = movieNames[state.movie];
  document.getElementById('reviewShowtime').textContent = `Today, ${state.showtime} - ${state.theater === 'downtown' ? 'IMAX' : 'Standard'}`;
  document.getElementById('reviewTheater').textContent = theaterNames[state.theater];
  document.getElementById('reviewSeats').textContent = state.selectedSeats.join(', ');

  // Calculate total
  const ticketTotal =
    state.tickets.adult * prices.adult +
    state.tickets.child * prices.child +
    state.tickets.senior * prices.senior;
  const consumableTotal =
    state.consumables.popcorn * prices.popcorn +
    state.consumables.soda * prices.soda +
    state.consumables.candy * prices.candy +
    state.consumables.hotdog * prices.hotdog;
  const grandTotal = ticketTotal + consumableTotal + prices.serviceFee;

  document.getElementById('reviewTotal').textContent = `$${grandTotal.toFixed(2)}`;

  // Update extras list
  const extrasList = document.getElementById('reviewExtrasList');
  let extrasHtml = '';
  if (state.tickets.adult > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.tickets.adult}x Adult Ticket</p>`;
  if (state.tickets.child > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.tickets.child}x Child Ticket</p>`;
  if (state.tickets.senior > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.tickets.senior}x Senior Ticket</p>`;
  if (state.consumables.popcorn > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.consumables.popcorn}x Large Popcorn</p>`;
  if (state.consumables.soda > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.consumables.soda}x Large Soda</p>`;
  if (state.consumables.candy > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.consumables.candy}x Candy Box</p>`;
  if (state.consumables.hotdog > 0) extrasHtml += `<p class="text-sm text-slate-300">${state.consumables.hotdog}x Hot Dog</p>`;
  extrasList.innerHTML = extrasHtml || '<p class="text-sm text-slate-500">No extras</p>';
}

// Card number formatting
document.getElementById('cardNumber').addEventListener('input', function (e) {
  let value = e.target.value.replace(/\s/g, '').replace(/\D/g, '');
  value = value.match(/.{1,4}/g)?.join(' ') || '';
  e.target.value = value;
});

// Expiry formatting
document.getElementById('cardExpiry').addEventListener('input', function (e) {
  let value = e.target.value.replace(/\D/g, '');
  if (value.length >= 2) {
    value = value.slice(0, 2) + '/' + value.slice(2, 4);
  }
  e.target.value = value;
});

// CVV - numbers only
document.getElementById('cardCvv').addEventListener('input', function (e) {
  e.target.value = e.target.value.replace(/\D/g, '');
});

function validateForm() {
  let isValid = true;

  // Name validation
  const cardName = document.getElementById('cardName');
  const cardNameError = document.getElementById('cardNameError');
  if (!cardName.value.trim()) {
    cardNameError.classList.remove('hidden');
    cardName.classList.add('border-crimson');
    isValid = false;
  } else {
    cardNameError.classList.add('hidden');
    cardName.classList.remove('border-crimson');
  }

  // Card number validation
  const cardNumber = document.getElementById('cardNumber');
  const cardNumberError = document.getElementById('cardNumberError');
  const cardNumberClean = cardNumber.value.replace(/\s/g, '');
  if (cardNumberClean.length < 16) {
    cardNumberError.classList.remove('hidden');
    cardNumber.classList.add('border-crimson');
    isValid = false;
  } else {
    cardNumberError.classList.add('hidden');
    cardNumber.classList.remove('border-crimson');
  }

  // Expiry validation
  const cardExpiry = document.getElementById('cardExpiry');
  const cardExpiryError = document.getElementById('cardExpiryError');
  if (cardExpiry.value.length < 5) {
    cardExpiryError.classList.remove('hidden');
    cardExpiry.classList.add('border-crimson');
    isValid = false;
  } else {
    cardExpiryError.classList.add('hidden');
    cardExpiry.classList.remove('border-crimson');
  }

  // CVV validation
  const cardCvv = document.getElementById('cardCvv');
  const cardCvvError = document.getElementById('cardCvvError');
  if (cardCvv.value.length < 3) {
    cardCvvError.classList.remove('hidden');
    cardCvv.classList.add('border-crimson');
    isValid = false;
  } else {
    cardCvvError.classList.add('hidden');
    cardCvv.classList.remove('border-crimson');
  }

  // Email validation
  const email = document.getElementById('email');
  const emailError = document.getElementById('emailError');
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    emailError.classList.remove('hidden');
    email.classList.add('border-crimson');
    isValid = false;
  } else {
    emailError.classList.add('hidden');
    email.classList.remove('border-crimson');
  }

  return isValid;
}

document.getElementById('payButton').addEventListener('click', function () {
  if (validateForm()) {
    showConfirmation();
  }
});

function showConfirmation() {
  checkoutForm.classList.add('hidden');
  confirmationScreen.classList.remove('hidden');

  // Generate booking ID
  const bookingId = 'CB-2024-' + Math.random().toString(36).substr(2, 5).toUpperCase();
  document.getElementById('bookingId').textContent = bookingId;

  // Update confirmation details
  document.getElementById('confirmMovie').textContent = movieNames[state.movie];
  document.getElementById('confirmShowtime').textContent = `Today, ${state.showtime}`;
  document.getElementById('confirmTheater').textContent = theaterNames[state.theater];
  document.getElementById('confirmSeats').textContent = state.selectedSeats.join(', ');

  // Calculate and show total
  const ticketTotal =
    state.tickets.adult * prices.adult +
    state.tickets.child * prices.child +
    state.tickets.senior * prices.senior;
  const consumableTotal =
    state.consumables.popcorn * prices.popcorn +
    state.consumables.soda * prices.soda +
    state.consumables.candy * prices.candy +
    state.consumables.hotdog * prices.hotdog;
  const grandTotal = ticketTotal + consumableTotal + prices.serviceFee;

  document.getElementById('confirmTotal').textContent = `$${grandTotal.toFixed(2)}`;
}

document.getElementById('step4Back').addEventListener('click', () => {
  checkoutForm.classList.remove('hidden');
  confirmationScreen.classList.add('hidden');
  goToStep(3);
});

document.getElementById('newBookingBtn').addEventListener('click', function () {
  // Reset state
  state.currentStep = 1;
  state.theater = '';
  state.movie = '';
  state.showtime = '';
  state.selectedSeats = [];
  state.tickets = { adult: 0, child: 0, senior: 0 };
  state.consumables = { popcorn: 0, soda: 0, candy: 0, hotdog: 0 };

  // Reset form
  theaterSelect.value = '';
  movieSelect.value = '';
  document.getElementById('paymentForm').reset();

  // Hide confirmation, show checkout form
  checkoutForm.classList.remove('hidden');
  confirmationScreen.classList.add('hidden');

  // Reset UI
  updateShowtimes();
  goToStep(1);
});

// Initialize
updateShowtimes();
