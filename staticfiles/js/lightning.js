// Lightning background for hero section (based on provided shader snippet)
(function () {
  const settings = {
    hue: 220, // cooler blue-purple to match site gradient
    xOffset: 0,
    speed: 0.85,
    intensity: 0.65,
    size: 0.9,
    dprCap: 1.5
  };

  const vertexShaderSource = `
    attribute vec2 aPosition;
    void main() {
      gl_Position = vec4(aPosition, 0.0, 1.0);
    }
  `;

  const fragmentShaderSource = `
    precision mediump float;
    uniform vec2 iResolution;
    uniform float iTime;
    uniform float uHue;
    uniform float uXOffset;
    uniform float uSpeed;
    uniform float uIntensity;
    uniform float uSize;
    
    #define OCTAVE_COUNT 10

    vec3 hsv2rgb(vec3 c) {
        vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0,4.0,2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
        return c.z * mix(vec3(1.0), rgb, c.y);
    }

    float hash11(float p) {
        p = fract(p * .1031);
        p *= p + 33.33;
        p *= p + p;
        return fract(p);
    }

    float hash12(vec2 p) {
        vec3 p3 = fract(vec3(p.xyx) * .1031);
        p3 += dot(p3, p3.yzx + 33.33);
        return fract((p3.x + p3.y) * p3.z);
    }

    mat2 rotate2d(float theta) {
        float c = cos(theta);
        float s = sin(theta);
        return mat2(c, -s, s, c);
    }

    float noise(vec2 p) {
        vec2 ip = floor(p);
        vec2 fp = fract(p);
        float a = hash12(ip);
        float b = hash12(ip + vec2(1.0, 0.0));
        float c = hash12(ip + vec2(0.0, 1.0));
        float d = hash12(ip + vec2(1.0, 1.0));
        
        vec2 t = smoothstep(0.0, 1.0, fp);
        return mix(mix(a, b, t.x), mix(c, d, t.x), t.y);
    }

    float fbm(vec2 p) {
        float value = 0.0;
        float amplitude = 0.5;
        for (int i = 0; i < OCTAVE_COUNT; ++i) {
            value += amplitude * noise(p);
            p *= rotate2d(0.45);
            p *= 2.0;
            amplitude *= 0.5;
        }
        return value;
    }

    void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
        vec2 uv = fragCoord / iResolution.xy;
        uv = 2.0 * uv - 1.0;
        uv.x *= iResolution.x / iResolution.y;
        uv.x += uXOffset;
        
        uv += 2.0 * fbm(uv * uSize + 0.8 * iTime * uSpeed) - 1.0;
        
        float dist = abs(uv.x) + 0.02;
        vec3 baseColor = hsv2rgb(vec3(uHue / 360.0, 0.7, 0.9));
        vec3 col = baseColor * pow(mix(0.0, 0.08, hash11(iTime * uSpeed)) / dist, 1.0) * uIntensity;
        col = pow(col, vec3(1.0));
        fragColor = vec4(col, 1.0);
    }

    void main() {
        mainImage(gl_FragColor, gl_FragCoord.xy);
    }
  `;

  function compile(gl, source, type) {
    const shader = gl.createShader(type);
    if (!shader) return null;
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error('Lightning shader compile error:', gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  function init(container) {
    if (!container) return;
    // ensure the host fills the hero
    container.style.position = 'absolute';
    container.style.inset = '0';
    container.style.pointerEvents = 'none';

    const canvas = document.createElement('canvas');
    canvas.className = 'lightning-canvas';
    Object.assign(canvas.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      display: 'block'
    });

    const gl = canvas.getContext('webgl', { antialias: false, preserveDrawingBuffer: false });
    if (!gl) {
      console.error('WebGL not supported for lightning');
      container.classList.add('hero-lightning-fallback');
      return;
    }

    container.appendChild(canvas);
    container.classList.remove('hero-lightning-fallback');

    const resizeCanvas = () => {
      const host = container.getBoundingClientRect();
      const rect = (host.width > 2 && host.height > 2) ? host : (container.parentElement || container).getBoundingClientRect();
      const w = rect.width || window.innerWidth;
      const h = rect.height || window.innerHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, settings.dprCap);
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      return { dpr };
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const vs = compile(gl, vertexShaderSource, gl.VERTEX_SHADER);
    const fs = compile(gl, fragmentShaderSource, gl.FRAGMENT_SHADER);
    if (!vs || !fs) {
      container.classList.add('hero-lightning-fallback');
      container.contains(canvas) && container.removeChild(canvas);
      return;
    }

    const program = gl.createProgram();
    if (!program) {
      container.classList.add('hero-lightning-fallback');
      container.contains(canvas) && container.removeChild(canvas);
      return;
    }
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Lightning program link error:', gl.getProgramInfoLog(program));
      container.classList.add('hero-lightning-fallback');
      container.contains(canvas) && container.removeChild(canvas);
      return;
    }
    gl.useProgram(program);

    const vertices = new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]);
    const vertexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const aPosition = gl.getAttribLocation(program, 'aPosition');
    gl.enableVertexAttribArray(aPosition);
    gl.vertexAttribPointer(aPosition, 2, gl.FLOAT, false, 0, 0);

    const iResolutionLocation = gl.getUniformLocation(program, 'iResolution');
    const iTimeLocation = gl.getUniformLocation(program, 'iTime');
    const uHueLocation = gl.getUniformLocation(program, 'uHue');
    const uXOffsetLocation = gl.getUniformLocation(program, 'uXOffset');
    const uSpeedLocation = gl.getUniformLocation(program, 'uSpeed');
    const uIntensityLocation = gl.getUniformLocation(program, 'uIntensity');
    const uSizeLocation = gl.getUniformLocation(program, 'uSize');

    const startTime = performance.now();
    let frame;

    const render = () => {
      frame = requestAnimationFrame(render);
      const rect = (container.getBoundingClientRect().width > 2 && container.getBoundingClientRect().height > 2)
        ? container.getBoundingClientRect()
        : (container.parentElement || container).getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, settings.dprCap);
      const w = (rect.width || window.innerWidth) * dpr;
      const h = (rect.height || window.innerHeight) * dpr;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
        canvas.style.width = (rect.width || window.innerWidth) + 'px';
        canvas.style.height = (rect.height || window.innerHeight) + 'px';
      }
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(iResolutionLocation, canvas.width, canvas.height);
      const currentTime = performance.now();
      gl.uniform1f(iTimeLocation, (currentTime - startTime) / 1000.0);
      gl.uniform1f(uHueLocation, settings.hue);
      gl.uniform1f(uXOffsetLocation, settings.xOffset);
      gl.uniform1f(uSpeedLocation, settings.speed);
      gl.uniform1f(uIntensityLocation, settings.intensity);
      gl.uniform1f(uSizeLocation, settings.size);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    };
    render();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resizeCanvas);
      gl.getExtension('WEBGL_lose_context')?.loseContext();
      container.removeChild(canvas);
    };
  }

  function mount() {
    const container = document.getElementById('hero-lightning');
    if (!container) return;
    init(container);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
