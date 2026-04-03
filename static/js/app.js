// ── Toast notifications ──
function showToast(msg, duration = 3200) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), duration);
}

(function () {
  const p = new URLSearchParams(window.location.search);
  if (p.get('donated')    === '1') showToast('🌱 Donation submitted! Thank you.');
  if (p.get('claimed')    === '1') showToast('✅ Food claimed! +10 points earned.');
  if (p.get('registered') === '1') showToast('🙋 Volunteer registered! Welcome aboard.');
  if (p.get('redeemed')   === '1') showToast('🎟 Voucher redeemed! Enjoy your reward.');
  // Clean query string from URL without reload
  if (p.toString()) window.history.replaceState({}, '', window.location.pathname);
})();

// ── Animated counter ──
(function () {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count, 10);
    if (!target) return;
    let n = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const timer = setInterval(() => {
      n = Math.min(n + step, target);
      el.textContent = n;
      if (n >= target) clearInterval(timer);
    }, 30);
  });
})();

// ── Mobile sidebar toggle ──
function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
}

// ── Disable submit button after click ──
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', () => {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) { btn.style.opacity = '0.6'; btn.disabled = true; }
  });
});
