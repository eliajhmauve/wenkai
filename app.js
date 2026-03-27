// === Scroll Reveal Animation ===
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      const cards = entry.target.querySelectorAll('.card');
      cards.forEach((card, i) => {
        card.style.transitionDelay = `${i * 0.06}s`;
        card.classList.add('revealed');
      });
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.section, .hero-content > *').forEach(el => {
  el.classList.add('reveal');
  revealObserver.observe(el);
});

// === Hero staggered entrance ===
window.addEventListener('load', () => {
  const heroElements = document.querySelectorAll('.hero-content > *');
  heroElements.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = `opacity 0.7s ease ${i * 0.12}s, transform 0.7s ease ${i * 0.12}s`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      });
    });
  });
});

// === Card hover glow + subtle 3D tilt ===
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    if (!card._ticking) {
      card._ticking = true;
      requestAnimationFrame(() => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty('--glow-x', `${x}px`);
        card.style.setProperty('--glow-y', `${y}px`);
        const cx = rect.width / 2, cy = rect.height / 2;
        const rx = ((y - cy) / cy) * -2.5;
        const ry = ((x - cx) / cx) * 2.5;
        card.style.transform = `translateY(-4px) perspective(600px) rotateX(${rx}deg) rotateY(${ry}deg)`;
        card._ticking = false;
      });
    }
  });
  card.addEventListener('mouseleave', () => { card.style.transform = ''; });
});

// === Stat counter animation ===
const countObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const num = parseInt(el.textContent.trim());
      if (!isNaN(num) && num > 0) animateCount(el, 0, num);
      countObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

function animateCount(el, start, end) {
  const duration = 1200;
  const startTime = performance.now();
  function update(t) {
    const p = Math.min((t - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(start + (end - start) * eased);
    if (p < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

document.querySelectorAll('.stat-num').forEach(el => countObserver.observe(el));

// === Scroll progress bar (JS fallback) ===
const progressBar = document.getElementById('progress-bar');
if (progressBar && !CSS.supports('animation-timeline', 'scroll()')) {
  window.addEventListener('scroll', () => {
    const p = document.documentElement.scrollTop / (document.documentElement.scrollHeight - window.innerHeight);
    progressBar.style.transform = `scaleX(${p})`;
  }, { passive: true });
}

// === Hamburger menu ===
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    const isOpen = mobileMenu.classList.toggle('open');
    hamburger.classList.toggle('active');
    hamburger.setAttribute('aria-expanded', isOpen);
    mobileMenu.setAttribute('aria-hidden', !isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      hamburger.classList.remove('active');
      hamburger.setAttribute('aria-expanded', 'false');
      mobileMenu.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    });
  });
}
