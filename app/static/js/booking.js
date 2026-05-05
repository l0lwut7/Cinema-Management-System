// ==================== STATE ====================
const state = {
  currentStep: 1,
  theater: '',
  movie: '',
  showtime: '',
  screeningId: null,
  saloonType: '',
  basePrice: 0,
  selectedSeats: [],
  seatLayout: {},
  tickets: { adult: 0, child: 0, senior: 0 },
  consumables: { popcorn: 0, soda: 0, candy: 0, hotdog: 0 },
};
const realScreenings = window.BOOKING_SCREENINGS || [];

const prices = {
  serviceFee: 2.50,
  adult: 0,
  child: 0,
  senior: 0,
  popcorn: 0,
  soda: 0,
  candy: 0,
  hotdog: 0
};


const realConsumables = window.BOOKING_CONSUMABLES || [];

function resolveConsumableKey(name) {
  const lname = (name || "").toLowerCase();
  if (lname.includes("popcorn")) return "popcorn";
  if (lname.includes("soda")) return "soda";
  if (lname.includes("candy")) return "candy";
  if (lname.includes("hot")) return "hotdog";
  return null;
}

realConsumables.forEach(item => {
  const key = resolveConsumableKey(item.name);
  if (!key) return;

  const parsed = parseFloat(item.unit_price);
  if (!isNaN(parsed)) {
    prices[key] = parsed;
  }
});

// Final pass: hydrate prices from data-price attributes on consumable buttons
// (set by Jinja from the same DB values). Guarantees prices are always present.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".consumable-plus[data-item][data-price]").forEach(btn => {
    const key = btn.dataset.item;
    const parsed = parseFloat(btn.dataset.price);
    if (key && !isNaN(parsed)) {
      prices[key] = parsed;
    }
  });
});

let occupiedSeats = [];

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
  fetch(`/booking/occupied-seats/${state.screeningId}`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        occupiedSeats = data.occupied_seats;
      } else {
        occupiedSeats = [];
      }

      renderSeatMap();
      updateSeatInfo();
    })
    .catch(error => {
      console.error("Occupied seats error:", error);
      occupiedSeats = [];
      renderSeatMap();
      updateSeatInfo();
    });
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
  state.screeningId = null;
  state.saloonType = '';
  state.basePrice = 0;
  step1Next.disabled = true;

  if (!state.theater || !state.movie) {
    emptyState.classList.remove('hidden');
    noScreenings.classList.add('hidden');
    showtimesGrid.classList.add('hidden');
    return;
  }

  const filteredScreenings = realScreenings.filter(screening => {
    return String(screening.theater_id) === String(state.theater)
      && String(screening.movie_id) === String(state.movie);
  });

  if (filteredScreenings.length === 0) {
    emptyState.classList.add('hidden');
    noScreenings.classList.remove('hidden');
    showtimesGrid.classList.add('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  noScreenings.classList.add('hidden');
  showtimesGrid.classList.remove('hidden');

  showtimesList.innerHTML = filteredScreenings.map(screening => `
    <button
      class="showtime-btn bg-background hover:bg-crimson/20 border border-surfaceLight hover:border-crimson text-white px-4 py-3 rounded-lg text-center transition-all"
      data-screening-id="${screening.screening_id}"
      data-time="${screening.start_time_display}"
      data-saloon-type="${screening.saloon_type}"
      data-base-price="${screening.base_price}">
      <span class="block font-semibold">${screening.start_time_display}</span>
      <span class="block text-xs text-slate-400 mt-1">
        Saloon ${screening.saloon_number} - ${screening.saloon_type}
      </span>
      <span class="block text-xs text-slate-400 mt-1">
        $${Number(screening.base_price).toFixed(2)}
      </span>
    </button>
  `).join('');

  document.querySelectorAll('.showtime-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.showtime-btn').forEach(b => {
        b.classList.remove('bg-crimson', 'border-crimson');
        b.classList.add('bg-background', 'border-surfaceLight');
      });

      btn.classList.remove('bg-background', 'border-surfaceLight');
      btn.classList.add('bg-crimson', 'border-crimson');

      state.screeningId = Number(btn.dataset.screeningId);
      state.showtime = btn.dataset.time;
      state.saloonType = btn.dataset.saloonType;
      state.basePrice = Number(btn.dataset.basePrice);
      prices.adult = Number(state.basePrice || 0);
prices.child = prices.adult * 0.5;
prices.senior = prices.adult * 0.7;

updateTicketPriceLabels();

      const selectedScreening = filteredScreenings.find(s => s.screening_id === Number(btn.dataset.screeningId));
      state.seatLayout = (selectedScreening && selectedScreening.seat_layout) ? selectedScreening.seat_layout : {};
      state.selectedSeats = [];
      loadOccupiedSeats(state.screeningId);

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

function updateTicketPriceLabels() {
  const adultPriceLabel = document.getElementById('adultPriceLabel');
  const childPriceLabel = document.getElementById('childPriceLabel');
  const seniorPriceLabel = document.getElementById('seniorPriceLabel');

  if (adultPriceLabel) {
    adultPriceLabel.textContent = `$${prices.adult.toFixed(2)} each`;
  }

  if (childPriceLabel) {
    childPriceLabel.textContent = `$${prices.child.toFixed(2)} each`;
  }

  if (seniorPriceLabel) {
    seniorPriceLabel.textContent = `$${prices.senior.toFixed(2)} each`;
  }
}

function loadOccupiedSeats(screeningId) {
  fetch(`/booking/occupied-seats/${screeningId}`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        occupiedSeats = data.occupied_seats;
        console.log("Occupied seats loaded:", occupiedSeats);
      } else {
        occupiedSeats = [];
        console.log("Occupied seats could not be loaded:", data.message);
      }
    })
    .catch(error => {
      occupiedSeats = [];
      console.error("Occupied seats error:", error);
    });
}

function renderSeatMap() {
  const layout = state.seatLayout;

  if (!layout || Object.keys(layout).length === 0) {
    seatMap.innerHTML = '<p class="text-slate-400 text-center py-4">No seat data available for this screening.</p>';
    return;
  }

  seatMap.innerHTML = Object.entries(layout).map(([row, cols]) => `
        <div class="flex items-center gap-2">
          <span class="w-6 text-center text-slate-400 font-medium">${row}</span>
          <div class="flex gap-1">
            ${cols.map(num => {
    const seatId = `${row}${num}`;
    const isOccupied = occupiedSeats.includes(seatId);
    const isSelected = state.selectedSeats.includes(seatId);

    let classes = 'seat w-8 h-8 rounded text-xs font-medium flex items-center justify-center cursor-pointer';

    if (isOccupied) {
      classes += ' bg-slate-600 opacity-50 cursor-not-allowed occupied';
    } else if (isSelected) {
      classes += ' bg-crimson text-white';
    } else {
      classes += ' bg-surfaceLight hover:bg-slate-500';
    }

    return `<button class="${classes}" data-seat="${seatId}" ${isOccupied ? 'disabled' : ''}>${num}</button>`;
  }).join('')}
          </div>
          <span class="w-6 text-center text-slate-400 font-medium">${row}</span>
        </div>
      `).join('');

  // Add click handlers
  document.querySelectorAll('.seat:not(.occupied)').forEach(seat => {
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
    const subtotal = state.selectedSeats.length * state.basePrice;
    seatsSubtotal.textContent = `$${subtotal.toFixed(2)}`;
    step2Next.disabled = false;
  }
}

function updateSeatInfo() {
  const selectedMovieText = movieSelect.options[movieSelect.selectedIndex]?.text || 'Movie';
  const selectedTheaterText = theaterSelect.options[theaterSelect.selectedIndex]?.text || 'Theater';

  document.getElementById('seatMovieInfo').textContent = selectedMovieText;
  document.getElementById('seatShowtimeInfo').textContent = `${state.showtime} - ${state.saloonType}`;
  document.getElementById('seatTheaterInfo').textContent = selectedTheaterText;
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
 if (state.tickets.adult > 0) {
  ticketHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.tickets.adult}x Adult</span><span>$${(state.tickets.adult * prices.adult).toFixed(2)}</span></div>`;
}

if (state.tickets.child > 0) {
  ticketHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.tickets.child}x Child</span><span>$${(state.tickets.child * prices.child).toFixed(2)}</span></div>`;
}

if (state.tickets.senior > 0) {
  ticketHtml += `<div class="flex justify-between text-sm"><span class="text-slate-400">${state.tickets.senior}x Senior</span><span>$${(state.tickets.senior * prices.senior).toFixed(2)}</span></div>`;
}
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
const selectedMovieText = movieSelect.options[movieSelect.selectedIndex]?.text || 'Movie';
const selectedTheaterText = theaterSelect.options[theaterSelect.selectedIndex]?.text || 'Theater';

document.getElementById('reviewMovie').textContent = selectedMovieText;
document.getElementById('reviewShowtime').textContent = `${state.showtime} - ${state.saloonType}`;
document.getElementById('reviewTheater').textContent = selectedTheaterText;
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

// Cardholder name - letters + spaces only (Turkish/international supported)
const CARDHOLDER_NAME_REGEX = /^[A-Za-zÇçĞğİıÖöŞşÜüÂâÎîÛû ]+$/;
document.getElementById('cardName').addEventListener('input', function (e) {
  e.target.value = e.target.value.replace(/[^A-Za-zÇçĞğİıÖöŞşÜüÂâÎîÛû ]/g, '');
});

// Card number formatting
document.getElementById('cardNumber').addEventListener('input', function (e) {
  let value = e.target.value.replace(/\s/g, '').replace(/\D/g, '');
  value = value.match(/.{1,4}/g)?.join(' ') || '';
  e.target.value = value;
});

// Expiry formatting — month must be 01..12
document.getElementById('cardExpiry').addEventListener('input', function (e) {
  let digits = e.target.value.replace(/\D/g, '').slice(0, 4);

  // First digit > 1 means user typed something like "5" → coerce to "05"
  if (digits.length === 1 && parseInt(digits[0], 10) > 1) {
    digits = '0' + digits;
  }

  // Two-digit month must be in 01..12
  if (digits.length >= 2) {
    let month = parseInt(digits.slice(0, 2), 10);
    if (month === 0) {
      digits = '01' + digits.slice(2);
    } else if (month > 12) {
      digits = '12' + digits.slice(2);
    }
  }

  let formatted = digits;
  if (digits.length >= 2) {
    formatted = digits.slice(0, 2) + '/' + digits.slice(2, 4);
  }
  e.target.value = formatted;
});

// CVV - numbers only
document.getElementById('cardCvv').addEventListener('input', function (e) {
  e.target.value = e.target.value.replace(/\D/g, '');
});

function validateForm() {
  let isValid = true;

  // Name validation — letters & spaces only (Turkish/international supported)
  const cardName = document.getElementById('cardName');
  const cardNameError = document.getElementById('cardNameError');
  const trimmedName = cardName.value.trim();
  if (!trimmedName || !CARDHOLDER_NAME_REGEX.test(trimmedName)) {
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

  // Expiry validation — must be MM/YY, month 01..12, and not earlier than current month/year
  const cardExpiry = document.getElementById('cardExpiry');
  const cardExpiryError = document.getElementById('cardExpiryError');
  const expiryMatch = cardExpiry.value.match(/^(\d{2})\/(\d{2})$/);
  const expiryMonth = expiryMatch ? parseInt(expiryMatch[1], 10) : NaN;
  const expiryYear = expiryMatch ? parseInt(expiryMatch[2], 10) : NaN;

  const now = new Date();
  const currentMonth = now.getMonth() + 1;
  const currentYear = now.getFullYear() % 100;

  const isFormatValid = expiryMatch && expiryMonth >= 1 && expiryMonth <= 12;
  const isNotExpired = isFormatValid && (
    expiryYear > currentYear ||
    (expiryYear === currentYear && expiryMonth >= currentMonth)
  );

  if (!isFormatValid || !isNotExpired) {
    cardExpiryError.textContent = !isFormatValid
      ? 'Invalid expiry'
      : 'Card expiry must not be earlier than ' +
        String(currentMonth).padStart(2, '0') + '/' + String(currentYear).padStart(2, '0');
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


function createBookingInDatabase() {
  console.log("createBookingInDatabase çalıştı");
  console.log("Selected seats:", state.selectedSeats);

  if (!state.selectedSeats || state.selectedSeats.length === 0) {
    alert("Please select at least one seat.");
    return;
  }

const screeningId = state.screeningId;

if (!screeningId) {
  alert("Please select a screening.");
  return;
}
  const formattedSeats = state.selectedSeats.map(seatId => {
    return {
      row: seatId.charAt(0),
      number: Number(seatId.slice(1))
    };
  });

  const requestBody = {
  screening_id: screeningId,
  selected_seats: formattedSeats,
  tickets: state.tickets,
  consumables: state.consumables
};

  console.log("Sending to backend:", requestBody);

  fetch("/booking/create", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(requestBody)
  })
    .then(response => {
      console.log("Backend response status:", response.status);
      return response.json();
    })
    .then(data => {
      console.log("Booking response:", data);

      if (data.success) {
        showConfirmation(data.booking_id, data.total_amount);
      } else {
        alert(data.message || "Booking could not be created.");
      }
    })
    .catch(error => {
      console.error("Booking error:", error);
      alert("Something went wrong while creating booking.");
    });
}

document.getElementById("payButton").addEventListener("click", function () {
  console.log("PAY BUTTON CLICKED");

  if (validateForm()) {
    console.log("FORM VALID, CREATING BOOKING");
    createBookingInDatabase();
  } else {
    console.log("FORM NOT VALID");
    alert("Please fill payment form correctly.");
  }
});

function showConfirmation(bookingIdFromDb = null, totalAmountFromDb = null) {
  checkoutForm.classList.add('hidden');
  confirmationScreen.classList.remove('hidden');

    const bookingId = bookingIdFromDb ? "CB-" + bookingIdFromDb : 'CB-2024-' + Math.random().toString(36).substr(2, 5).toUpperCase();
    document.getElementById('bookingId').textContent = bookingId;
    const selectedMovieText = movieSelect.options[movieSelect.selectedIndex]?.text || 'Movie';
const selectedTheaterText = theaterSelect.options[theaterSelect.selectedIndex]?.text || 'Theater';

document.getElementById('confirmMovie').textContent = selectedMovieText;
document.getElementById('confirmShowtime').textContent = state.showtime;
document.getElementById('confirmTheater').textContent = selectedTheaterText;
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

  if (totalAmountFromDb !== null) {
  document.getElementById('confirmTotal').textContent = `$${Number(totalAmountFromDb).toFixed(2)}`;
} else {
  document.getElementById('confirmTotal').textContent = `$${grandTotal.toFixed(2)}`;
}

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
  state.screeningId = null;
  state.selectedSeats = [];
  state.seatLayout = {};
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

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
  const bookingApp = document.getElementById('booking-app');

  if (bookingApp && bookingApp.dataset.movieId) {
    try {
      // 1. Safely parse the JSON we passed from Jinja (handles "null" cleanly)
      const initialMovieId = JSON.parse(bookingApp.dataset.movieId);

      // 2. If an ID was passed, update the dropdown menu
      if (initialMovieId !== null) {
        // Map the backend integer IDs to the frontend mockup string values
        movieSelect.value = String(initialMovieId);
      }
    } catch (e) {
      console.error("Error reading initial movie ID:", e);
    }
  }

  // 3. Trigger the initial render. 
  // This will read the values from the dropdowns, update state.movie, 
  // and show/hide the correct grids!
  updateShowtimes();
});