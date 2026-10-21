/* ============================================================
   ORCHARD CORE OPS — script.js
   ============================================================ */

/* ── Navbar scroll effect ───────────────────────────────────── */
(function () {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;
  const update = () => navbar.classList.toggle('scrolled', window.scrollY > 30);
  update();
  window.addEventListener('scroll', update, { passive: true });
})();

/* ── Hamburger menu ─────────────────────────────────────────── */
(function () {
  const btn   = document.getElementById('hamburger');
  const links = document.getElementById('navLinks');
  if (!btn || !links) return;
  btn.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!btn.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
    }
  });
})();

/* ── Intersection Observer — fade-up ────────────────────────── */
(function () {
  const els = document.querySelectorAll('.fade-up');
  if (!els.length) return;
  // Reset initial state for scroll-triggered animation
  els.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(40px)';
    el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
  });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, i * 80);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(el => io.observe(el));
})();

/* ── Sidebar active link on scroll (dashboard) ──────────────── */
(function () {
  const sbLinks = document.querySelectorAll('.sb-link[href^="#"]');
  if (!sbLinks.length) return;
  const sections = Array.from(sbLinks)
    .map(l => document.querySelector(l.getAttribute('href')))
    .filter(Boolean);

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 120) current = '#' + s.id;
    });
    sbLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === current));
  }, { passive: true });
})();

/* ── Animated counter numbers ───────────────────────────────── */
function animateCounter(el, target, duration = 1600) {
  const start = performance.now();
  const isFloat = target % 1 !== 0;
  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const val = target * ease;
    el.textContent = isFloat
      ? val.toFixed(1)
      : Math.floor(val).toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

(function () {
  const targets = document.querySelectorAll('.stat-number, .wm-big, .sc-num, .ts-num');
  if (!targets.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const raw = el.textContent.replace(/[^0-9.]/g, '');
      const num = parseFloat(raw);
      if (!isNaN(num) && num > 0) animateCounter(el, num);
      io.unobserve(el);
    });
  }, { threshold: 0.5 });
  targets.forEach(el => io.observe(el));
})();

/* ── Auto-dismiss alerts ────────────────────────────────────── */
(function () {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, max-height 0.5s ease';
      alert.style.opacity = '0';
      alert.style.maxHeight = '0';
      alert.style.overflow = 'hidden';
      alert.style.padding = '0';
      alert.style.margin = '0';
    }, 5000);
  });
})();

/* ── Smooth scroll for anchor links ────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

/* ── Bar fill animations triggered by IO ───────────────────── */
(function () {
  const bars = document.querySelectorAll('.metric-bar-fill, .kpi-bar, .cmp-bar, .ag-bar');
  if (!bars.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animation = 'bar-fill 1.5s ease-out both';
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });
  bars.forEach(b => io.observe(b));
})();

/* ── Particle / glow cursor effect (subtle) ────────────────── */
(function () {
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:fixed;top:0;left:0;pointer-events:none;z-index:9999;opacity:0.4;';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  let W = canvas.width  = window.innerWidth;
  let H = canvas.height = window.innerHeight;
  window.addEventListener('resize', () => {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  });

  const particles = [];
  let mx = -1000, my = -1000;
  window.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; }, { passive: true });

  class Particle {
    constructor(x, y) {
      this.x  = x + (Math.random() - 0.5) * 20;
      this.y  = y + (Math.random() - 0.5) * 20;
      this.vx = (Math.random() - 0.5) * 0.8;
      this.vy = (Math.random() - 0.5) * 0.8 - 0.5;
      this.life   = 1;
      this.decay  = 0.018 + Math.random() * 0.01;
      this.size   = 2 + Math.random() * 3;
      this.color  = Math.random() > 0.5 ? '34,197,94' : '192,192,192';
    }
    update() {
      this.x    += this.vx;
      this.y    += this.vy;
      this.life -= this.decay;
    }
    draw() {
      ctx.save();
      ctx.globalAlpha = this.life * 0.5;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size * this.life, 0, Math.PI * 2);
      ctx.fillStyle = `rgb(${this.color})`;
      ctx.fill();
      ctx.restore();
    }
  }

  let frame = 0;
  function loop() {
    ctx.clearRect(0, 0, W, H);
    frame++;
    if (frame % 3 === 0 && mx > 0) particles.push(new Particle(mx, my));
    if (particles.length > 80) particles.splice(0, particles.length - 80);
    for (let i = particles.length - 1; i >= 0; i--) {
      particles[i].update();
      particles[i].draw();
      if (particles[i].life <= 0) particles.splice(i, 1);
    }
    requestAnimationFrame(loop);
  }
  loop();
})();
