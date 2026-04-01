// Main JavaScript for Techno Bucket

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Animated logo and brand accent
    const logoImg = document.querySelector('.logo-img');
    if (logoImg) {
        logoImg.classList.add('animated-logo');
    }

    const brandText = document.querySelector('.navbar-brand span');
    if (brandText) {
        brandText.classList.add('text-gradient-shimmer');
    }

    // Refresh electric borders when the page is visible to ensure active effects after back tab
    const electricCards = document.querySelectorAll('.js-electric-border');
    const ensureElectric = () => {
        electricCards.forEach(card => {
            if (!card.closest('.electric-border')) {
                // Re-trigger by removing and re-adding class for style update
                card.classList.remove('js-electric-border');
                void card.offsetWidth;
                card.classList.add('js-electric-border');
            }
        });
    };
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') ensureElectric();
    });

    // Hero to offers minimal built-in animation: subtle hue shift
    const heroSection = document.querySelector('.home-hero-section');
    if (heroSection) {
        let angle = 0;
        let pageVisible = true;
        let heroRaf;
        const heroAnimation = () => {
            heroRaf = requestAnimationFrame(heroAnimation);
            if (!pageVisible) return;
            angle += 0.01;
            heroSection.style.background = `radial-gradient(circle at 45% 35%, rgba(34, 211, 238, 0.18) ${45 + Math.sin(angle) * 3}%, rgba(168, 85, 247, 0.09) ${60 + Math.cos(angle) * 3}%, #05070f 100%)`;
        };
        heroRaf = requestAnimationFrame(heroAnimation);
        document.addEventListener('visibilitychange', () => {
            pageVisible = document.visibilityState === 'visible';
        });
    }

    // Fallback for aurora/lightning if module script can't run
    const auraContainer = document.getElementById('aurora-container');
    const heroLightning = document.getElementById('hero-lightning');
    if (auraContainer && auraContainer.children.length === 0) {
        auraContainer.classList.add('soft-aurora-fallback');
    }
    if (heroLightning && heroLightning.children.length === 0) {
        heroLightning.classList.add('hero-lightning-fallback');
    }
});

// Generic utility that triggers once when whole document loads
window.addEventListener('load', () => {
    const offers = document.querySelectorAll('.home-offer-card');
    offers.forEach((card, index) => {
        card.style.transitionDelay = `${index * 120}ms`;
    });
});
