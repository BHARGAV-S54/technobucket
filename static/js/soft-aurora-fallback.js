// Fallback aurora animation for environments where ES6 modules fail (like Vercel)
(function() {
    'use strict';

    function initFallbackAurora() {
        const container = document.getElementById('aurora-container') || document.getElementById('soft-aurora-container');
        if (!container) return;

        // Only apply fallback if no WebGL canvas exists
        if (container.querySelector('canvas')) return;

        container.classList.add('soft-aurora-fallback');
        container.style.position = container.style.position || 'absolute';
        container.style.inset = '0';
        container.style.zIndex = '0';
        container.style.pointerEvents = 'none';

        // Add subtle animation to the fallback
        let hue = 0;
        const animate = () => {
            hue += 0.5;
            const color1 = `hsl(${200 + Math.sin(hue * 0.01) * 20}, 70%, 60%)`;
            const color2 = `hsl(${280 + Math.cos(hue * 0.01) * 20}, 70%, 50%)`;
            container.style.background = `
                radial-gradient(120% 60% at 30% 50%, ${color1} 0.4, transparent 55%),
                radial-gradient(110% 55% at 70% 50%, ${color2} 0.4, transparent 60%),
                linear-gradient(180deg, rgba(5, 8, 20, 0.82), rgba(5, 8, 20, 0.94))
            `;
            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFallbackAurora);
    } else {
        initFallbackAurora();
    }

    // Also try after a delay in case modules load slowly
    setTimeout(initFallbackAurora, 1000);
})();