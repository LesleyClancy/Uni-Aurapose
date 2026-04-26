const canvas = document.getElementById("prismCanvas");
const ctx = canvas.getContext("2d");
const body = document.body;

let width = 0;
let height = 0;
let pointerX = 0.64;
let pointerY = 0.42;
let time = 0;
const parallaxNodes = document.querySelectorAll("[data-parallax]");

const colors = [
  "rgba(114, 247, 255, ",
  "rgba(48, 108, 255, ",
  "rgba(255, 92, 214, ",
  "rgba(178, 44, 255, ",
  "rgba(255, 255, 255, ",
];

function initIntro() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion) {
    body.classList.remove("intro-active");
    body.classList.add("intro-complete");
    return;
  }

  window.setTimeout(() => {
    body.classList.remove("intro-active");
    body.classList.add("intro-complete");
  }, 1880);
}

function resize() {
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function drawPrism(cx, cy, radius) {
  const sides = 5;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(time * 0.08);
  ctx.beginPath();

  for (let i = 0; i < sides; i += 1) {
    const angle = -Math.PI / 2 + (i * Math.PI * 2) / sides;
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }

  ctx.closePath();
  const grad = ctx.createLinearGradient(-radius, -radius, radius, radius);
  grad.addColorStop(0, "rgba(255,255,255,0.5)");
  grad.addColorStop(0.28, "rgba(114,247,255,0.18)");
  grad.addColorStop(0.58, "rgba(255,92,214,0.11)");
  grad.addColorStop(1, "rgba(255,255,255,0.03)");
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.lineWidth = 1;
  ctx.strokeStyle = "rgba(230, 252, 255, 0.5)";
  ctx.stroke();

  for (let i = 0; i < sides; i += 1) {
    const angle = -Math.PI / 2 + (i * Math.PI * 2) / sides;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
    ctx.strokeStyle = `rgba(230, 252, 255, ${0.12 + i * 0.025})`;
    ctx.stroke();
  }

  ctx.restore();
}

function drawBeam(cx, cy, angle, length, color, alpha) {
  const x = Math.cos(angle) * length;
  const y = Math.sin(angle) * length;
  const grad = ctx.createLinearGradient(cx - x * 0.18, cy - y * 0.18, cx + x, cy + y);
  grad.addColorStop(0, `${color}0)`);
  grad.addColorStop(0.18, `${color}${alpha})`);
  grad.addColorStop(0.7, `${color}${alpha * 0.42})`);
  grad.addColorStop(1, `${color}0)`);

  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  ctx.lineWidth = 1.4;
  ctx.strokeStyle = grad;
  ctx.beginPath();
  ctx.moveTo(cx - x * 0.2, cy - y * 0.2);
  ctx.lineTo(cx + x, cy + y);
  ctx.stroke();
  ctx.restore();
}

function updateParallaxMotion() {
  const offsetX = (pointerX - 0.5) * 26;
  const offsetY = (pointerY - 0.5) * 18;

  parallaxNodes.forEach((node, index) => {
    const driftX = Math.sin(time * 1.8 + index * 1.3) * (6 + index * 1.2);
    const driftY = Math.cos(time * 1.35 + index * 0.9) * (4 + index);
    node.style.setProperty("--parallax-x", `${(offsetX * (0.3 + index * 0.08) + driftX).toFixed(2)}px`);
    node.style.setProperty("--parallax-y", `${(offsetY * (0.26 + index * 0.06) + driftY).toFixed(2)}px`);
  });
}

function animate() {
  time += 0.008;
  ctx.clearRect(0, 0, width, height);

  const cx = width * (0.62 + (pointerX - 0.5) * 0.08);
  const cy = height * (0.42 + (pointerY - 0.5) * 0.08);
  const radius = Math.min(width, height) * 0.22;

  const bg = ctx.createRadialGradient(cx, cy, radius * 0.05, cx, cy, radius * 3);
  bg.addColorStop(0, "rgba(114, 247, 255, 0.18)");
  bg.addColorStop(0.32, "rgba(255, 92, 214, 0.09)");
  bg.addColorStop(1, "rgba(3, 5, 9, 0)");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);

  for (let i = 0; i < 18; i += 1) {
    const drift = Math.sin(time * 2 + i) * 0.12;
    const angle = -0.62 + i * 0.075 + drift;
    drawBeam(cx - radius * 0.3, cy, angle, width * 0.68, colors[i % colors.length], 0.22);
  }

  drawPrism(cx, cy, radius);

  for (let i = 0; i < 36; i += 1) {
    const x = (Math.sin(i * 45.7 + time * 26) * 0.5 + 0.5) * width;
    const y = (Math.cos(i * 32.1 + time * 20) * 0.5 + 0.5) * height;
    ctx.fillStyle = `rgba(230, 252, 255, ${0.03 + (i % 4) * 0.014})`;
    ctx.fillRect(x, y, 1.2, 1.2);
  }

  updateParallaxMotion();
  requestAnimationFrame(animate);
}

window.addEventListener("resize", resize);
window.addEventListener("pointermove", (event) => {
  pointerX = event.clientX / window.innerWidth;
  pointerY = event.clientY / window.innerHeight;
});

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.animate(
        [
          { opacity: 0, transform: "translateY(28px)" },
          { opacity: 1, transform: "translateY(0)" },
        ],
        {
          duration: 700,
          easing: "cubic-bezier(.2,.9,.2,1)",
          fill: "forwards",
        },
      );
      observer.unobserve(entry.target);
    });
  },
  { threshold: 0.18 },
);

document.querySelectorAll("section:not(.hero) h2, .spectrum-lanes article, .signal-copy p").forEach((node) => {
  node.style.opacity = 0;
  observer.observe(node);
});

resize();
updateParallaxMotion();
initIntro();
animate();
