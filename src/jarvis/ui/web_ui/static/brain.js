/**
 * JARVIS Brain Visualization - Interactive neural network canvas.
 * Displays real-time cortical region activity and neural pathways.
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
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width || 400;
        this.canvas.height = rect.height || 400;
    }

    update(data) {
        this.regions = data.regions || {};
        this.pathways = data.active_pathways || [];
    }

    start() {
        this._animate();
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    _animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this._drawBackground();
        this._drawPathways();
        this._drawRegions();
        this._drawParticles();
        this.animationId = requestAnimationFrame(() => this._animate());
    }

    _drawBackground() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Dark gradient background
        const grad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
        grad.addColorStop(0, 'rgba(0, 30, 60, 0.3)');
        grad.addColorStop(1, 'rgba(10, 10, 15, 0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);

        // Grid dots
        ctx.fillStyle = 'rgba(0, 240, 255, 0.08)';
        for (let x = 0; x < w; x += 30) {
            for (let y = 0; y < h; y += 30) {
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

            const pulse = 0.3 + 0.7 * (Math.sin(now * 3 + srcPos.x) * 0.5 + 0.5);

            // Glow line
            ctx.beginPath();
            ctx.moveTo(srcPos.x, srcPos.y);
            ctx.lineTo(dstPos.x, dstPos.y);
            ctx.strokeStyle = `rgba(0, 240, 255, ${0.1 + pulse * 0.3})`;
            ctx.lineWidth = 1 + pulse * 2;
            ctx.shadowColor = '#00f0ff';
            ctx.shadowBlur = 10 * pulse;
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Data packet traveling along the pathway
            if (Math.random() < 0.3) {
                this.particles.push({
                    x: srcPos.x,
                    y: srcPos.y,
                    targetX: dstPos.x,
                    targetY: dstPos.y,
                    t: 0,
                    speed: 0.02 + Math.random() * 0.03,
                    size: 2 + Math.random() * 3,
                    life: 1,
                });
            }
        }
    }

    _drawRegions() {
        const positions = this._getRegionPositions();
        const ctx = this.ctx;

        for (const [key, region] of Object.entries(this.regions)) {
            const pos = positions[key];
            if (!pos) continue;

            const isActive = region.active;
            const radius = isActive ? 28 : 20;
            const color = this._hexToRgba(region.color || '#00f0ff', isActive ? 0.9 : 0.4);

            // Glow for active regions
            if (isActive) {
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, radius * 1.5, 0, Math.PI * 2);
                const glow = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, radius * 1.5);
                glow.addColorStop(0, `rgba(0, 240, 255, 0.15)`);
                glow.addColorStop(1, `rgba(0, 240, 255, 0)`);
                ctx.fillStyle = glow;
                ctx.fill();
            }

            // Region circle
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.shadowColor = isActive ? '#00f0ff' : 'transparent';
            ctx.shadowBlur = isActive ? 20 : 0;
            ctx.fill();
            ctx.shadowBlur = 0;

            // Border
            ctx.strokeStyle = isActive ? '#00f0ff' : 'rgba(0, 240, 255, 0.3)';
            ctx.lineWidth = isActive ? 2 : 1;
            ctx.stroke();

            // Label
            ctx.fillStyle = isActive ? '#ffffff' : 'rgba(255, 255, 255, 0.5)';
            ctx.font = '9px Orbitron, monospace';
            ctx.textAlign = 'center';
            ctx.fillText(region.name || key, pos.x, pos.y + 4);

            // Latency
            if (region.latency_ms > 0) {
                ctx.fillStyle = 'rgba(0, 240, 255, 0.5)';
                ctx.font = '7px monospace';
                ctx.fillText(region.latency_ms.toFixed(0) + 'ms', pos.x, pos.y + radius + 12);
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
            p.life -= 0.01;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 240, 255, ${p.life * 0.8})`;
            ctx.shadowColor = '#00f0ff';
            ctx.shadowBlur = 10 * p.life;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    _getRegionPositions() {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const cx = w / 2;
        const cy = h / 2;

        return {
            pfc: { x: cx, y: cy - 90 },
            auditory: { x: cx - 70, y: cy - 20 },
            motor: { x: cx + 70, y: cy - 20 },
            wernicke: { x: cx - 50, y: cy + 60 },
            broca: { x: cx + 50, y: cy + 60 },
            hippocampus: { x: cx, y: cy + 120 },
        };
    }

    _hexToRgba(hex, alpha) {
        if (!hex || typeof hex !== 'string') return `rgba(0, 240, 255, ${alpha})`;
        // Handle ANSI color codes or hex
        const match = hex.match(/#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i);
        if (match) {
            return `rgba(${parseInt(match[1], 16)}, ${parseInt(match[2], 16)}, ${parseInt(match[3], 16)}, ${alpha})`;
        }
        return `rgba(0, 240, 255, ${alpha})`;
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('brain-canvas');
    if (canvas) {
        window.brainCanvas = new BrainCanvas('brain-canvas');
        window.brainCanvas.start();

        // Update from SSE or polling
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
