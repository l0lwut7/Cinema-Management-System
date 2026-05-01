// Auth Tab Switching
function switchAuthTab(tab) {
  const loginTab = document.getElementById('login-tab');
  const registerTab = document.getElementById('register-tab');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  if (tab === 'login') {
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  } else {
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
  }
}

// Password Toggle
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

// Accordion Toggle
function toggleAccordion(button) {
  const item = button.parentElement;
  const isOpen = item.classList.contains('open');
  
  // Close all accordions
  document.querySelectorAll('.accordion-item').forEach(acc => acc.classList.remove('open'));
  
  // Open clicked if it was closed
  if (!isOpen) {
    item.classList.add('open');
  }
}

// Form Handlers
function handleLogin() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  
  if (!email || !password) {
    document.getElementById('login-error').classList.remove('hidden');
    return;
  }
  
  document.getElementById('login-error').classList.add('hidden');
  
  // Simulate login by redirecting to dashboard
  window.location.href = '/dashboard';
}

function handleRegister() {
  // Simulate registration by redirecting to dashboard
  window.location.href = '/dashboard';
}

// Password Strength Indicator
document.getElementById('register-password')?.addEventListener('input', function(e) {
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
