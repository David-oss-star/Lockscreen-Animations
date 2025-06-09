// animationRegistry.js

const animationRegistry = {
    clock: {
      factory: (ctx, canvas) => {
        return () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "#111";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "white";
          ctx.font = "32px monospace";
          ctx.textAlign = "center";
          ctx.fillText(new Date().toLocaleTimeString(), canvas.width / 2, canvas.height / 2);
        };
      }
    },
  
    bouncingText: {
      factory: (ctx, canvas) => {
        const text = "Hello!";
        let posX = 0;
        let direction = 2;
        const fontSize = 28;
  
        ctx.font = `${fontSize}px sans-serif`;
        const textWidth = ctx.measureText(text).width;
  
        return () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "#111";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "lime";
          ctx.font = `${fontSize}px sans-serif`;
          ctx.textAlign = "left";
          ctx.fillText(text, posX, canvas.height / 2);
  
          posX += direction;
          if (posX + textWidth >= canvas.width || posX <= 0) direction *= -1;
        };
      }
    },
  
    waveText: {
      factory: (ctx, canvas) => {
        let angle = 0;
        return () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "#111";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
  
          const text = "Wave!";
          ctx.font = "28px sans-serif";
          ctx.fillStyle = "cyan";
          const y = canvas.height / 2 + Math.sin(angle) * 20;
          ctx.fillText(text, canvas.width / 2, y);
          angle += 0.1;
        };
      }
    },
  
    colorPulse: {
      factory: (ctx, canvas) => {
        let hue = 0;
  
        return () => {
          hue = (hue + 1) % 360;
          const color = `hsl(${hue}, 100%, 50%)`;
  
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = color;
          ctx.fillRect(0, 0, canvas.width, canvas.height);
  
          ctx.fillStyle = "#000";
          ctx.font = "28px sans-serif";
          ctx.textAlign = "center";
          ctx.fillText("Color Pulse", canvas.width / 2, canvas.height / 2);
        };
      }
    },
  
    yourNewAnimationName: {
      factory: (ctx, canvas) => {
        let frame = 0;
  
        return () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "#111";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
  
          ctx.fillStyle = "orange";
          ctx.font = "28px sans-serif";
          ctx.textAlign = "center";
          ctx.fillText("Your Animation!", canvas.width / 2, canvas.height / 2 + Math.sin(frame) * 10);
  
          frame += 0.1;
        };
      }
    },
  };
  
  export default animationRegistry;
  