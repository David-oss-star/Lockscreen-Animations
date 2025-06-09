const canvas = document.getElementById("animCanvas");
const ctx = canvas.getContext("2d");

const animationTypeSelect = document.getElementById("animationType");
let animationType = animationTypeSelect.value;

// Set on change
animationTypeSelect.addEventListener("change", () => {
  animationType = animationTypeSelect.value;
  startAnimation(); // Restart animation
});

let animationFrameId; // for canceling

import animationRegistry from './animationRegistry.js';

function startAnimation() {
  if (animationFrameId) cancelAnimationFrame(animationFrameId);

  const animator = animationRegistry[animationType];
  if (!animator) return;

  const drawFn = animator(ctx, canvas);
  function loop() {
    drawFn();
    animationFrameId = requestAnimationFrame(loop);
  }
  loop();
}


function animateClock() {
  function drawClock() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const now = new Date();

    // Background
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Time
    ctx.fillStyle = "white";
    ctx.font = "32px monospace";
    ctx.textAlign = "center";
    ctx.fillText(now.toLocaleTimeString(), canvas.width / 2, canvas.height / 2);

    animationFrameId = requestAnimationFrame(drawClock);
  }

  drawClock();
}

function animateBouncingText() {
  const text = "Hello!";
  const fontSize = 30;
  let posX = 0;
  let direction = 2;

  ctx.font = `${fontSize}px sans-serif`;
  ctx.textAlign = "left";
  const textWidth = ctx.measureText(text).width;

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Background
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Text
    ctx.fillStyle = "lime";
    ctx.font = `${fontSize}px sans-serif`;
    ctx.textAlign = "left";
    ctx.fillText(text, posX, canvas.height / 2);

    posX += direction;

    if (posX + textWidth >= canvas.width || posX <= 0) {
      direction *= -1;
    }

    animationFrameId = requestAnimationFrame(draw);
  }

  draw();
}

async function saveDesign() {
  const design = {
    type: animationType,
    created: new Date().toISOString()
  };

  try {
    const response = await fetch("/save_animation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(design)
    });

    const result = await response.json();

    if (response.ok) {
      alert("Animation saved! ID: " + result.animation_id);
      location.href = "/my_animations";
    } else {
      alert("Error saving: " + result.error);
    }
  } catch (err) {
    alert("Failed to save animation: " + err.message);
  }
}

// Start first animation on load
startAnimation();
