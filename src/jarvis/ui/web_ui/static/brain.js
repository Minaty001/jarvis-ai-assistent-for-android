/**
 * JARVIS Brain Visualization - Responsive Neural Network Canvas.
 * Supports auto-adapting layouts for Desktop (wide) and Android Mobile (compact).
 * Crafted by Minaty001.
 */

class BrainCanvas {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.regions = {};
        this.pathways = [];
        this.animationId = null;
        this.particles = [];
        this._init();
    }

    _init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('orientationchange', () => setTimeout(() => this.resize(), 200));
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = (rect.width || 360) * dpr;
        this.canvas.height = (rect.height || 160) * dpr;
        this.ctx.scale(dpr, dpr);
        this.cssWidth = rect.width || 360;
        this.cssHeight = rect.height || 160;
    }

    update(data) {
        this.regions = data.regions || {};
        this.pathways = data.active_pathways || [];
    }

    start() {
        if (!this.animationId) {
            this._animate();
        }
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    _animate() {
        this.ctx.clearRect(0, 0, this.cssWidth, this.cssHeight);
        this._drawBackground();
        this._drawPathways();
        this._drawRegions();
        this._drawParticles();
        this.animationId = requestAnimationFrame(() => this._animate());
    }

    _drawBackground() {
        const ctx = this.ctx;
        const w = this.cssWidth;
        const h = this.cssHeight;

        // Dark gradient background
        const grad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.max(w, h) / 2);
        grad.addColorStop(0, 'rgba(0, 35, 70, 0.35)');
        grad.addColorStop(1, 'rgba(2, 11, 20, 0.1)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);

        // Grid dots
        ctx.fillStyle = 'rgba(0, 240, 255, 0.08)';
        const step = Math.max(24, Math.floor(w / 16));
        for (let x = step / 2; x < w; x += step) {
            for (let y = step / 2; y < h; y += step) {
                ctx.beginPath();
                ctx.arc(x, y, 1, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    _drawPathways() {
        if (!this.pathways.length) return;

        const regionPositions = this._getRegionPositions();
        const ctx = this.ctx;
        const now = Date.now() / 1000;

        for (const [src, dst] of this.pathways) {
            const srcPos = regionPositions[src.toLowerCase()];
            const dstPos = regionPositions[dst.toLowerCase()];
            if (!srcPos || !dstPos) continue;

            const pulse = 0.3 + 0.7 * (Math.sin(now * 3.5 + srcPos.x) * 0.5 + 0.5);

            ctx.beginPath();
            ctx.moveTo(srcPos.x, srcPos.y);
            ctx.lineTo(dstPos.x, dstPos.y);
            ctx.strokeStyle = `rgba(0, 240, 255, ${0.18 + pulse * 0.4})`;
            ctx.lineWidth = 1.2 + pulse * 1.8;
            ctx.shadowColor = '#00f0ff';
            ctx.shadowBlur = 10 * pulse;
            ctx.stroke();
            ctx.shadowBlur = 0;

            if (Math.random() < 0.3) {
                this.particles.push({
                    x: srcPos.x,
                    y: srcPos.y,
                    targetX: dstPos.x,
                    targetY: dstPos.y,
                    t: 0,
                    speed: 0.025 + Math.random() * 0.035,
                    size: 2 + Math.random() * 2.5,
                    life: 1,
                });
            }
        }
    }

    _drawRegions() {
        const positions = this._getRegionPositions();
        const ctx = this.ctx;
        const minDim = Math.min(this.cssWidth, this.cssHeight);
        const isWide = (this.cssWidth / this.cssHeight) > 1.8;
        const baseRadius = isWide 
            ? Math.max(12, Math.min(22, minDim * 0.08))
            : Math.max(10, Math.min(18, minDim * 0.09));

        for (const [key, region] of Object.entries(this.regions)) {
            const pos = positions[key];
            if (!pos) continue;

            const isActive = region.active;
            const radius = isActive ? baseRadius * 1.25 : baseRadius;
            const color = this._hexToRgba(region.color || '#00f0ff', isActive ? 0.95 : 0.45);

            if (isActive) {
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, radius * 1.6, 0, Math.PI * 2);
                const glow = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, radius * 1.6);
                glow.addColorStop(0, `rgba(0, 240, 255, 0.28)`);
                glow.addColorStop(1, `rgba(0, 240, 255, 0)`);
                ctx.fillStyle = glow;
                ctx.fill();
            }

            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.shadowColor = isActive ? '#00f0ff' : 'transparent';
            ctx.shadowBlur = isActive ? 18 : 0;
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.strokeStyle = isActive ? '#00f0ff' : 'rgba(0, 240, 255, 0.35)';
            ctx.lineWidth = isActive ? 2 : 1;
            ctx.stroke();

            const fontSize = Math.max(7, Math.min(11, baseRadius * 0.55));
            ctx.fillStyle = isActive ? '#ffffff' : 'rgba(255, 255, 255, 0.7)';
            ctx.font = `700 ${fontSize}px Orbitron, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(region.name || key.toUpperCase(), pos.x, pos.y);

            if (region.latency_ms > 0 && isActive) {
                ctx.fillStyle = 'rgba(0, 240, 255, 0.75)';
                ctx.font = '7px monospace';
                ctx.fillText(region.latency_ms.toFixed(0) + 'ms', pos.x, pos.y + radius + 8);
            }
        }
    }

    _drawParticles() {
        const ctx = this.ctx;
        this.particles = this.particles.filter(p => p.life > 0 && p.t < 1);

        for (const p of this.particles) {
            p.t += p.speed;
            p.x += (p.targetX - p.x) * p.speed;
            p.y += (p.targetY - p.y) * p.speed;
            p.life -= 0.012;

            ctx.beginPath();
            ctx.arc(p.x, p.y, Math.max(1, p.size * p.life), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 240, 255, ${p.life * 0.85})`;
            ctx.shadowColor = '#00f0ff';
            ctx.shadowBlur = 8 * p.life;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    _getRegionPositions() {
        const w = this.cssWidth;
        const h = this.cssHeight;
        const cx = w / 2;
        const cy = h / 2;

        const isWide = (w / h) > 1.8;

        if (isWide) {
            const scaleX = Math.min(w / 650, 1.3);
            const scaleY = Math.min(h / 240, 1.3);

            return {
                pfc: { x: cx, y: cy - 75 * scaleY },
                auditory: { x: cx - 120 * scaleX, y: cy - 40 * scaleY },
                motor: { x: cx + 120 * scaleX, y: cy - 40 * scaleY },
                wernicke: { x: cx - 75 * scaleX, y: cy + 15 * scaleY },
                broca: { x: cx + 75 * scaleX, y: cy + 15 * scaleY },
                hippocampus: { x: cx, y: cy + 80 * scaleY },
                occipital: { x: cx - 210 * scaleX, y: cy - 65 * scaleY },
                somatosensory: { x: cx + 210 * scaleX, y: cy - 65 * scaleY },
                defense: { x: cx - 180 * scaleX, y: cy + 55 * scaleY },
                thalamus: { x: cx + 180 * scaleX, y: cy + 55 * scaleY },
                cerebellum: { x: cx, y: cy + 42 * scaleY },
            };
        } else {
            const scaleX = Math.min(w / 340, 1.2);
            const scaleY = Math.min(h / 150, 1.2);

            return {
                pfc: { x: cx, y: cy - 52 * scaleY },
                auditory: { x: cx - 60 * scaleX, y: cy - 28 * scaleY },
                motor: { x: cx + 60 * scaleX, y: cy - 28 * scaleY },
                wernicke: { x: cx - 38 * scaleX, y: cy + 8 * scaleY },
                broca: { x: cx + 38 * scaleX, y: cy + 8 * scaleY },
                hippocampus: { x: cx, y: cy + 55 * scaleY },
                occipital: { x: cx - 110 * scaleX, y: cy - 42 * scaleY },
                somatosensory: { x: cx + 110 * scaleX, y: cy - 42 * scaleY },
                defense: { x: cx - 95 * scaleX, y: cy + 38 * scaleY },
                thalamus: { x: cx + 95 * scaleX, y: cy + 38 * scaleY },
                cerebellum: { x: cx, y: cy + 28 * scaleY },
            };
        }
    }

    _hexToRgba(hex, alpha) {
        if (!hex || typeof hex !== 'string') return `rgba(0, 240, 255, ${alpha})`;
        const match = hex.match(/#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i);
        if (match) {
            return `rgba(${parseInt(match[1], 16)}, ${parseInt(match[2], 16)}, ${parseInt(match[3], 16)}, ${alpha})`;
        }
        return `rgba(0, 240, 255, ${alpha})`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('brain-canvas');
    if (canvas) {
        window.brainCanvas = new BrainCanvas('brain-canvas');
        window.brainCanvas.start();

        if (window.EventSource) {
            const source = new EventSource('/api/stream');
            source.onmessage = function(e) {
                try {
                    const data = JSON.parse(e.data);
                    if (window.brainCanvas) {
                        window.brainCanvas.update(data);
                    }
                } catch (err) {}
            };
        }
    }
});
