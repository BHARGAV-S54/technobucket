// Fallback lightning animation for environments where ES6 modules fail (like Vercel)
(function() {
    'use strict';

    function initFallbackLightning() {
        const container = document.getElementById('hero-lightning');
        if (!container) return;

        // Only apply fallback if no WebGL canvas exists
        if (container.querySelector('canvas')) return;

        container.classList.add('hero-lightning-fallback');

        // Add subtle lightning-like animation
        let intensity = 0;
        let direction = 1;
        const animate = () => {
            intensity += direction * 0.02;
            if (intensity > 1) direction = -1;
            if (intensity < 0) direction = 1;

            const opacity = 0.3 + intensity * 0.4;
            const blur = 20 + intensity * 10;

            container.style.background = `
                radial-gradient(140% 140% at 50% 40%,
                    rgba(79, 70, 229, ${opacity}),
                    rgba(5, 7, 15, 0.95)
                )
            `;
            container.style.filter = `blur(${blur}px)`;

            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFallbackLightning);
    } else {
        initFallbackLightning();
    }

    // Also try after a delay in case modules load slowly
    setTimeout(initFallbackLightning, 1000);
})();