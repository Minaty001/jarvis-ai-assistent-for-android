---
name: jarvis-web-designs
description: 55 real-world design systems (Stripe, Linear, Vercel, Apple) + Signature Stark JARVIS MCU HUD & Brain UI as HTML/CSS.
version: 1.1.0
author: Jarvis AI Team (adapted from Hermes Agent + Teknium)
license: MIT
tags: [design, css, html, ui, web-development, design-systems, templates, jarvis, mcu, hud, brain-ui]
platforms: [linux, macos, windows, termux]
triggers:
  - make it look like jarvis
  - jarvis style
  - stark hud design
  - mcu iron man theme
  - jarvis brain UI
  - build a page that looks like
  - make it look like stripe
  - design like linear
  - vercel style
  - create a UI
  - web design
  - landing page
  - dashboard design
  - website styled like
---

# Jarvis Popular Web Designs & MCU HUD Design System

55 real-world design systems plus the **Signature Stark JARVIS MCU HUD & Cortical Brain UI** ready for generating HTML/CSS. Each template captures a complete visual language: color palette, typography hierarchy, component styles, spacing system, shadows, responsive behavior, and agent prompts with exact CSS values.

## Signature JARVIS Design Systems

### 1. Stark JARVIS MCU & Cortical Brain UI (`jarvis-mcu`)
- **Theme:** Void-black cybernetic canvas (`#050811`), neon arc-reactor accents, glassmorphic HUD panels, live neural pathway animations.
- **Font Stack:** Primary: `'Orbitron'`, `'Rajdhani'`, system-ui; Monospace: `'JetBrains Mono'`, monospace.
- **Google Fonts Link:** `<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">`
- **Cortical Region Palette:**
  - Executive (PFC): Amber `#ffaa00`
  - Speech (Auditory STT): Cyan `#00f0ff`
  - LLM (Wernicke): Green `#00ff88`
  - Voice (Broca TTS): Purple `#8844ff`
  - Device (Motor): Red `#ff3366`
  - Memory (Hippocampus): Blue `#0066ff`
  - Vision (Occipital): Magenta `#ff00ff`
  - Telemetry (Somatosensory): Teal `#00ffcc`
  - Defense (Protocol): Bright Red `#ff3300`
  - Search (Thalamus): Yellow `#ffff00`
  - Scheduler (Cerebellum): Lime `#aaff00`

```css
:root {
  --jarvis-bg-void: #050811;
  --jarvis-bg-panel: rgba(10, 16, 32, 0.75);
  --jarvis-border-glow: rgba(0, 240, 255, 0.25);
  --jarvis-text-primary: #f0f6fc;
  --jarvis-text-muted: #8b949e;
  --jarvis-accent-cyan: #00f0ff;
  --jarvis-accent-gold: #ffaa00;
  --jarvis-accent-red: #ff3300;
  --jarvis-accent-green: #00ff88;
  --jarvis-font-head: 'Orbitron', 'Rajdhani', sans-serif;
  --jarvis-font-body: 'Inter', system-ui, sans-serif;
  --jarvis-font-mono: 'JetBrains Mono', monospace;
  --jarvis-shadow-hud: 0 0 25px rgba(0, 240, 255, 0.15);
}

body {
  background-color: var(--jarvis-bg-void);
  background-image: 
    radial-gradient(circle at 50% 0%, rgba(0, 240, 255, 0.1) 0%, transparent 60%),
    linear-gradient(to bottom, rgba(5, 8, 17, 0.9), #050811);
  color: var(--jarvis-text-primary);
  font-family: var(--jarvis-font-body);
}

.jarvis-hud-card {
  background: var(--jarvis-bg-panel);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--jarvis-border-glow);
  border-radius: 12px;
  box-shadow: var(--jarvis-shadow-hud);
  padding: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.jarvis-hud-card:hover {
  border-color: rgba(0, 240, 255, 0.5);
  box-shadow: 0 0 35px rgba(0, 240, 255, 0.3);
  transform: translateY(-2px);
}
```

---

## HTML Generation Pattern for Jarvis

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JARVIS System HUD</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-void: #050811;
      --bg-card: rgba(12, 20, 38, 0.7);
      --border-cyan: rgba(0, 240, 255, 0.3);
      --text-main: #e6edf3;
      --cyan-glow: #00f0ff;
      --gold-glow: #ffaa00;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg-void);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
    }
    h1 {
      font-family: 'Orbitron', sans-serif;
      color: var(--cyan-glow);
      text-transform: uppercase;
      letter-spacing: 3px;
      text-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
      margin-bottom: 1.5rem;
    }
    .hud-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
      width: 100%;
      max-width: 1200px;
    }
    .card {
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-cyan);
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.1);
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: var(--gold-glow);
    }
    .dot {
      width: 8px;
      height: 8px;
      background: var(--gold-glow);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--gold-glow);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }
  </style>
</head>
<body>
  <h1>JARVIS Cortical HUD</h1>
  <div class="hud-grid">
    <div class="card">
      <div class="status-badge"><div class="dot"></div> PROTOCOL ALPHA: NOMINAL</div>
      <p style="margin-top: 1rem; color: #8b949e;">All 11 neural pathways online and operating at maximum capacity.</p>
    </div>
  </div>
</body>
</html>
```

---

## Complete Brand Catalog

### AI & Machine Learning
- `jarvis-mcu` — Stark JARVIS MCU HUD, arc-reactor glow, glassmorphism, 11-region cortical map
- `claude` — Anthropic Claude: Warm terracotta accent, clean editorial layout
- `cohere` — Cohere: Vibrant gradients, data-rich dashboard aesthetic
- `elevenlabs` — ElevenLabs: Dark cinematic UI, audio-waveform aesthetics
- `mistral.ai` — Mistral AI: French-engineered minimalism, purple-toned
- `ollama` — Ollama: Terminal-first, monochrome simplicity
- `opencode.ai` — OpenCode AI: Developer-centric dark theme, full monospace
- `x.ai` — xAI: Stark monochrome, futuristic minimalism, full monospace

### Developer Tools & Platforms
- `linear.app` — Linear: Ultra-minimal dark-mode, precise, purple accent
- `vercel` — Vercel: Black and white precision, Geist font system
- `supabase` — Supabase: Dark emerald theme, code-first developer tool
- `raycast` — Raycast: Sleek dark chrome, vibrant gradient accents
- `resend` — Resend: Minimal dark theme, monospace accents
- `sentry` — Sentry: Dark dashboard, data-dense, pink-purple accent
- `warp` — Warp: Dark IDE-like interface, block-based command UI

### Infrastructure & Cloud
- `stripe` — Stripe: Signature purple gradients, weight-300 elegance
- `hashicorp` — HashiCorp: Enterprise-clean, black and white
- `clickhouse` — ClickHouse: Yellow-accented, technical documentation style

### Fintech, Enterprise & Consumer
- `apple` — Apple: Premium white space, SF Pro, cinematic imagery
- `spotify` — Spotify: Vibrant green on dark, bold type, album-art-driven
- `revolut` — Revolut: Sleek dark interface, gradient cards, fintech precision
- `spacex` — SpaceX: Stark black and white, full-bleed imagery, futuristic

---

## Choosing a Design Style for Jarvis

- **Stark / Iron Man / Assistant HUD:** Use `jarvis-mcu` (Void black, cyan/gold glow, glassmorphic cards, Orbitron font).
- **Developer / Coding Dashboard:** Use `linear.app`, `vercel`, `supabase`, `raycast`.
- **Minimalist Content / Notes:** Use `notion`, `claude`, `mintlify`.
- **Premium Corporate / Presentation:** Use `stripe`, `apple`, `revolut`.
