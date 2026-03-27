// === Tab Filtering + Search ===
const tabs = document.querySelectorAll('.tab');
const mobileTabs = document.querySelectorAll('.mobile-tab');
const cards = document.querySelectorAll('.card');
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');
const searchInput = document.getElementById('search-input');

let activeFilter = 'all';

function applyFilters() {
  const query = (searchInput?.value || '').trim().toLowerCase();
  let visibleIndex = 0;
  cards.forEach(card => {
    const matchCategory = activeFilter === 'all' || card.dataset.category === activeFilter;
    const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
    const desc = card.querySelector('p')?.textContent.toLowerCase() || '';
    const matchSearch = !query || title.includes(query) || desc.includes(query);
    const match = matchCategory && matchSearch;
    if (match) {
      card.classList.remove('hidden');
      card.style.transitionDelay = `${visibleIndex * 0.03}s`;
      visibleIndex++;
      requestAnimationFrame(() => {
        card.classList.add('visible');
      });
    } else {
      card.classList.remove('visible');
      card.classList.add('hidden');
      card.style.transitionDelay = '0s';
    }
  });
}

function filterCards(category) {
  activeFilter = category;
  applyFilters();
}

function setActiveTab(category) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.filter === category));
  mobileTabs.forEach(t => t.classList.toggle('active', t.dataset.filter === category));
}

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const filter = tab.dataset.filter;
    setActiveTab(filter);
    filterCards(filter);
  });
});

mobileTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const filter = tab.dataset.filter;
    setActiveTab(filter);
    filterCards(filter);
    closeMobileMenu();
  });
});

// === Hamburger Menu ===
function closeMobileMenu() {
  mobileMenu.classList.remove('open');
  hamburger.classList.remove('active');
  hamburger.setAttribute('aria-expanded', 'false');
  mobileMenu.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    const isOpen = mobileMenu.classList.toggle('open');
    hamburger.classList.toggle('active');
    hamburger.setAttribute('aria-expanded', isOpen);
    mobileMenu.setAttribute('aria-hidden', !isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });
}

// === Search Input ===
if (searchInput) {
  searchInput.addEventListener('input', () => {
    applyFilters();
  });
}

// === Card Entrance Stagger ===
function revealCards() {
  const visibleCards = document.querySelectorAll('.card:not(.hidden)');
  visibleCards.forEach((card, i) => {
    card.style.transition = `opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.04}s, transform 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.04}s, box-shadow 0.35s ease, border-color 0.35s ease`;
    requestAnimationFrame(() => {
      card.classList.add('visible');
    });
  });
}

// Initial reveal on load
window.addEventListener('load', () => {
  // Hero entrance
  const heroEls = document.querySelectorAll('.hero-content > *');
  heroEls.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(16px)';
    el.style.transition = `opacity 0.6s ease ${i * 0.1}s, transform 0.6s ease ${i * 0.1}s`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      });
    });
  });

  // Cards stagger
  revealCards();
});

// === Card Hover: Glow + Subtle Tilt ===
cards.forEach(card => {
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
        const rx = ((y - cy) / cy) * -1.5;
        const ry = ((x - cx) / cx) * 1.5;
        card.style.transform = `translateY(-4px) perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg)`;
        card._ticking = false;
      });
    }
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
});

// === Stat Counter Animation ===
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
  const duration = 1000;
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

// === Scroll Progress (JS fallback) ===
const progressBar = document.getElementById('progress-bar');
if (progressBar && !CSS.supports('animation-timeline', 'scroll()')) {
  window.addEventListener('scroll', () => {
    const p = document.documentElement.scrollTop / (document.documentElement.scrollHeight - window.innerHeight);
    progressBar.style.transform = `scaleX(${Math.min(p, 1)})`;
  }, { passive: true });
}
