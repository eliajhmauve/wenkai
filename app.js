// === Scroll Reveal Animation ===
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -60px 0px'
};

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      const cards = entry.target.querySelectorAll('.card');
      cards.forEach((card, i) => {
        card.style.transitionDelay = `${i * 0.08}s`;
        card.classList.add('revealed');
      });
      revealObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

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

// === Card hover glow + 3D tilt effect ===
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

        // 3D tilt
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -4;
        const rotateY = ((x - centerX) / centerX) * 4;
        card.style.transform = `translateY(-6px) perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

        card._ticking = false;
      });
    }
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
});

// === Stat counter animation ===
const countObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = el.textContent.trim();

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

window.addEventListener('scroll', () => {
  if (window.scrollY > 100) {
    nav.classList.add('nav-scrolled');
  } else {
    nav.classList.remove('nav-scrolled');
  }
}, { passive: true });

// === Scroll progress bar (JS fallback for browsers without scroll-timeline) ===
const progressBar = document.getElementById('progress-bar');
if (progressBar && !CSS.supports('animation-timeline', 'scroll()')) {
  window.addEventListener('scroll', () => {
    const scrollTop = document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollTop / scrollHeight;
    progressBar.style.transform = `scaleX(${progress})`;
  }, { passive: true });
}

// === Hamburger menu toggle ===
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

// === Parallax hero on scroll ===
const heroContent = document.querySelector('.hero-content');
const heroBg = document.querySelector('.hero-bg');
if (heroContent && heroBg) {
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight) {
      heroContent.style.transform = `translateY(${y * 0.15}px)`;
      heroContent.style.opacity = 1 - y / (window.innerHeight * 0.8);
      heroBg.style.transform = `translateY(${y * 0.3}px)`;
    }
  }, { passive: true });
}
