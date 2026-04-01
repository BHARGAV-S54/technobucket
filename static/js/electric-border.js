// Vanilla JS implementation inspired by reactbits.dev ElectricBorder

document.addEventListener('DOMContentLoaded', function () {
    const targets = document.querySelectorAll('.js-electric-border');
    if (!targets.length) return;

    targets.forEach(function (card) {
        createElectricBorder(card);
    });
});

function createElectricBorder(cardElement, options) {
    const opts = Object.assign(
        {
            color: '#5227FF',
            speed: 1,
            chaos: 0.12,
            borderRadius: 24
        },
        options || {}
    );

    const parent = cardElement.parentElement;
    if (!parent) return;

    // Build wrapper structure: electric-border > canvas, layers, content
    const wrapper = document.createElement('div');
    wrapper.className = 'electric-border';
    wrapper.style.borderRadius = (opts.borderRadius || 24) + 'px';
    wrapper.style.setProperty('--electric-border-color', opts.color);

    const canvasContainer = document.createElement('div');
    canvasContainer.className = 'eb-canvas-container';
    const canvas = document.createElement('canvas');
    canvas.className = 'eb-canvas';
    canvasContainer.appendChild(canvas);

    const layers = document.createElement('div');
    layers.className = 'eb-layers';
    const glow1 = document.createElement('div');
    glow1.className = 'eb-glow-1';
    const glow2 = document.createElement('div');
    glow2.className = 'eb-glow-2';
    const bgGlow = document.createElement('div');
    bgGlow.className = 'eb-background-glow';
    layers.appendChild(glow1);
    layers.appendChild(glow2);
    layers.appendChild(bgGlow);

    const content = document.createElement('div');
    content.className = 'eb-content';
    content.appendChild(cardElement);

    wrapper.appendChild(canvasContainer);
    wrapper.appendChild(layers);
    wrapper.appendChild(content);

    parent.appendChild(wrapper);

    // Core drawing logic adapted from React version
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let time = 0;
    let lastFrameTime = performance.now();

    const noiseRandom = function (x) {
        return (Math.sin(x * 12.9898) * 43758.5453) % 1;
    };

    const noise2D = function (x, y) {
        const i = Math.floor(x);
        const j = Math.floor(y);
        const fx = x - i;
        const fy = y - j;

        const a = noiseRandom(i + j * 57);
        const b = noiseRandom(i + 1 + j * 57);
        const c = noiseRandom(i + (j + 1) * 57);
        const d = noiseRandom(i + 1 + (j + 1) * 57);

        const ux = fx * fx * (3.0 - 2.0 * fx);
        const uy = fy * fy * (3.0 - 2.0 * fy);

        return (
            a * (1 - ux) * (1 - uy) +
            b * ux * (1 - uy) +
            c * (1 - ux) * uy +
            d * ux * uy
        );
    };

    const octavedNoise = function (
        x,
        octaves,
        lacunarity,
        gain,
        baseAmplitude,
        baseFrequency,
        time,
        seed,
        baseFlatness
    ) {
        let y = 0;
        let amplitude = baseAmplitude;
        let frequency = baseFrequency;

        for (let i = 0; i < octaves; i++) {
            let octaveAmplitude = amplitude;
            if (i === 0) {
                octaveAmplitude *= baseFlatness;
            }
            y +=
                octaveAmplitude *
                noise2D(frequency * x + seed * 100, time * frequency * 0.3);
            frequency *= lacunarity;
            amplitude *= gain;
        }

        return y;
    };

    const getCornerPoint = function (
        centerX,
        centerY,
        radius,
        startAngle,
        arcLength,
        progress
    ) {
        const angle = startAngle + progress * arcLength;
        return {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        };
    };

    const getRoundedRectPoint = function (
        t,
        left,
        top,
        width,
        height,
        radius
    ) {
        const straightWidth = width - 2 * radius;
        const straightHeight = height - 2 * radius;
        const cornerArc = (Math.PI * radius) / 2;
        const totalPerimeter =
            2 * straightWidth + 2 * straightHeight + 4 * cornerArc;
        const distance = t * totalPerimeter;

        let accumulated = 0;

        if (distance <= accumulated + straightWidth) {
            const progress = (distance - accumulated) / straightWidth;
            return { x: left + radius + progress * straightWidth, y: top };
        }
        accumulated += straightWidth;

        if (distance <= accumulated + cornerArc) {
            const progress = (distance - accumulated) / cornerArc;
            return getCornerPoint(
                left + width - radius,
                top + radius,
                radius,
                -Math.PI / 2,
                Math.PI / 2,
                progress
            );
        }
        accumulated += cornerArc;

        if (distance <= accumulated + straightHeight) {
            const progress = (distance - accumulated) / straightHeight;
            return {
                x: left + width,
                y: top + radius + progress * straightHeight
            };
        }
        accumulated += straightHeight;

        if (distance <= accumulated + cornerArc) {
            const progress = (distance - accumulated) / cornerArc;
            return getCornerPoint(
                left + width - radius,
                top + height - radius,
                radius,
                0,
                Math.PI / 2,
                progress
            );
        }
        accumulated += cornerArc;

        if (distance <= accumulated + straightWidth) {
            const progress = (distance - accumulated) / straightWidth;
            return {
                x: left + width - radius - progress * straightWidth,
                y: top + height
            };
        }
        accumulated += straightWidth;

        if (distance <= accumulated + cornerArc) {
            const progress = (distance - accumulated) / cornerArc;
            return getCornerPoint(
                left + radius,
                top + height - radius,
                radius,
                Math.PI / 2,
                Math.PI / 2,
                progress
            );
        }
        accumulated += cornerArc;

        if (distance <= accumulated + straightHeight) {
            const progress = (distance - accumulated) / straightHeight;
            return {
                x: left,
                y: top + height - radius - progress * straightHeight
            };
        }
        accumulated += straightHeight;

        const progress = (distance - accumulated) / cornerArc;
        return getCornerPoint(
            left + radius,
            top + radius,
            radius,
            Math.PI,
            Math.PI / 2,
            progress
        );
    };

    if (cardElement.classList.contains('eb-initialized')) return;
    cardElement.classList.add('eb-initialized');

    const chaos = opts.chaos;
    const speed = opts.speed;
    const borderRadius = opts.borderRadius;

    const octaves = 10;
    const lacunarity = 1.6;
    const gain = 0.7;
    const amplitude = chaos;
    const frequency = 10;
    const baseFlatness = 0;
    const displacement = 20;
    const borderOffset = 20;

    function updateSize() {
        const rect = cardElement.getBoundingClientRect();
        const width = rect.width + borderOffset * 2;
        const height = rect.height + borderOffset * 2;

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        return { width, height, dpr };
    }

    let size = updateSize();

    function draw(currentTime) {
        const deltaTime = (currentTime - lastFrameTime) / 1000;
        time += deltaTime * speed;
        lastFrameTime = currentTime;

        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.setTransform(size.dpr, 0, 0, size.dpr, 0, 0);

        ctx.strokeStyle = opts.color;
        ctx.lineWidth = 1.2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        const scale = displacement;
        const left = borderOffset;
        const top = borderOffset;
        const borderWidth = size.width - 2 * borderOffset;
        const borderHeight = size.height - 2 * borderOffset;
        const maxRadius = Math.min(borderWidth, borderHeight) / 2;
        const radius = Math.min(borderRadius, maxRadius);

        const approximatePerimeter =
            2 * (borderWidth + borderHeight) + 2 * Math.PI * radius;
        const sampleCount = Math.floor(approximatePerimeter / 2);

        ctx.beginPath();

        for (let i = 0; i <= sampleCount; i++) {
            const progress = i / sampleCount;
            const point = getRoundedRectPoint(
                progress,
                left,
                top,
                borderWidth,
                borderHeight,
                radius
            );

            const xNoise = octavedNoise(
                progress * 8,
                octaves,
                lacunarity,
                gain,
                amplitude,
                frequency,
                time,
                0,
                baseFlatness
            );

            const yNoise = octavedNoise(
                progress * 8,
                octaves,
                lacunarity,
                gain,
                amplitude,
                frequency,
                time,
                1,
                baseFlatness
            );

            const displacedX = point.x + xNoise * scale;
            const displacedY = point.y + yNoise * scale;

            if (i === 0) {
                ctx.moveTo(displacedX, displacedY);
            } else {
                ctx.lineTo(displacedX, displacedY);
            }
        }

        ctx.closePath();
        ctx.stroke();

        requestAnimationFrame(draw);
    }

    const resizeObserver = new ResizeObserver(function () {
        size = updateSize();
    });
    resizeObserver.observe(cardElement);

    requestAnimationFrame(draw);
}

