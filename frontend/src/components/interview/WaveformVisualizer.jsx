import React, { useRef, useEffect } from 'react';

export const WaveformVisualizer = ({ isRecording, analyserNode, audioLevel }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      if (!isRecording) {
        // Idle ambient line
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.strokeStyle = 'rgba(100, 116, 139, 0.3)';
        ctx.lineWidth = 2;
        ctx.stroke();
        return;
      }

      if (analyserNode) {
        const bufferLength = analyserNode.fftSize;
        const dataArray = new Uint8Array(bufferLength);
        analyserNode.getByteTimeDomainData(dataArray);

        // Draw glowing wave
        ctx.lineWidth = 3;
        const gradient = ctx.createLinearGradient(0, 0, width, 0);
        gradient.addColorStop(0, '#3b82f6');
        gradient.addColorStop(0.5, '#8b5cf6');
        gradient.addColorStop(1, '#ec4899');
        ctx.strokeStyle = gradient;

        ctx.beginPath();
        const sliceWidth = (width * 1.0) / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = (v * height) / 2;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
          x += sliceWidth;
        }

        ctx.lineTo(width, height / 2);
        ctx.stroke();

        // Draw frequency bars in background
        const freqArray = new Uint8Array(analyserNode.frequencyBinCount);
        analyserNode.getByteFrequencyData(freqArray);
        const barWidth = (width / 32) - 2;
        let barX = 0;

        for (let i = 0; i < 32; i++) {
          const barHeight = (freqArray[i * 2] / 255) * (height / 2);
          ctx.fillStyle = `rgba(59, 130, 246, ${Math.max(0.15, barHeight / height)})`;
          ctx.fillRect(barX, height - barHeight, barWidth, barHeight);
          barX += barWidth + 2;
        }
      } else {
        // Fallback simulation wave
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#3b82f6';
        ctx.beginPath();
        for (let i = 0; i < width; i++) {
          const y = height / 2 + Math.sin(i * 0.05 + Date.now() * 0.01) * (audioLevel * 0.4);
          if (i === 0) ctx.moveTo(i, y);
          else ctx.lineTo(i, y);
        }
        ctx.stroke();
      }

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [isRecording, analyserNode, audioLevel]);

  return (
    <div className="w-full flex flex-col items-center">
      <canvas
        ref={canvasRef}
        width={500}
        height={80}
        className="w-full h-20 rounded-xl bg-slate-900/60 border border-slate-800/80"
      />
    </div>
  );
};
