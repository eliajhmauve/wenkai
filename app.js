// === Scroll Reveal Animation ===
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -60px 0px'
};

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      // Stagger children cards
      const cards = entry.target.querySelectorAll('.card');
      cards.forEach((card, i) => {
        card.style.transitionDelay = `${i * 0.08}s`;
        card.classList.add('revealed');
      });
    }
  });
}, observerOptions);

// Observe sections and individual elements
document.querySelectorAll('.section, .hero-content > *').forEach(el => {
  el.classList.add('reveal');
  revealObserver.observe(el);
});

// === Hero staggered entrance ===
window.addEventListener('load', () => {
  const heroElements = document.querySelectorAll('.hero-content > *');
  heroElements.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = `opacity 0.8s ease ${i * 0.15}s, transform 0.8s ease ${i * 0.15}s`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      });
    });
  });
});

// === Card hover glow effect ===
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty('--glow-x', `${x}px`);
    card.style.setProperty('--glow-y', `${y}px`);
  });
});

// === Stat counter animation ===
const countObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = el.textContent.trim();

      // Only animate numbers
      if (target.includes('%')) {
        animateCount(el, 0, 100, '%');
      } else {
        const num = parseInt(target);
        if (!isNaN(num) && num > 0) {
          animateCount(el, 0, num, '');
        }
      }
      countObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

function animateCount(el, start, end, suffix) {
  const duration = 1500;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (end - start) * eased);
    el.textContent = current + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

document.querySelectorAll('.stat-num').forEach(el => {
  countObserver.observe(el);
});

// === Smooth nav background on scroll ===
const nav = document.querySelector('.nav');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  if (scrollY > 100) {
    nav.classList.add('nav-scrolled');
  } else {
    nav.classList.remove('nav-scrolled');
  }
  lastScroll = scrollY;
}, { passive: true });
