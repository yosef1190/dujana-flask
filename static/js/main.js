// ═══════════════════════════════════════════════════════════════════════════
//  DUJANA SPARE PARTS — MAIN JS
// ═══════════════════════════════════════════════════════════════════════════

// ── STATE ────────────────────────────────────────────────────────────────────
let allProducts = [];
let currentLang = 'en';
let currentSlide = 0;
let slideInterval = null;
let isAdmin = false;
let statsAnimated = false;

// ── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  checkAuth();
  loadProducts();
  initSlider();
  buildDots();
  initScrollEffects();
  initHeader();
});

// ── PARTICLES ────────────────────────────────────────────────────────────────
function initParticles() {
  const canvas = document.getElementById('particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = Array.from({length:40}, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 2 + 0.5,
    dx: (Math.random() - 0.5) * 0.4,
    dy: (Math.random() - 0.5) * 0.4,
    o: Math.random() * 0.5 + 0.1
  }));

  function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(5,150,105,${p.o})`;
      ctx.fill();
      p.x += p.dx; p.y += p.dy;
      if (p.x<0||p.x>canvas.width) p.dx*=-1;
      if (p.y<0||p.y>canvas.height) p.dy*=-1;
    });
    requestAnimationFrame(draw);
  }
  draw();

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });
}

// ── HEADER SCROLL ────────────────────────────────────────────────────────────
function initHeader() {
  const header = document.getElementById('mainHeader');
  const scrollTop = document.getElementById('scrollTop');
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 20);
    scrollTop.classList.toggle('visible', window.scrollY > 400);
    updateActiveNav();
  });
}

function updateActiveNav() {
  const sections = ['hero','products','blog','about','contact'];
  const links = document.querySelectorAll('.nav-links a');
  let current = '';
  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el && window.scrollY >= el.offsetTop - 100) current = id;
  });
  links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === `#${current}`));
}

function toggleMobileNav() {
  document.getElementById('mobileNav').classList.toggle('open');
}

// ── SCROLL REVEAL & STATS ─────────────────────────────────────────────────────
function initScrollEffects() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        if (e.target.classList.contains('stats-bar') && !statsAnimated) {
          statsAnimated = true;
          animateStats();
        }
      }
    });
  }, { threshold: 0.1 });

  // Only animate these — NOT product cards
  document.querySelectorAll('.feature-card, .blog-card, .testimonial-card, .contact-item, .stats-bar').forEach(el => {
    el.classList.add('animate-reveal');
    observer.observe(el);
  });

  // Immediately reveal stat-cards inside stats-bar (handled by stats-bar observer)
  observer.observe(document.querySelector('.stats-bar'));
}

function animateStats() {
  document.querySelectorAll('.stat-card').forEach((card, i) => {
    const target = parseInt(card.dataset.count);
    const suffix = card.dataset.suffix || '';
    const el = document.getElementById(`stat${i}`);
    if (!el) return;
    let start = 0;
    const duration = 1800;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(ease * target).toLocaleString() + (progress === 1 ? suffix : '');
      if (progress < 1) requestAnimationFrame(step);
    };
    setTimeout(() => requestAnimationFrame(step), i * 150);
  });
}

// ── LANGUAGE ─────────────────────────────────────────────────────────────────
function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'am' : 'en';
  document.getElementById('langLabel').textContent = currentLang === 'en' ? 'አማርኛ' : 'English';
  document.body.classList.toggle('amharic', currentLang === 'am');
  applyLanguage();
  renderProducts(filterList());
}

function applyLanguage() {
  document.querySelectorAll('[data-en]').forEach(el => {
    if (el.tagName !== 'INPUT') {
      el.textContent = currentLang === 'am' ? (el.dataset.am || el.dataset.en) : el.dataset.en;
    }
  });
  document.querySelectorAll('[data-placeholder-en]').forEach(el => {
    el.placeholder = currentLang === 'am' ? (el.dataset.placeholderAm || el.dataset.placeholderEn) : el.dataset.placeholderEn;
  });
  updateCategoryFilter();
}

// ── PRODUCTS ─────────────────────────────────────────────────────────────────
async function loadProducts() {
  showSpinner();
  try {
    const res = await fetch('/api/products');
    const data = await res.json();
    if (data.success) {
      allProducts = data.products;
      updateCategoryFilter();
      renderProducts(allProducts);
    }
  } catch { showToast('Failed to load products', 'error'); }
  finally { hideSpinner(); }
}

function renderProducts(products) {
  const grid = document.getElementById('productGrid');
  const noP  = document.getElementById('noProducts');
  const cnt  = document.getElementById('productCount');
  cnt.textContent = `${products.length} ${currentLang === 'am' ? 'ምርቶች' : 'products'}`;
  if (!products.length) { grid.innerHTML = ''; noP.classList.remove('hidden'); return; }
  noP.classList.add('hidden');
  grid.innerHTML = products.map((p, i) => cardHTML(p, i)).join('');
}

function cardHTML(p, i) {
  const name     = currentLang === 'am' ? p.name_am : p.name_en;
  const category = currentLang === 'am' ? p.category_am : p.category_en;
  const desc     = currentLang === 'am' ? p.desc_am : p.desc_en;
  const seller   = currentLang === 'am' ? p.seller_am : p.seller_en;
  const low      = p.stock < 5;
  const stockTxt = currentLang === 'am'
    ? (p.stock === 0 ? 'አልተቀረ' : `${p.stock} ቀርቷል`)
    : (p.stock === 0 ? 'Out of stock' : `${p.stock} in stock`);

  const imgHtml = p.image_path
    ? `<img class="product-img" src="${p.image_path}" alt="${name}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'product-img-placeholder\\'><i class=\\'fa-solid fa-car-side\\'></i></div>'">`
    : `<div class="product-img-placeholder"><i class="fa-solid fa-car-side"></i></div>`;

  const adminBtns = isAdmin ? `
    <button class="btn-edit"   onclick="event.stopPropagation();openProductModal('${p.id}')"><i class="fa-solid fa-pen"></i></button>
    <button class="btn-delete" onclick="event.stopPropagation();deleteProduct('${p.id}')"><i class="fa-solid fa-trash"></i></button>` : '';

  const contactLabel = currentLang === 'am' ? 'ሻጭ ያነጋግሩ' : 'Contact Seller';

  return `
  <div class="product-card" onclick="openDetailModal('${p.id}')">
    ${imgHtml}
    <div class="product-body">
      <div class="product-category">${category}</div>
      <div class="product-name">${name}</div>
      <div class="product-desc">${desc}</div>
      <div class="product-footer">
        <span class="product-price">${Number(p.price).toLocaleString()} ETB</span>
        <span class="product-stock${low?' low':''}">${stockTxt}</span>
      </div>
    </div>
    <div class="product-actions" onclick="event.stopPropagation()">
      <button class="btn-contact" onclick="toggleSellerInfo('${p.id}')">
        <i class="fa-solid fa-phone"></i> ${contactLabel}
      </button>
      ${adminBtns}
    </div>
    <div class="seller-info" id="seller-${p.id}">
      <p><i class="fa-solid fa-store"></i> ${seller}</p>
      <p><a href="tel:${p.phone}"><i class="fa-solid fa-phone"></i> ${p.phone}</a></p>
    </div>
  </div>`;
}

function toggleSellerInfo(id) {
  document.getElementById(`seller-${id}`)?.classList.toggle('visible');
}

function filterProducts() { renderProducts(filterList()); }

function filterList() {
  const q   = document.getElementById('searchInput').value.toLowerCase();
  const cat = document.getElementById('categoryFilter').value;
  const pr  = document.getElementById('priceFilter').value;
  return allProducts.filter(p => {
    const nameMatch = p.name_en.toLowerCase().includes(q) || p.name_am.includes(q);
    const catMatch  = !cat || p.category_en === cat;
    let priceMatch  = true;
    if (pr) {
      const v = Number(p.price);
      if (pr==='0-500')      priceMatch = v<500;
      if (pr==='500-1500')   priceMatch = v>=500 && v<=1500;
      if (pr==='1500-5000')  priceMatch = v>1500 && v<=5000;
      if (pr==='5000+')      priceMatch = v>5000;
    }
    return nameMatch && catMatch && priceMatch;
  });
}

function updateCategoryFilter() {
  const sel = document.getElementById('categoryFilter');
  const cur = sel.value;
  const cats = [...new Set(allProducts.map(p => p.category_en))];
  const lbl = currentLang === 'am' ? 'ሁሉም ምድቦች' : 'All Categories';
  sel.innerHTML = `<option value="">${lbl}</option>` + cats.map(c => {
    const am = allProducts.find(p=>p.category_en===c)?.category_am || c;
    return `<option value="${c}" ${cur===c?'selected':''}>${currentLang==='am'?am:c}</option>`;
  }).join('');
}

// ── DETAIL MODAL ──────────────────────────────────────────────────────────────
function openDetailModal(id) {
  const p = allProducts.find(x => x.id === id);
  if (!p) return;
  const name     = currentLang === 'am' ? p.name_am : p.name_en;
  const category = currentLang === 'am' ? p.category_am : p.category_en;
  const desc     = currentLang === 'am' ? p.desc_am : p.desc_en;
  const seller   = currentLang === 'am' ? p.seller_am : p.seller_en;
  const imgHtml  = p.image_path
    ? `<img class="detail-img" src="${p.image_path}" alt="${name}">`
    : `<div class="detail-img-ph"><i class="fa-solid fa-car-side"></i></div>`;

  document.getElementById('detailContent').innerHTML = `
    <div class="detail-grid">
      <div>${imgHtml}</div>
      <div>
        <span class="detail-badge">${category}</span>
        <div class="detail-title">${name}</div>
        <div class="detail-price">${Number(p.price).toLocaleString()} ETB</div>
        <div class="detail-desc">${desc}</div>
        <div class="detail-meta">
          <div class="detail-row"><i class="fa-solid fa-boxes-stacked"></i> ${currentLang==='am'?'ክምችት':'Stock'}: <strong>${p.stock}</strong></div>
          <div class="detail-row"><i class="fa-solid fa-store"></i> ${currentLang==='am'?'ሻጭ':'Seller'}: <strong>${seller}</strong></div>
          <div class="detail-row"><i class="fa-solid fa-phone"></i> <a href="tel:${p.phone}">${p.phone}</a></div>
        </div>
        <a href="tel:${p.phone}" class="btn-call"><i class="fa-solid fa-phone"></i> ${currentLang==='am'?'ደውሉ':'Call Now'}</a>
      </div>
    </div>`;
  document.getElementById('detailModal').classList.remove('hidden');
}
function closeDetailModal() { document.getElementById('detailModal').classList.add('hidden'); }

// ── AUTH ──────────────────────────────────────────────────────────────────────
async function checkAuth() {
  try {
    const res = await fetch('/api/check-auth');
    const data = await res.json();
    if (data.authenticated) setAdminMode(data.username);
  } catch {}
}

function setAdminMode(username) {
  isAdmin = true;
  document.getElementById('adminName').textContent = username;
  document.getElementById('adminPanel').classList.remove('hidden');
  document.getElementById('adminBtn').innerHTML = `<i class="fa-solid fa-shield-halved"></i> ${username}`;
  renderProducts(filterList());
}

function openLoginModal() {
  if (isAdmin) {
    document.getElementById('adminPanel').scrollIntoView({behavior:'smooth'});
    return;
  }
  document.getElementById('loginModal').classList.remove('hidden');
  setTimeout(() => document.getElementById('loginPassword').focus(), 300);
}
function closeLoginModal() {
  document.getElementById('loginModal').classList.add('hidden');
  document.getElementById('loginPassword').value = '';
}

async function handleLogin(e) {
  e.preventDefault();
  const password = document.getElementById('loginPassword').value;
  showSpinner();
  try {
    const res = await fetch('/api/login', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ password })
    });
    const data = await res.json();
    if (data.success) {
      setAdminMode(data.admin.username);
      closeLoginModal();
      showToast(currentLang==='am'?'ዳሽቦርድ ተከፈተ':'Dashboard unlocked', 'success');
    } else {
      showToast(currentLang==='am'?'የይለፍ ቃሉ ትክክል አይደለም':'Incorrect password', 'error');
    }
  } catch { showToast('Connection error', 'error'); }
  finally { hideSpinner(); }
}

async function handleLogout() {
  showSpinner();
  try {
    await fetch('/api/logout', {method:'POST'});
    isAdmin = false;
    document.getElementById('adminPanel').classList.add('hidden');
    document.getElementById('adminBtn').innerHTML = `<i class="fa-solid fa-shield-halved"></i> Admin`;
    showToast(currentLang==='am'?'ወጥቷል':'Logged out', 'info');
    renderProducts(filterList());
  } finally { hideSpinner(); }
}

function togglePasswordVisibility() {
  const inp = document.getElementById('loginPassword');
  const ico = document.getElementById('eyeIcon');
  inp.type = inp.type === 'password' ? 'text' : 'password';
  ico.className = `fa-solid fa-eye${inp.type==='password'?'':'-slash'}`;
}

// ── PRODUCT MODAL ─────────────────────────────────────────────────────────────
async function openProductModal(id = null) {
  document.getElementById('productForm').reset();
  document.getElementById('imagePath').value = '';
  document.getElementById('imagePreview').classList.add('hidden');
  document.getElementById('imagePreview').src = '';
  document.getElementById('imageUploadPlaceholder').style.display = 'flex';

  if (id) {
    const p = allProducts.find(x => x.id === id);
    if (!p) return;
    document.getElementById('productModalTitle').textContent = 'Edit Product';
    document.getElementById('productId').value   = p.id;
    document.getElementById('nameEn').value       = p.name_en;
    document.getElementById('nameAm').value       = p.name_am;
    document.getElementById('price').value        = p.price;
    document.getElementById('stock').value        = p.stock;
    document.getElementById('categoryEn').value   = p.category_en;
    document.getElementById('categoryAm').value   = p.category_am;
    document.getElementById('descEn').value       = p.desc_en;
    document.getElementById('descAm').value       = p.desc_am;
    document.getElementById('sellerEn').value     = p.seller_en;
    document.getElementById('sellerAm').value     = p.seller_am;
    document.getElementById('phone').value        = p.phone;
    document.getElementById('imagePath').value    = p.image_path;
    if (p.image_path) {
      document.getElementById('imagePreview').src = p.image_path;
      document.getElementById('imagePreview').classList.remove('hidden');
      document.getElementById('imageUploadPlaceholder').style.display = 'none';
    }
  } else {
    document.getElementById('productModalTitle').textContent = 'Add Product';
    document.getElementById('productId').value = '';
  }
  document.getElementById('productModal').classList.remove('hidden');
}
function closeProductModal() { document.getElementById('productModal').classList.add('hidden'); }

async function uploadImage(e) {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData(); fd.append('image', file);
  showSpinner();
  try {
    const res = await fetch('/api/upload-image', {method:'POST', body:fd});
    const data = await res.json();
    if (data.success) {
      document.getElementById('imagePath').value = data.image_path;
      const prev = document.getElementById('imagePreview');
      prev.src = data.image_path; prev.classList.remove('hidden');
      document.getElementById('imageUploadPlaceholder').style.display = 'none';
      showToast('Image uploaded', 'success');
    } else { showToast(data.message || 'Upload failed', 'error'); }
  } catch { showToast('Upload error', 'error'); }
  finally { hideSpinner(); }
}

async function saveProduct(e) {
  e.preventDefault();
  const id = document.getElementById('productId').value;
  const payload = {
    name_en: document.getElementById('nameEn').value,
    name_am: document.getElementById('nameAm').value,
    price: document.getElementById('price').value,
    stock: document.getElementById('stock').value,
    category_en: document.getElementById('categoryEn').value,
    category_am: document.getElementById('categoryAm').value,
    desc_en: document.getElementById('descEn').value,
    desc_am: document.getElementById('descAm').value,
    seller_en: document.getElementById('sellerEn').value,
    seller_am: document.getElementById('sellerAm').value,
    phone: document.getElementById('phone').value,
    image_path: document.getElementById('imagePath').value
  };
  showSpinner();
  try {
    const res = await fetch(id ? `/api/products/${id}` : '/api/products', {
      method: id ? 'PUT' : 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(id ? 'Product updated' : 'Product added', 'success');
      closeProductModal(); await loadProducts();
    } else { showToast(data.message || 'Failed', 'error'); }
  } catch { showToast('Error saving', 'error'); }
  finally { hideSpinner(); }
}

async function deleteProduct(id) {
  if (!confirm('Delete this product?')) return;
  showSpinner();
  try {
    const res = await fetch(`/api/products/${id}`, {method:'DELETE'});
    const data = await res.json();
    if (data.success) { showToast('Product deleted', 'success'); await loadProducts(); }
  } catch { showToast('Delete failed', 'error'); }
  finally { hideSpinner(); }
}

// ── HERO SLIDER ───────────────────────────────────────────────────────────────
function buildDots() {
  const slides = document.querySelectorAll('.hero-slide');
  const cnt = document.getElementById('slideDots');
  slides.forEach((_,i) => {
    const d = document.createElement('span');
    d.className = 'dot' + (i===0?' active':'');
    d.onclick = () => goToSlide(i);
    cnt.appendChild(d);
  });
  slideInterval = setInterval(() => changeSlide(1), 6000);
}

function changeSlide(dir) {
  const slides = document.querySelectorAll('.hero-slide');
  const dots   = document.querySelectorAll('.dot');
  slides[currentSlide].classList.remove('active');
  dots[currentSlide].classList.remove('active');
  currentSlide = (currentSlide + dir + slides.length) % slides.length;
  slides[currentSlide].classList.add('active');
  dots[currentSlide].classList.add('active');
  clearInterval(slideInterval);
  slideInterval = setInterval(() => changeSlide(1), 6000);
}

function initSlider() {} // Handled in buildDots

function goToSlide(i) {
  const slides = document.querySelectorAll('.hero-slide');
  const dots   = document.querySelectorAll('.dot');
  slides[currentSlide].classList.remove('active');
  dots[currentSlide].classList.remove('active');
  currentSlide = i;
  slides[currentSlide].classList.add('active');
  dots[currentSlide].classList.add('active');
  clearInterval(slideInterval);
  slideInterval = setInterval(() => changeSlide(1), 6000);
}

// ── UTILS ──────────────────────────────────────────────────────────────────────
function showSpinner() { document.getElementById('spinner').classList.remove('hidden'); }
function hideSpinner() { document.getElementById('spinner').classList.add('hidden'); }

function showToast(msg, type='info') {
  const icons = {success:'fa-circle-check', error:'fa-circle-xmark', info:'fa-circle-info'};
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fa-solid ${icons[type]}"></i> ${msg}`;
  document.getElementById('toast-container').appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

// Close modal on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay'))
    e.target.classList.add('hidden');
});

// Keyboard close
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    ['loginModal','productModal','detailModal'].forEach(id =>
      document.getElementById(id)?.classList.add('hidden')
    );
  }
});
