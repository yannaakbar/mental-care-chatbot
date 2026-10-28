(function () {
  'use strict';

  // ===== PRELOADER =====
  window.addEventListener('load', function () {
    const preloader = document.getElementById('preloader');
    if (preloader) {
      preloader.classList.add('loaded');
      setTimeout(() => preloader.remove(), 300);
    }
  });

  // ===== BACK TO TOP =====
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 100) {
        backToTop.classList.add('active');
      } else {
        backToTop.classList.remove('active');
      }
    });

    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ===== MOBILE NAV TOGGLE =====
  const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
  const navbar          = document.querySelector('#navbar');

  if (mobileNavToggle) {
    mobileNavToggle.addEventListener('click', function () {
      navbar.classList.toggle('navbar-mobile');
      this.classList.toggle('bi-list');
      this.classList.toggle('bi-x');
    });
  }

  // ===== SMOOTH SCROLL =====
  document.querySelectorAll('.scrollto').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();

        // Tutup mobile nav jika terbuka
        if (navbar.classList.contains('navbar-mobile')) {
          navbar.classList.remove('navbar-mobile');
          mobileNavToggle.classList.toggle('bi-list');
          mobileNavToggle.classList.toggle('bi-x');
        }

        const headerHeight = document.getElementById('header').offsetHeight;
        const targetPos    = target.offsetTop - headerHeight - 10;

        window.scrollTo({ top: targetPos, behavior: 'smooth' });
      }
    });
  });

  // ===== ACTIVE NAV ON SCROLL =====
  function navbarLinksActive() {
    const scrollY      = window.scrollY;
    const headerHeight = document.getElementById('header')?.offsetHeight || 70;

    document.querySelectorAll('.scrollto').forEach(function (el) {
      const sectionId = el.getAttribute('href');
      if (!sectionId.startsWith('#')) return;

      const section = document.querySelector(sectionId);
      if (!section) return;

      const sectionTop    = section.offsetTop - headerHeight - 20;
      const sectionBottom = sectionTop + section.offsetHeight;

      if (scrollY >= sectionTop && scrollY < sectionBottom) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });
  }

  window.addEventListener('scroll', navbarLinksActive);
  navbarLinksActive();

  // ===== HEADER SCROLL EFFECT =====
  const header = document.getElementById('header');
  if (header) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 50) {
        header.style.padding = '10px 0';
        header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.2)';
      } else {
        header.style.padding = '15px 0';
        header.style.boxShadow = '0 2px 15px rgba(0,0,0,0.1)';
      }
    });
  }

  // ===== AOS ANIMATION =====
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration : 800,
      easing   : 'ease-in-out',
      once     : true,
      mirror   : false,
    });
  }

})();