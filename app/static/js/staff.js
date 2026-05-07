// =============================================
// Staff Operations Terminal — JavaScript
// =============================================

// =====================
// CART STATE
// =====================
let cart = [];
// ticket:     { name, price, type:'ticket',     quantity:1, screeningId, row, seatNumber }
// consumable: { name, price, type:'consumable', quantity,   consumableId }

const TAX_RATE     = 0.085;
let isProcessing   = false; // guard against double-clicks during AJAX

let currentScreeningId    = null;
let currentScreeningPrice = 0;
let selectedSeats         = []; // [{row:'A', number:3}]

// =====================
// CART FUNCTIONS
// =====================
function addConsumableToCart(consumableId, name, price) {
    const existing = cart.find(i => i.type === 'consumable' && i.consumableId === consumableId);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ name, price, type: 'consumable', quantity: 1, consumableId });
    }
    updateCartDisplay();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
}

function updateQuantity(index, delta) {
    const item = cart[index];
    if (!item) return;
    if (item.type === 'ticket' && delta > 0) return; // each seat is unique, can't duplicate
    item.quantity += delta;
    if (item.quantity <= 0) {
        removeFromCart(index);
    } else {
        updateCartDisplay();
    }
}

function clearCart() {
    cart = [];
    updateCartDisplay();
}

function updateCartDisplay() {
    const cartItemsEl = document.getElementById('cartItems');
    if (!cartItemsEl) return;

    if (cart.length === 0) {
        cartItemsEl.innerHTML = `
            <div class="text-center text-gray-600 py-10 text-sm">
                <svg class="w-10 h-10 mx-auto mb-3 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                <p class="text-gray-500">Cart is empty</p>
                <p class="text-xs text-gray-700 mt-1">Tap items to add</p>
            </div>`;
        ['subtotal', 'tax', 'total'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = '$0.00';
        });
        return;
    }

    let html     = '';
    let subtotal = 0;

    cart.forEach((item, index) => {
        const itemTotal    = item.price * item.quantity;
        subtotal          += itemTotal;
        const icon         = item.type === 'ticket' ? '🎬' : '🛒';
        const canIncrement = item.type !== 'ticket';

        html += `
            <div class="cart-item flex items-center justify-between bg-dark-bg rounded-lg p-2">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                    <span class="text-lg">${icon}</span>
                    <div class="min-w-0">
                        <p class="text-sm font-medium text-white truncate">${item.name}</p>
                        <p class="text-xs text-gray-500">$${item.price.toFixed(2)} each</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <div class="flex items-center bg-dark-surface rounded-lg">
                        <button onclick="updateQuantity(${index},-1)" class="px-2 py-1 text-gray-400 hover:text-white transition-colors">-</button>
                        <span class="px-2 text-sm font-semibold">${item.quantity}</span>
                        <button onclick="updateQuantity(${index},1)"
                                class="px-2 py-1 ${canIncrement ? 'text-gray-400 hover:text-white' : 'text-gray-700 cursor-not-allowed'} transition-colors"
                                ${canIncrement ? '' : 'disabled'}>+</button>
                    </div>
                    <span class="text-sm font-semibold text-crimson w-16 text-right">$${itemTotal.toFixed(2)}</span>
                    <button onclick="removeFromCart(${index})" class="p-1 text-gray-500 hover:text-red-500 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>`;
    });

    cartItemsEl.innerHTML = html;

    const tax   = subtotal * TAX_RATE;
    const total = subtotal + tax;

    const sub = document.getElementById('subtotal');
    const tx  = document.getElementById('tax');
    const tot = document.getElementById('total');
    if (sub) sub.textContent = '$' + subtotal.toFixed(2);
    if (tx)  tx.textContent  = '$' + tax.toFixed(2);
    if (tot) tot.textContent = '$' + total.toFixed(2);
}

// =====================
// PAYMENT FUNCTIONS
// =====================
async function processPayment(method) {
    if (isProcessing) return;
    if (cart.length === 0) { alert('Cart is empty! Add items to proceed.'); return; }

    const ticketItems     = cart.filter(i => i.type === 'ticket');
    const consumableItems = cart.filter(i => i.type === 'consumable');

    const screeningIds = [...new Set(ticketItems.map(i => i.screeningId).filter(Boolean))];
    if (screeningIds.length > 1) {
        alert('Cannot mix tickets from different screenings. Please process them separately.');
        return;
    }

    const screeningId = screeningIds.length ? screeningIds[0] : null;
    const seats       = ticketItems.map(i => ({ row: i.row, number: i.seatNumber }));
    const consumables = consumableItems.map(i => ({ id: i.consumableId, quantity: i.quantity }));
    const subtotal    = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);
    const total       = subtotal * (1 + TAX_RATE);

    isProcessing = true;
    setPaymentButtonsDisabled(true);

    try {
        const res  = await fetch('/staff/checkout', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ screening_id: screeningId, seats, consumables, method }),
        });
        const data = await res.json();

        if (!res.ok || data.error) {
            alert('Checkout failed: ' + (data.error || 'Unknown error'));
            return;
        }

        // Clear cart state without re-rendering (success screen takes over)
        cart = [];
        showCheckoutSuccess(data.booking_code || data.booking_id, data.ticket_ids, method, total);

    } catch (err) {
        alert('Network error: ' + err.message);
    } finally {
        isProcessing = false;
        setPaymentButtonsDisabled(false);
    }
}

function setPaymentButtonsDisabled(disabled) {
    document.querySelectorAll('.pos-btn').forEach(btn => {
        btn.disabled = disabled;
    });
}

function showCheckoutSuccess(bookingId, ticketIds, method, total) {
    // Populate dynamic fields
    const methodEl = document.getElementById('successMethod');
    const bidEl    = document.getElementById('successBookingId');
    const totEl    = document.getElementById('successTotal');
    const tidsEl   = document.getElementById('successTicketIds');

    if (methodEl) methodEl.textContent = method.toUpperCase();
    if (bidEl)    bidEl.textContent    = String(bookingId);
    if (totEl)    totEl.textContent    = '$' + total.toFixed(2);

    if (tidsEl) {
        tidsEl.innerHTML = (ticketIds || []).map(id => `
            <div class="bg-dark-elevated border border-slate-600 rounded-lg p-3 text-center">
                <p class="text-xs text-gray-500 mb-1">Ticket</p>
                <p class="font-mono font-bold text-white text-lg">#${id}</p>
            </div>`).join('');
    }

    // Swap views
    const cartView     = document.getElementById('cartView');
    const successView  = document.getElementById('checkoutSuccess');
    if (cartView)    cartView.classList.add('hidden');
    if (successView) { successView.classList.remove('hidden'); successView.classList.add('flex'); }
}

function resetCheckout() {
    const cartView    = document.getElementById('cartView');
    const successView = document.getElementById('checkoutSuccess');
    if (successView) { successView.classList.add('hidden'); successView.classList.remove('flex'); }
    if (cartView)    cartView.classList.remove('hidden');
    // cart array was already cleared in processPayment; this just repaints the empty state
    updateCartDisplay();
}

// =====================
// REFUND FUNCTIONS (2-step partial refund)
// =====================

async function lookUpBooking() {
    const input = document.getElementById('refundBookingCode');
    const raw   = input ? input.value.trim() : '';
    const code  = parseInt(raw, 10);

    if (!raw || isNaN(code) || raw.length !== 6) {
        alert('Please enter a valid 6-digit Booking Code');
        return;
    }

    try {
        const res  = await fetch(`/staff/booking-tickets/${code}`);
        const data = await res.json();

        if (!res.ok || data.error) {
            alert('Lookup failed: ' + (data.error || 'Booking not found'));
            return;
        }

        // Populate step 2 card
        const bcEl = document.getElementById('r2BookingCode');
        const mvEl = document.getElementById('r2Movie');
        const tmEl = document.getElementById('r2Time');
        const totEl= document.getElementById('r2Total');
        if (bcEl)  bcEl.textContent  = '#' + data.booking_code;
        if (mvEl)  mvEl.textContent  = data.movie || '—';
        if (tmEl)  tmEl.textContent  = data.start_display || '—';
        if (totEl) totEl.textContent = '$' + parseFloat(data.total_amount).toFixed(2);

        const listEl = document.getElementById('r2TicketList');
        if (listEl) {
            listEl.innerHTML = (data.tickets || []).map(t => `
                <label class="flex items-center gap-3 p-3 bg-dark-bg rounded-xl cursor-pointer hover:bg-dark-elevated transition-colors">
                    <input type="checkbox" class="refund-ticket-cb w-4 h-4 rounded border-dark-border bg-dark-surface text-crimson focus:ring-crimson flex-shrink-0"
                           value="${t.ticket_code}" onchange="syncRefundSelectAll()">
                    <span class="font-mono font-bold text-white text-sm">Seat ${t.seat}</span>
                    <span class="text-xs text-gray-500 ml-auto">${t.ticket_code}</span>
                </label>`).join('');
        }

        const selAllEl = document.getElementById('r2SelectAll');
        if (selAllEl) selAllEl.checked = false;

        document.getElementById('refundStep1').classList.add('hidden');
        document.getElementById('refundStep2').classList.remove('hidden');
        document.getElementById('refundSuccess').classList.add('hidden');

    } catch (err) {
        alert('Network error: ' + err.message);
    }
}

function toggleSelectAllRefund(checked) {
    document.querySelectorAll('.refund-ticket-cb').forEach(cb => { cb.checked = checked; });
}

function syncRefundSelectAll() {
    const all = document.querySelectorAll('.refund-ticket-cb');
    const allChecked = [...all].every(cb => cb.checked);
    const selAll = document.getElementById('r2SelectAll');
    if (selAll) selAll.checked = allChecked;
}

async function processPartialRefund() {
    const ticketCodes = [...document.querySelectorAll('.refund-ticket-cb:checked')].map(cb => cb.value);
    if (!ticketCodes.length) {
        alert('Please select at least one seat to refund');
        return;
    }

    try {
        const res  = await fetch('/staff/process_refund', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ ticket_codes: ticketCodes }),
        });
        const data = await res.json();

        if (!res.ok || data.error) {
            alert('Refund failed: ' + (data.error || 'Unknown error'));
            return;
        }

        const msgEl   = document.getElementById('rSuccessMsg');
        const seatsEl = document.getElementById('rSuccessSeats');
        if (msgEl)   msgEl.textContent   = data.fully_refunded ? 'Booking fully refunded.' : 'Partial refund processed.';
        if (seatsEl) seatsEl.textContent = 'Freed seats: ' + (data.refunded_seats || []).join(', ');

        document.getElementById('refundStep2').classList.add('hidden');
        document.getElementById('refundSuccess').classList.remove('hidden');

    } catch (err) {
        alert('Network error: ' + err.message);
    }
}

function resetRefundPanel() {
    const codeInput = document.getElementById('refundBookingCode');
    if (codeInput) codeInput.value = '';
    document.getElementById('refundStep1').classList.remove('hidden');
    document.getElementById('refundStep2').classList.add('hidden');
    document.getElementById('refundSuccess').classList.add('hidden');
}

function closeRefundModal() {
    const modal   = document.getElementById('refundModal');
    const content = document.getElementById('refundModalContent');
    if (!modal || !content) return;
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
        const rs = document.getElementById('refundSearch');
        const br = document.getElementById('bookingResult');
        const es = document.getElementById('refundEmptyState');
        if (rs) rs.value = '';
        if (br) br.classList.add('hidden');
        if (es) es.classList.remove('hidden');
        _currentRefundTicketId = null;
    }, 200);
}

// =====================
// TICKET SCANNER
// =====================
// =====================
// BOOKING SCANNER (Tab)
// =====================

async function validateBooking() {
    const input = document.getElementById('bookingCodeInput');
    const raw   = input ? input.value.trim() : '';

    if (!raw) return;

    if (!/^\d{6}$/.test(raw)) {
        appendScanLog(false, raw, 'Must be exactly 6 digits');
        if (input) { input.value = ''; input.focus(); }
        return;
    }

    try {
        const res  = await fetch('/staff/validate_booking', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ booking_code: parseInt(raw, 10) }),
        });
        const data = await res.json();

        if (data.valid) {
            appendScanLog(true, raw, `${data.movie || '—'} · ${data.seats || ''}`);
        } else {
            appendScanLog(false, raw, data.reason || 'Invalid booking');
        }
    } catch (err) {
        appendScanLog(false, raw, 'Network error');
    }

    if (input) { input.value = ''; input.focus(); }
}

function appendScanLog(success, bookingCode, detail) {
    const logsEl   = document.getElementById('scannerLogs');
    const emptyEl  = document.getElementById('scannerLogsEmpty');
    if (!logsEl) return;

    // Hide empty state on first scan
    if (emptyEl) emptyEl.classList.add('hidden');

    const now = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    const el  = document.createElement('div');
    el.className = 'scan-log-entry flex items-center gap-3 rounded-xl p-3 ' +
        (success
            ? 'bg-green-500/10 border border-green-500/25'
            : 'bg-red-500/10 border border-red-500/25');

    const iconPath = success ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12';
    const iconColor = success ? 'text-green-400' : 'text-red-400';
    const iconBg    = success ? 'bg-green-500/20' : 'bg-red-500/20';
    const labelColor = success ? 'text-green-400' : 'text-red-400';
    const label      = success ? `Valid Booking: #${bookingCode} — All tickets verified.`
                               : `Invalid Booking: #${bookingCode || '?'} — ${detail}`;

    el.innerHTML = `
        <div class="w-8 h-8 ${iconBg} rounded-full flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="${iconPath}"/>
            </svg>
        </div>
        <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold ${labelColor} truncate">${label}</p>
            ${success ? `<p class="text-xs text-gray-500 truncate">${detail}</p>` : ''}
        </div>
        <span class="text-xs text-gray-600 flex-shrink-0">${now}</span>`;

    // Prepend (newest at top)
    logsEl.insertBefore(el, logsEl.firstChild);

    // Rule of 3: remove the oldest entry if there are more than 3
    while (logsEl.children.length > 3) {
        logsEl.removeChild(logsEl.lastChild);
    }
}

async function validateTicket() {
    const input      = document.getElementById('ticketInput');
    const ticketCode = input ? input.value.trim().toUpperCase() : '';

    const idleEl    = document.getElementById('scannerIdle');
    const successEl = document.getElementById('scannerSuccess');
    const failEl    = document.getElementById('scannerFail');

    if (idleEl)    idleEl.classList.add('hidden');
    if (successEl) successEl.classList.add('hidden');
    if (failEl)    failEl.classList.add('hidden');

    if (!ticketCode) {
        if (failEl) failEl.classList.remove('hidden');
        const ftEl = document.getElementById('failTicketId');
        const frEl = document.getElementById('failReason');
        if (ftEl) ftEl.textContent = '(empty)';
        if (frEl) frEl.textContent = 'Please enter a ticket code';
        return;
    }

    try {
        const res  = await fetch('/staff/validate_ticket', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ ticket_code: ticketCode }),
        });
        const data = await res.json();

        if (data.valid) {
            if (successEl) successEl.classList.remove('hidden');
            const stEl  = document.getElementById('successTicketId');
            const smEl  = document.getElementById('successMovie');
            const ssEl  = document.getElementById('successSeat');
            const stmEl = document.getElementById('successTime');
            const sgEl  = document.getElementById('successGuest');
            if (stEl)  stEl.textContent  = ticketCode;
            if (smEl)  smEl.textContent  = data.movie  || '—';
            if (ssEl)  ssEl.textContent  = `Hall ${data.saloon} / Seat ${data.seat}`;
            if (stmEl) stmEl.textContent = '—';
            if (sgEl)  sgEl.textContent  = '—';

            const vc = document.getElementById('validCount');
            if (vc) vc.textContent = parseInt(vc.textContent) + 1;
            addRecentScan(ticketCode, true, data.movie);
        } else {
            if (failEl) failEl.classList.remove('hidden');
            const ftEl = document.getElementById('failTicketId');
            const frEl = document.getElementById('failReason');
            if (ftEl) ftEl.textContent = ticketCode;
            if (frEl) frEl.textContent = data.reason || 'Invalid ticket';

            const ic = document.getElementById('invalidCount');
            if (ic) ic.textContent = parseInt(ic.textContent) + 1;
            addRecentScan(ticketCode, false, data.reason);
        }
    } catch (err) {
        if (failEl) failEl.classList.remove('hidden');
        const ftEl = document.getElementById('failTicketId');
        const frEl = document.getElementById('failReason');
        if (ftEl) ftEl.textContent = ticketCode;
        if (frEl) frEl.textContent = 'Network error';
    }
}

function resetScanner() {
    const input = document.getElementById('ticketInput');
    if (input) { input.value = ''; input.focus(); }
    const idleEl    = document.getElementById('scannerIdle');
    const successEl = document.getElementById('scannerSuccess');
    const failEl    = document.getElementById('scannerFail');
    if (idleEl)    idleEl.classList.remove('hidden');
    if (successEl) successEl.classList.add('hidden');
    if (failEl)    failEl.classList.add('hidden');
}

function addRecentScan(ticketId, isValid, subtitle) {
    const recentScans = document.getElementById('recentScans');
    if (!recentScans) return;
    const iconClass = isValid ? 'bg-green-500/20' : 'bg-red-500/20';
    const iconColor = isValid ? 'text-green-400'  : 'text-red-400';
    const iconPath  = isValid ? 'M5 13l4 4L19 7'  : 'M6 18L18 6M6 6l12 12';

    const el = document.createElement('div');
    el.className = 'flex items-center justify-between bg-dark-surface rounded-lg p-3 cart-item';
    el.innerHTML = `
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 ${iconClass} rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${iconPath}"/>
                </svg>
            </div>
            <div>
                <p class="text-sm font-mono text-white">${ticketId}</p>
                <p class="text-xs ${isValid ? 'text-gray-500' : 'text-red-400'}">${subtitle || (isValid ? 'Valid' : 'Invalid')}</p>
            </div>
        </div>
        <span class="text-xs text-gray-500">Just now</span>`;
    recentScans.insertBefore(el, recentScans.firstChild);
    while (recentScans.children.length > 5) recentScans.removeChild(recentScans.lastChild);
}

// =====================
// SCREENING / TICKET FLOW
// =====================
function openScreeningSelector(screeningId, movieName, basePrice) {
    currentScreeningId    = screeningId;
    currentScreeningPrice = basePrice;
    selectedSeats         = [];

    const nameEl = document.getElementById('tsMovieName');
    const ctnrEl = document.getElementById('tsSeatsContainer');
    const btn    = document.getElementById('tsAddToCartBtn');
    const cntEl  = document.getElementById('tsSelectedCount');
    const prEl   = document.getElementById('tsTotalPrice');
    const selEl  = document.getElementById('ticketSelector');

    if (nameEl) nameEl.textContent = movieName;
    if (ctnrEl) ctnrEl.innerHTML = `
        <div class="text-center text-gray-400 py-8">
            <svg class="w-8 h-8 mx-auto mb-2 animate-spin text-crimson" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <p class="mt-2 text-sm">Loading seats...</p>
        </div>`;
    if (btn) { btn.disabled = true; btn.classList.add('opacity-50', 'cursor-not-allowed'); }
    if (cntEl) cntEl.textContent = '0 seats selected';
    if (prEl)  prEl.textContent  = '$0.00';
    if (selEl) selEl.classList.remove('hidden');

    loadSeats(screeningId);
}

async function loadSeats(screeningId) {
    const ctnrEl = document.getElementById('tsSeatsContainer');
    try {
        const res  = await fetch(`/staff/seats/${screeningId}`);
        const data = await res.json();
        if (!res.ok || data.error) {
            if (ctnrEl) ctnrEl.innerHTML =
                `<p class="text-crimson text-center py-4">Error loading seats: ${data.error || 'Unknown'}</p>`;
            return;
        }
        renderSeats(data.rows);
    } catch (err) {
        if (ctnrEl) ctnrEl.innerHTML =
            `<p class="text-crimson text-center py-4">Network error: ${err.message}</p>`;
    }
}

function renderSeats(rows) {
    const ctnrEl  = document.getElementById('tsSeatsContainer');
    if (!ctnrEl) return;
    const rowKeys = Object.keys(rows).sort();

    if (rowKeys.length === 0) {
        ctnrEl.innerHTML = `<p class="text-gray-400 text-center py-8">No seats found for this saloon.</p>`;
        return;
    }

    let html = `
        <div class="bg-dark-bg rounded-xl border border-dark-border p-6 overflow-x-auto">
            <div class="w-full max-w-lg mx-auto mb-8">
                <div class="h-2 w-full bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent rounded-full opacity-60"></div>
                <p class="text-center text-xs text-gray-500 font-bold uppercase tracking-[0.3em] mt-2">Screen</p>
            </div>
            <div class="flex flex-col gap-3 max-w-xl mx-auto">`;

    rowKeys.forEach(rowLetter => {
        const seats = rows[rowLetter];
        html += `<div class="flex items-center justify-center gap-2">
            <span class="w-6 text-center text-xs font-bold text-gray-600">${rowLetter}</span>
            <div class="flex gap-2">`;

        seats.forEach((seat, i) => {
            const cls     = seat.occupied ? 'seat-pos occupied' : 'seat-pos';
            const onclick = seat.occupied ? '' : `onclick="toggleSeat(this,'${rowLetter}',${seat.number})"`;
            html += `<div class="${cls}" ${onclick} title="Seat ${rowLetter}${seat.number}">${seat.number}</div>`;
        });

        html += `</div></div>`;
    });

    html += `
            </div>
            <div class="flex justify-center gap-6 mt-8 pt-6 border-t border-dark-border text-xs text-gray-400">
                <div class="flex items-center gap-2"><div class="w-4 h-4 border border-dark-border bg-dark-bg rounded-sm"></div> Available</div>
                <div class="flex items-center gap-2"><div class="w-4 h-4 bg-crimson rounded-sm"></div> Selected</div>
                <div class="flex items-center gap-2"><div class="w-4 h-4 bg-dark-elevated rounded-sm"></div> Occupied</div>
            </div>
        </div>`;

    ctnrEl.innerHTML = html;
}

function closeTicketSelector() {
    const selEl = document.getElementById('ticketSelector');
    if (selEl) selEl.classList.add('hidden');
    currentScreeningId    = null;
    currentScreeningPrice = 0;
    selectedSeats         = [];
}

function toggleSeat(el, row, number) {
    if (el.classList.contains('occupied')) return;
    const idx = selectedSeats.findIndex(s => s.row === row && s.number === number);
    if (idx >= 0) {
        el.classList.remove('selected');
        selectedSeats.splice(idx, 1);
    } else {
        el.classList.add('selected');
        selectedSeats.push({ row, number });
    }
    updateTicketSelectorFooter();
}

function updateTicketSelectorFooter() {
    const count  = selectedSeats.length;
    const btn    = document.getElementById('tsAddToCartBtn');
    const cntEl  = document.getElementById('tsSelectedCount');
    const prEl   = document.getElementById('tsTotalPrice');

    if (cntEl) cntEl.textContent = `${count} seat${count !== 1 ? 's' : ''} selected`;

    if (count > 0) {
        if (prEl) prEl.textContent = '$' + (count * currentScreeningPrice).toFixed(2);
        if (btn)  { btn.disabled = false; btn.classList.remove('opacity-50', 'cursor-not-allowed'); }
    } else {
        if (prEl) prEl.textContent = '$0.00';
        if (btn)  { btn.disabled = true; btn.classList.add('opacity-50', 'cursor-not-allowed'); }
    }
}

function addSelectedTicketsToCart() {
    if (!currentScreeningId || selectedSeats.length === 0) return;
    const movieName = document.getElementById('tsMovieName')?.textContent || 'Movie';

    selectedSeats.forEach(seat => {
        cart.push({
            name:        `${movieName} — Seat ${seat.row}${seat.number}`,
            price:       currentScreeningPrice,
            type:        'ticket',
            quantity:    1,
            screeningId: currentScreeningId,
            row:         seat.row,
            seatNumber:  seat.number,
        });
    });

    updateCartDisplay();
    closeTicketSelector();
}

// =====================
// LAYOUT RESIZER
// =====================
function initResizer() {
    const resizeHandle = document.getElementById('resizeHandle');
    const leftPanel    = document.getElementById('leftPanel');
    if (!resizeHandle || !leftPanel) return;

    let isResizing = false;

    resizeHandle.addEventListener('mousedown', e => {
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        resizeHandle.classList.add('active');
        e.preventDefault();
    });
    document.addEventListener('mousemove', e => {
        if (!isResizing) return;
        let w = Math.min(Math.max(e.clientX, 420), window.innerWidth * 0.75);
        leftPanel.style.width = w + 'px';
        leftPanel.style.flex  = 'none';
    });
    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = 'default';
            resizeHandle.classList.remove('active');
        }
    });
}

// =====================
// BOOTSTRAP (safe init)
// =====================
document.addEventListener('DOMContentLoaded', () => {

    // Tab switching
    document.querySelectorAll('.pos-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pos-tab-btn').forEach(b => {
                b.classList.remove('border-crimson', 'text-crimson', 'bg-dark-bg/50');
                b.classList.add('border-transparent', 'text-gray-400');
            });
            btn.classList.add('border-crimson', 'text-crimson', 'bg-dark-bg/50');
            btn.classList.remove('border-transparent', 'text-gray-400');

            const tabId  = btn.dataset.tab;
            const tabEl  = document.getElementById('tab-' + tabId);
            document.querySelectorAll('.pos-tab-content').forEach(c => c.classList.add('hidden'));
            if (tabEl) tabEl.classList.remove('hidden');

            if (tabId !== 'movies') closeTicketSelector();
        });
    });

    // Enter-key shortcuts (guarded)
    const bookingCodeInput  = document.getElementById('bookingCodeInput');
    const refundBookingCode = document.getElementById('refundBookingCode');
    if (bookingCodeInput)  bookingCodeInput.addEventListener('keypress',  e => { if (e.key === 'Enter') validateBooking(); });
    if (refundBookingCode) refundBookingCode.addEventListener('keypress', e => { if (e.key === 'Enter') lookUpBooking(); });

    initResizer();
});
