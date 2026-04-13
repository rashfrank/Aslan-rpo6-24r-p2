/* KaspiBoard — UI JavaScript v2 */

document.addEventListener('DOMContentLoaded', function () {

  /* --- 1. PAGE LOADER --- */
  const loader = document.getElementById('page-loader');
  if (loader) {
    loader.classList.add('is-hidden');
    setTimeout(() => loader.remove(), 400);
  }

  /* --- 2. HAMBURGER MENU --- */
  const toggleBtn = document.getElementById('navbar-toggle');
  const mobileMenu = document.getElementById('navbar-mobile-menu');
  if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener('click', function () {
      const isOpen = mobileMenu.classList.toggle('is-open');
      toggleBtn.setAttribute('aria-expanded', isOpen);
    });
  }

  /* --- 3. MOBILE SEARCH OVERLAY --- */
  const overlay = document.getElementById('mobile-search-overlay');
  if (overlay) {
    // Показываем как flex при открытии
    const origToggle = window.toggleOverlay;
    overlay.style.display = 'none';

    // Переопределяем кнопку меню снизу
    const menuBtn = document.getElementById('bottom-search-btn');
    if (menuBtn) {
      menuBtn.onclick = function () {
        const isOpen = overlay.style.display === 'flex';
        overlay.style.display = isOpen ? 'none' : 'flex';
      };
    }

    // Закрытие по клику на затемнение
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) overlay.style.display = 'none';
    });
  }

  /* --- 4. ALERT CLOSE --- */
  document.querySelectorAll('.alert__close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        alert.style.transition = 'opacity .25s, transform .25s';
        setTimeout(() => alert.remove(), 260);
      }
    });
  });

  /* --- 5. ALERT AUTO-HIDE --- */
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      if (alert.parentNode) {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity .35s';
        setTimeout(() => alert.remove(), 360);
      }
    }, 5000);
  });

  /* --- 6. FAV BUTTON ANIMATION --- */
  document.querySelectorAll('.ad-card__fav-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.style.transform = 'scale(1.35)';
      setTimeout(() => { btn.style.transform = ''; }, 200);
    });
  });

  /* --- 7. DATA-CONFIRM --- */
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm || 'Вы уверены?')) e.preventDefault();
    });
  });

  /* --- 8. STAR RATING - подсветка при наведении --- */
  const starLabels = document.querySelectorAll('.star-rating label');
  starLabels.forEach(function (label) {
    label.addEventListener('mouseenter', function () {
      // CSS уже обрабатывает это через :hover ~ label
    });
  });

  /* --- 9. ACTIVE BOTTOM NAV --- */
  const path = window.location.pathname;
  document.querySelectorAll('.bottom-nav__item').forEach(function (item) {
    const href = item.getAttribute('href');
    if (href && path === href) {
      item.classList.add('is-active');
    }
  });

  /* --- 10. LAZY IMAGES --- */
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          obs.unobserve(img);
        }
      });
    });
    lazyImages.forEach(img => obs.observe(img));
  }

});
