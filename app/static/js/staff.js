// =============================================
// Staff Operations Terminal — JavaScript
// =============================================

// =====================
// CART STATE & FUNCTIONS
// =====================
let cart = [];
const TAX_RATE = 0.085;

function addToCart(name, price, type) {
    const existingItem = cart.find(item => item.name === name);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({ name, price, type, quantity: 1 });
    }
    updateCartDisplay();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
}

function updateQuantity(index, delta) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
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

    if (cart.length === 0) {
        cartItemsEl.innerHTML = `
            <div class="text-center text-gray-500 py-4 text-sm" id="emptyCartMsg">
                <svg class="w-8 h-8 mx-auto mb-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                Cart is empty — tap items to add
            </div>
        `;
        document.getElementById('subtotal').textContent = '$0.00';
        document.getElementById('tax').textContent = '$0.00';
        document.getElementById('total').textContent = '$0.00';
        return;
    }

    let html = '';
    let subtotal = 0;

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;

        const typeIcon = item.type === 'ticket' ? '🎬'
                       : item.type === 'snack'  ? '🍿'
                       : item.type === 'drink'  ? '🥤' : '📦';

        html += `
            <div class="cart-item flex items-center justify-between bg-dark-bg rounded-lg p-2">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                    <span class="text-lg">${typeIcon}</span>
                    <div class="min-w-0">
                        <p class="text-sm font-medium text-white truncate">${item.name}</p>
                        <p class="text-xs text-gray-500">$${item.price.toFixed(2)} each</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <div class="flex items-center bg-dark-surface rounded-lg">
                        <button onclick="updateQuantity(${index}, -1)" class="px-2 py-1 text-gray-400 hover:text-white transition-colors">-</button>
                        <span class="px-2 text-sm font-semibold">${item.quantity}</span>
                        <button onclick="updateQuantity(${index}, 1)" class="px-2 py-1 text-gray-400 hover:text-white transition-colors">+</button>
                    </div>
                    <span class="text-sm font-semibold text-crimson w-16 text-right">$${itemTotal.toFixed(2)}</span>
                    <button onclick="removeFromCart(${index})" class="p-1 text-gray-500 hover:text-red-500 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    });

    cartItemsEl.innerHTML = html;

    const tax   = subtotal * TAX_RATE;
    const total = subtotal + tax;

    document.getElementById('subtotal').textContent = '$' + subtotal.toFixed(2);
    document.getElementById('tax').textContent      = '$' + tax.toFixed(2);
    document.getElementById('total').textContent    = '$' + total.toFixed(2);
}

// =====================
// PAYMENT FUNCTIONS
// =====================
function processPayment(method) {
    if (cart.length === 0) {
        alert('Cart is empty! Add items to proceed.');
        return;
    }

    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const total    = subtotal * (1 + TAX_RATE);

    document.getElementById('paymentMethod').textContent  = method.toUpperCase();
    document.getElementById('paymentAmount').textContent  = '$' + total.toFixed(2);
    document.getElementById('receiptNumber').textContent  = Math.floor(Math.random() * 900000 + 100000);

    const modal   = document.getElementById('paymentModal');
    const content = document.getElementById('paymentModalContent');
    modal.classList.remove('hidden');
    setTimeout(() => {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closePaymentModal() {
    const modal   = document.getElementById('paymentModal');
    const content = document.getElementById('paymentModalContent');
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
        clearCart();
    }, 200);
}

function printReceipt() {
    alert('Printing receipt...');
}

// =====================
// POS TAB SWITCHING
// =====================
document.querySelectorAll('.pos-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.pos-tab-btn').forEach(b => {
            b.classList.remove('border-crimson', 'text-crimson', 'bg-dark-bg/50');
            b.classList.add('border-transparent', 'text-gray-400');
            const icon = b.querySelector('svg');
            if (b.dataset.tab !== 'refund' && b.dataset.tab !== 'scanner') {
                icon.setAttribute('fill', 'currentColor');
                icon.removeAttribute('stroke');
            }
        });
        btn.classList.add('border-crimson', 'text-crimson', 'bg-dark-bg/50');
        btn.classList.remove('border-transparent', 'text-gray-400');

        const tabId = btn.dataset.tab;
        document.querySelectorAll('.pos-tab-content').forEach(c => c.classList.add('hidden'));
        document.getElementById('tab-' + tabId).classList.remove('hidden');
        
        // Hide ticket selector if switching away from movies
        if (tabId !== 'movies' && typeof closeTicketSelector === 'function') {
            closeTicketSelector();
        }
    });
});


// =====================
// REFUND FUNCTIONS
// =====================
function searchBooking() {
    const searchValue = document.getElementById('refundSearch').value.trim();
    if (!searchValue) {
        alert('Please enter a Booking ID, email, or phone number');
        return;
    }
    document.getElementById('refundEmptyState').classList.add('hidden');
    document.getElementById('bookingResult').classList.remove('hidden');
    document.getElementById('resultBookingId').textContent = 'BK-' + Math.floor(Math.random() * 900000 + 100000);
}

function processRefund(type) {
    const reason = document.getElementById('refundReason').value;
    if (!reason) {
        alert('Please select a refund reason');
        return;
    }

    const amount = type === 'full' ? '$47.97' : '$31.98';
    document.getElementById('refundAmount').textContent = '-' + amount;
    document.getElementById('refundId').textContent     = Math.floor(Math.random() * 900000 + 100000);

    const modal   = document.getElementById('refundModal');
    const content = document.getElementById('refundModalContent');
    modal.classList.remove('hidden');
    setTimeout(() => {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeRefundModal() {
    const modal   = document.getElementById('refundModal');
    const content = document.getElementById('refundModalContent');
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
        document.getElementById('refundSearch').value = '';
        document.getElementById('bookingResult').classList.add('hidden');
        document.getElementById('refundEmptyState').classList.remove('hidden');
        document.getElementById('refundReason').value = '';
    }, 200);
}

// =====================
// TICKET SCANNER
// =====================
function validateTicket() {
    const ticketId = document.getElementById('ticketInput').value.trim().toUpperCase();
    if (!ticketId) {
        alert('Please enter or scan a ticket ID');
        return;
    }

    document.getElementById('scannerIdle').classList.add('hidden');
    document.getElementById('scannerSuccess').classList.add('hidden');
    document.getElementById('scannerFail').classList.add('hidden');

    setTimeout(() => {
        const isValid = ticketId.startsWith('TK-') && ticketId.length > 10 && !ticketId.includes('0000');

        if (isValid) {
            document.getElementById('scannerSuccess').classList.remove('hidden');
            document.getElementById('successTicketId').textContent = ticketId;
            const validCount = document.getElementById('validCount');
            validCount.textContent = parseInt(validCount.textContent) + 1;
            addRecentScan(ticketId, true);
        } else {
            document.getElementById('scannerFail').classList.remove('hidden');
            document.getElementById('failTicketId').textContent = ticketId;
            const invalidCount = document.getElementById('invalidCount');
            invalidCount.textContent = parseInt(invalidCount.textContent) + 1;
            addRecentScan(ticketId, false);
        }
    }, 500);
}

function resetScanner() {
    document.getElementById('ticketInput').value = '';
    document.getElementById('scannerIdle').classList.remove('hidden');
    document.getElementById('scannerSuccess').classList.add('hidden');
    document.getElementById('scannerFail').classList.add('hidden');
    document.getElementById('ticketInput').focus();
}

function addRecentScan(ticketId, isValid) {
    const recentScans = document.getElementById('recentScans');
    const iconClass   = isValid ? 'bg-green-500/20' : 'bg-red-500/20';
    const iconColor   = isValid ? 'text-green-400'  : 'text-red-400';
    const iconPath    = isValid ? 'M5 13l4 4L19 7'  : 'M6 18L18 6M6 6l12 12';
    const subtitle    = isValid ? 'Dune: Part Three • Hall 1' : 'Invalid ticket';

    const newScan = document.createElement('div');
    newScan.className = 'flex items-center justify-between bg-dark-surface rounded-lg p-3 cart-item';
    newScan.innerHTML = `
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 ${iconClass} rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${iconPath}"/>
                </svg>
            </div>
            <div>
                <p class="text-sm font-mono text-white">${ticketId}</p>
                <p class="text-xs ${isValid ? 'text-gray-500' : 'text-red-400'}">${subtitle}</p>
            </div>
        </div>
        <span class="text-xs text-gray-500">Just now</span>
    `;
    recentScans.insertBefore(newScan, recentScans.firstChild);
    while (recentScans.children.length > 5) {
        recentScans.removeChild(recentScans.lastChild);
    }
}

// Enter key support
document.getElementById('ticketInput').addEventListener('keypress', e => {
    if (e.key === 'Enter') validateTicket();
});
document.getElementById('refundSearch').addEventListener('keypress', e => {
    if (e.key === 'Enter') searchBooking();
});

// =====================
// SHIFT TIMER
// =====================
function updateShiftTime() {
    const now        = new Date();
    const shiftStart = new Date();
    shiftStart.setHours(9, 0, 0, 0);

    const diff    = now - shiftStart;
    const hours   = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);

    document.getElementById('shiftTime').textContent =
        String(hours).padStart(2, '0')   + ':' +
        String(minutes).padStart(2, '0') + ':' +
        String(seconds).padStart(2, '0');
}

setInterval(updateShiftTime, 1000);
updateShiftTime();

// =====================
// LAYOUT RESIZER
// =====================
const resizeHandle = document.getElementById('resizeHandle');
const leftPanel = document.getElementById('leftPanel');
let isResizing = false;

if (resizeHandle && leftPanel) {
    resizeHandle.addEventListener('mousedown', function(e) {
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        resizeHandle.classList.add('active');
        e.preventDefault(); // prevent text selection
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        // Calculate new width for left panel
        // constrain to a min width of 420px and max of ~75% screen width
        let newWidth = e.clientX;
        const minWidth = 420;
        const maxWidth = window.innerWidth * 0.75;
        
        if (newWidth < minWidth) newWidth = minWidth;
        if (newWidth > maxWidth) newWidth = maxWidth;
        
        leftPanel.style.width = newWidth + 'px';
        leftPanel.style.flex = 'none'; // remove flex-1 if present
    });

    document.addEventListener('mouseup', function(e) {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = 'default';
            resizeHandle.classList.remove('active');
        }
    });
}

// =====================
// TICKET SELECTION FLOW
// =====================
let currentSelectedTicket = null;
let currentSelectedSeats = [];

function openTicketSelector(id, name, price, gradient) {
    currentSelectedTicket = { id, name, price };
    currentSelectedSeats = [];
    
    document.getElementById('tsMovieName').textContent = name;
    
    // reset selection UI
    document.getElementById('tsShowtimeSelect').value = '';
    document.getElementById('tsSeatsContainer').classList.add('hidden');
    document.getElementById('tsAddToCartBtn').disabled = true;
    document.getElementById('tsAddToCartBtn').classList.add('opacity-50', 'cursor-not-allowed');
    document.getElementById('tsSelectedCount').textContent = '0 seats selected';
    document.getElementById('tsTotalPrice').textContent = '$0.00';
    
    // clear selected seats
    document.querySelectorAll('.seat-pos').forEach(seat => {
        seat.classList.remove('selected');
    });

    document.getElementById('ticketSelector').classList.remove('hidden');
}

function closeTicketSelector() {
    document.getElementById('ticketSelector').classList.add('hidden');
    currentSelectedTicket = null;
    currentSelectedSeats = [];
}

function onShowtimeChange(selectElement) {
    const seatsContainer = document.getElementById('tsSeatsContainer');
    if (selectElement.value) {
        seatsContainer.classList.remove('hidden');
    } else {
        seatsContainer.classList.add('hidden');
    }
}

function toggleSeat(seatElement, seatId) {
    if (seatElement.classList.contains('occupied')) return;
    
    const isSelected = seatElement.classList.contains('selected');
    
    if (isSelected) {
        seatElement.classList.remove('selected');
        currentSelectedSeats = currentSelectedSeats.filter(s => s !== seatId);
    } else {
        seatElement.classList.add('selected');
        currentSelectedSeats.push(seatId);
    }
    
    updateTicketSelectorFooter();
}

function updateTicketSelectorFooter() {
    const count = currentSelectedSeats.length;
    const btn = document.getElementById('tsAddToCartBtn');
    
    document.getElementById('tsSelectedCount').textContent = `${count} seat${count !== 1 ? 's' : ''} selected`;
    
    if (count > 0 && currentSelectedTicket) {
        const total = count * currentSelectedTicket.price;
        document.getElementById('tsTotalPrice').textContent = '$' + total.toFixed(2);
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
        document.getElementById('tsTotalPrice').textContent = '$0.00';
        btn.disabled = true;
        btn.classList.add('opacity-50', 'cursor-not-allowed');
    }
}

function addSelectedTicketsToCart() {
    if (!currentSelectedTicket || currentSelectedSeats.length === 0) return;
    
    const showtime = document.getElementById('tsShowtimeSelect').value;
    
    // Add each seat as a separate line item
    currentSelectedSeats.forEach(seat => {
        const itemName = `${currentSelectedTicket.name} (${showtime} - Seat ${seat})`;
        addToCart(itemName, currentSelectedTicket.price, 'ticket');
    });
    
    closeTicketSelector();
}

