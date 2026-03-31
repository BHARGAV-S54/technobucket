import * as THREE from 'https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/three.module.min.js';
import { RoomEnvironment } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/environments/RoomEnvironment.js';

class Engine {
    constructor(options) {
        this.options = { ...options };
        this.size = { width: 0, height: 0, wWidth: 0, wHeight: 0, ratio: 0, pixelRatio: 0 };
        this.clock = new THREE.Clock();
        this.time = { elapsed: 0, delta: 0 };
        this.isPaused = false;
        this.init();
    }

    init() {
        this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
        this.scene = new THREE.Scene();
        this.canvas = document.getElementById(this.options.id);
        if (!this.canvas) return;

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            powerPreference: 'high-performance',
            antialias: true,
            alpha: true
        });
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        window.addEventListener('resize', () => this.resize());
        this.parent = this.canvas.parentNode;
        if (this.parent && 'ResizeObserver' in window) {
            this.resizeObserver = new ResizeObserver(() => this.resize());
            this.resizeObserver.observe(this.parent);
        }
        this.resize();
        this.start();
    }

    resize() {
        const parent = this.parent || this.canvas.parentNode;
        if (!parent) return;
        const rect = parent.getBoundingClientRect();
        const w = Math.max(1, Math.round(rect.width));
        const h = Math.max(1, Math.round(rect.height));
        this.size.width = w;
        this.size.height = h;
        this.size.ratio = w / h;
        this.camera.aspect = this.size.ratio;
        this.camera.updateProjectionMatrix();
        const fovRad = (this.camera.fov * Math.PI) / 180;
        this.size.wHeight = 2 * Math.tan(fovRad / 2) * this.camera.position.length();
        this.size.wWidth = this.size.wHeight * this.camera.aspect;
        this.renderer.setSize(w, h, false);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.canvas.style.width = `${w}px`;
        this.canvas.style.height = `${h}px`;
        if (this.onResize) this.onResize(this.size);
    }

    start() {
        const animate = () => {
            this.requestID = requestAnimationFrame(animate);
            if (this.isPaused) return;
            this.time.delta = Math.min(this.clock.getDelta(), 0.1);
            this.time.elapsed += this.time.delta;
            if (this.onUpdate) this.onUpdate(this.time);
            this.renderer.render(this.scene, this.camera);
        };
        animate();
    }
}

class Physics {
    constructor(config) {
        this.config = config;
        this.pos = new Float32Array(3 * config.count);
        this.vel = new Float32Array(3 * config.count);
        this.sizes = new Float32Array(config.count);
        this.center = new THREE.Vector3();
        this.init();
    }

    init() {
        for (let i = 0; i < this.config.count; i++) {
            const b = i * 3;
            this.pos[b] = (Math.random() - 0.5) * 10;
            this.pos[b + 1] = (Math.random() - 0.5) * 10;
            this.pos[b + 2] = (Math.random() - 0.5) * 4;
            this.vel[b] = (Math.random() - 0.5) * 0.1;
            this.vel[b + 1] = (Math.random() - 0.5) * 0.1;
            this.vel[b + 2] = (Math.random() - 0.5) * 0.1;
            this.sizes[i] = i === 0 ? this.config.size0 : (Math.random() * (this.config.maxSize - this.config.minSize) + this.config.minSize);
        }
    }

    update(t) {
        const c = this.config;
        if (c.controlSphere0) {
            const b0 = 0;
            this.vel[b0] = (this.center.x - this.pos[b0]) * 0.2;
            this.vel[b0 + 1] = (this.center.y - this.pos[b0 + 1]) * 0.2;
            this.vel[b0 + 2] = (this.center.z - this.pos[b0 + 2]) * 0.2;
        }

        for (let i = 0; i < c.count; i++) {
            const b = i * 3;
            if (i > 0 || !c.controlSphere0) {
                this.vel[b + 1] -= t.delta * c.gravity;
                this.vel[b] *= c.friction;
                this.vel[b + 1] *= c.friction;
                this.vel[b + 2] *= c.friction;
            }
            this.pos[b] += this.vel[b];
            this.pos[b + 1] += this.vel[b + 1];
            this.pos[b + 2] += this.vel[b + 2];

            const r = this.sizes[i];
            if (Math.abs(this.pos[b]) + r > c.maxX) {
                this.pos[b] = Math.sign(this.pos[b]) * (c.maxX - r);
                this.vel[b] *= -c.wallBounce;
            }
            if (Math.abs(this.pos[b + 1]) + r > c.maxY) {
                this.pos[b + 1] = Math.sign(this.pos[b + 1]) * (c.maxY - r);
                this.vel[b + 1] *= -c.wallBounce;
            }
            if (Math.abs(this.pos[b + 2]) + r > 5) {
                this.pos[b + 2] = Math.sign(this.pos[b + 2]) * (5 - r);
                this.vel[b + 2] *= -c.wallBounce;
            }
        }

        for (let i = 0; i < c.count; i++) {
            const b1 = i * 3;
            const r1 = this.sizes[i];
            for (let j = i + 1; j < c.count; j++) {
                const b2 = j * 3;
                const r2 = this.sizes[j];
                const dx = this.pos[b2] - this.pos[b1];
                const dy = this.pos[b2 + 1] - this.pos[b1 + 1];
                const dz = this.pos[b2 + 2] - this.pos[b1 + 2];
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                const min = r1 + r2;

                if (dist < min) {
                    const nx = dx / (dist || 1);
                    const ny = dy / (dist || 1);
                    const nz = dz / (dist || 1);
                    const overlap = (min - dist) / 2;
                    if (i !== 0 || !c.controlSphere0) {
                        this.pos[b1] -= nx * overlap;
                        this.pos[b1 + 1] -= ny * overlap;
                        this.pos[b1 + 2] -= nz * overlap;
                    }
                    this.pos[b2] += nx * overlap;
                    this.pos[b2 + 1] += ny * overlap;
                    this.pos[b2 + 2] += nz * overlap;

                    const rvx = this.vel[b2] - this.vel[b1];
                    const rvy = this.vel[b2 + 1] - this.vel[b1 + 1];
                    const rvz = this.vel[b2 + 2] - this.vel[b1 + 2];
                    const velAlongNormal = rvx * nx + rvy * ny + rvz * nz;
                    if (velAlongNormal > 0) continue;
                    const e = c.wallBounce;
                    let jImpulse = -(1 + e) * velAlongNormal;
                    jImpulse /= 2;
                    const ix = jImpulse * nx;
                    const iy = jImpulse * ny;
                    const iz = jImpulse * nz;

                    if (i !== 0 || !c.controlSphere0) {
                        this.vel[b1] -= ix;
                        this.vel[b1 + 1] -= iy;
                        this.vel[b1 + 2] -= iz;
                    }
                    this.vel[b2] += ix;
                    this.vel[b2 + 1] += iy;
                    this.vel[b2 + 2] += iz;
                }
            }
        }
    }
}

export function initBallpit() {
    const canvas = document.getElementById('ballpit-canvas');
    if (!canvas) return;

    const themeColors = [
        new THREE.Color('#22d3ee'), // primary-cyan
        new THREE.Color('#3b82f6'), // primary-blue
        new THREE.Color('#f59e0b'), // warning (orange)
        new THREE.Color('#ffffff')  // white
    ];

    const config = {
        count: 320,
        gravity: 0.06,
        friction: 0.992,
        wallBounce: 0.92,
        followCursor: false,
        minSize: 0.35,
        maxSize: 0.85,
        size0: 1.5,
        maxX: 5,
        maxY: 5,
        controlSphere0: false
    };

    const engine = new Engine({ id: 'ballpit-canvas' });
    if (!engine.canvas) return;

    engine.camera.position.z = 18;

    const pmrem = new THREE.PMREMGenerator(engine.renderer);
    const envMap = pmrem.fromScene(new RoomEnvironment()).texture;

    const geometry = new THREE.SphereGeometry(1, 24, 24);
    const material = new THREE.MeshPhysicalMaterial({
        envMap,
        metalness: 0.15,
        roughness: 0.15,
        clearcoat: 1.0,
        clearcoatRoughness: 0.05
    });

    const mesh = new THREE.InstancedMesh(geometry, material, config.count);
    for (let i = 0; i < config.count; i++) {
        const randomColor = themeColors[Math.floor(Math.random() * themeColors.length)];
        mesh.setColorAt(i, randomColor);
    }
    mesh.instanceColor.needsUpdate = true;
    engine.scene.add(mesh);

    const physics = new Physics(config);
    const dummy = new THREE.Object3D();

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-100, -100);
    const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
    const point = new THREE.Vector3();

    const handleMove = (e) => {
        const rect = engine.canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, engine.camera);
        raycaster.ray.intersectPlane(plane, point);
        physics.center.copy(point);
        config.controlSphere0 = true;
    };

    window.addEventListener('pointermove', handleMove);
    window.addEventListener('touchstart', handleMove);
    window.addEventListener('touchmove', handleMove);

    window.addEventListener('pointerleave', () => { config.controlSphere0 = false; });

    engine.onUpdate = (t) => {
        physics.update(t);
        for (let i = 0; i < config.count; i++) {
            const b = i * 3;
            dummy.position.set(physics.pos[b], physics.pos[b + 1], physics.pos[b + 2]);
            const s = (i === 0 && !config.controlSphere0) ? 0.0001 : physics.sizes[i];
            dummy.scale.setScalar(s);
            dummy.updateMatrix();
            mesh.setMatrixAt(i, dummy.matrix);
        }
        mesh.instanceMatrix.needsUpdate = true;
    };

    engine.onResize = (size) => {
        config.maxX = size.wWidth / 2;
        config.maxY = size.wHeight / 2;
    };

    engine.scene.add(new THREE.AmbientLight(0xffffff, 1.2));
    const spot1 = new THREE.SpotLight(0xffffff, 80);
    spot1.position.set(10, 15, 10);
    engine.scene.add(spot1);
}

// Auto-init if not imported
if (document.getElementById('ballpit-canvas')) {
    initBallpit();
}
