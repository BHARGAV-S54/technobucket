document.addEventListener('DOMContentLoaded', function () {
    const giftBox = document.getElementById('giftBox');
    const comboPackCard = document.getElementById('comboPackCard');
    const ballPitBg = document.getElementById('ballPitBg');
    const confettiContainer = document.getElementById('confettiContainer');

    if (giftBox && comboPackCard) {
        giftBox.addEventListener('click', function () {
            if (giftBox.classList.contains('open')) return;

            giftBox.classList.add('open');
            launchConfetti();

            setTimeout(() => {
                comboPackCard.classList.add('visible');
                if (ballPitBg) {
                    ballPitBg.classList.add('visible');
                }
                // Ballpit initializes while hidden; force resize after reveal so
                // canvas and background dimensions stay in sync.
                window.dispatchEvent(new Event('resize'));
                setTimeout(() => window.dispatchEvent(new Event('resize')), 220);
                comboPackCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    }

    function launchConfetti() {
        const colors = ['#fbbf24', '#f59e0b', '#22d3ee', '#34d399', '#f87171', '#a855f7'];

        for (let i = 0; i < 40; i++) {
            const piece = document.createElement('div');
            piece.style.cssText = `
                position: absolute;
                width: ${8 + Math.random() * 10}px;
                height: ${8 + Math.random() * 10}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
                opacity: 0;
            `;

            const angle = (Math.random() * 360) * (Math.PI / 180);
            const distance = 80 + Math.random() * 120;
            const tx = Math.cos(angle) * distance + 'px';
            const ty = Math.sin(angle) * distance + 'px';

            piece.style.setProperty('--tx', tx);
            piece.style.setProperty('--ty', ty);
            piece.style.animation = `confetti-fly 1s ease-out forwards`;

            confettiContainer.appendChild(piece);
            setTimeout(() => piece.remove(), 1500);
        }
    }
});
