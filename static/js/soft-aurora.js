// Soft Aurora background animation — pure WebGL, no external dependencies
// Replaces the OGL-based version to work reliably on Vercel without CDN imports.

(function () {
  const config = {
    speed: 0.5,
    scale: 1.8,
    brightness: 1.1,
    color1: [0.133, 0.827, 0.933], // #22d3ee cyan
    color2: [0.659, 0.333, 0.969], // #a855f7 purple
  };

  const vertexSource = `
    attribute vec2 aPosition;
    varying vec2 vUv;
    void main() {
      vUv = aPosition * 0.5 + 0.5;
      gl_Position = vec4(aPosition, 0.0, 1.0);
    }
  `;

  const fragmentSource = `
    precision mediump float;
    varying vec2 vUv;
    uniform float uTime;
    uniform vec2 uResolution;
    uniform vec3 uColor1;
    uniform vec3 uColor2;
    uniform float uSpeed;
    uniform float uScale;
    uniform float uBrightness;

    float hash(vec2 p) {
      p = fract(p * vec2(234.34, 435.345));
      p += dot(p, p + 34.23);
      return fract(p.x * p.y);
    }

    float noise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      float a = hash(i);
      float b = hash(i + vec2(1.0, 0.0));
      float c = hash(i + vec2(0.0, 1.0));
      float d = hash(i + vec2(1.0, 1.0));
      return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    }

    float fbm(vec2 p) {
      float v = 0.0;
      float a = 0.5;
      for (int i = 0; i < 5; i++) {
        v += a * noise(p);
        p *= 2.0;
        a *= 0.5;
      }
      return v;
    }

    void main() {
      vec2 uv = vUv;
      float t = uTime * uSpeed;

      // Two layered aurora bands
      float n1 = fbm(uv * uScale + vec2(t * 0.3, t * 0.1));
      float n2 = fbm(uv * uScale * 1.4 + vec2(-t * 0.2, t * 0.15));

      float band1 = exp(-8.0 * abs(uv.y - 0.35 - n1 * 0.35));
      float band2 = exp(-10.0 * abs(uv.y - 0.55 - n2 * 0.25));

      vec3 col = band1 * uColor1 + band2 * uColor2;
      col *= uBrightness;

      float alpha = clamp(band1 + band2, 0.0, 0.75);
      gl_FragColor = vec4(col, alpha);
    }
  `;

  function compileShader(gl, source, type) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error('Aurora shader error:', gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  function initAurora(container) {
    if (!container) return;

    const canvas = document.createElement('canvas');
    Object.assign(canvas.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
    });
    container.appendChild(canvas);

    const gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: false });
    if (!gl) {
      container.classList.add('soft-aurora-fallback');
      return;
    }

    const vs = compileShader(gl, vertexSource, gl.VERTEX_SHADER);
    const fs = compileShader(gl, fragmentSource, gl.FRAGMENT_SHADER);
    if (!vs || !fs) return;

    const program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Aurora program error:', gl.getProgramInfoLog(program));
      return;
    }
    gl.useProgram(program);

    const vertices = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const aPosLoc = gl.getAttribLocation(program, 'aPosition');
    gl.enableVertexAttribArray(aPosLoc);
    gl.vertexAttribPointer(aPosLoc, 2, gl.FLOAT, false, 0, 0);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    const uTime = gl.getUniformLocation(program, 'uTime');
    const uRes = gl.getUniformLocation(program, 'uResolution');
    const uColor1 = gl.getUniformLocation(program, 'uColor1');
    const uColor2 = gl.getUniformLocation(program, 'uColor2');
    const uSpeed = gl.getUniformLocation(program, 'uSpeed');
    const uScale = gl.getUniformLocation(program, 'uScale');
    const uBrightness = gl.getUniformLocation(program, 'uBrightness');

    gl.uniform3fv(uColor1, config.color1);
    gl.uniform3fv(uColor2, config.color2);
    gl.uniform1f(uSpeed, config.speed);
    gl.uniform1f(uScale, config.scale);
    gl.uniform1f(uBrightness, config.brightness);

    function resize() {
      const rect = container.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
    }
    resize();
    window.addEventListener('resize', resize);

    const startTime = performance.now();
    let raf;
    function render() {
      raf = requestAnimationFrame(render);
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.uniform1f(uTime, (performance.now() - startTime) / 1000.0);
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    render();

    return function destroy() {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
      gl.getExtension('WEBGL_lose_context')?.loseContext();
      if (container.contains(canvas)) container.removeChild(canvas);
    };
  }

  function mount() {
    const container =
      document.getElementById('aurora-container') ||
      document.getElementById('soft-aurora-container');
    if (!container) return;
    initAurora(container);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
