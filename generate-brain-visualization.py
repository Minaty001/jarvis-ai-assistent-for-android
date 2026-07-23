#!/usr/bin/env python3
"""
Generate brain architecture visualization for Jarvis AI Assistant.
Creates an SVG showing brain regions as interconnected neural network.
"""
import math, os, random

W, H = 1200, 900
CX, CY = W // 2, H // 2

# ---- Color Palette ----
BG = "#0a0a0f"
NEON_CYAN = "#00f0ff"
NEON_BLUE = "#0066ff"
NEON_AMBER = "#ffaa00"
NEON_PURPLE = "#8844ff"
NEON_GREEN = "#00ff88"
NEON_RED = "#ff3366"
DIM_CYAN = "#004466"
GLOW = "#00aaff"

REGION_COLORS = {
    "PFC": {"fill": "#1a0a30", "stroke": NEON_AMBER, "glow": "rgba(255,170,0,0.15)"},
    "auditory": {"fill": "#0a1a30", "stroke": NEON_CYAN, "glow": "rgba(0,240,255,0.12)"},
    "wernicke": {"fill": "#0a3018", "stroke": NEON_GREEN, "glow": "rgba(0,255,136,0.12)"},
    "broca": {"fill": "#1a0a18", "stroke": NEON_PURPLE, "glow": "rgba(136,68,255,0.12)"},
    "motor": {"fill": "#300a0a", "stroke": NEON_RED, "glow": "rgba(255,51,102,0.12)"},
    "hippocampus": {"fill": "#0a1a20", "stroke": NEON_BLUE, "glow": "rgba(0,102,255,0.12)"},
}

# ---- SVG Builder Functions ----
svg = []

def emit(tag, **attrs):
    attrs_str = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in attrs.items())
    svg.append(f"  <{tag} {attrs_str}/>")

def text_label(t, x, y, color, size, anchor="middle", opacity="1", family="'Courier New', monospace", weight="normal"):
    emit("text", x=x, y=y, text_anchor=anchor, fill=color,
         font_family=family, font_size=str(size), opacity=opacity, font_weight=weight)
    svg[-1] = svg[-1].replace("/>", f">{t}</text>")

def draw_neural_path(x1, y1, x2, y2, color, dash="", opacity="0.5", width="1.5", glow=True):
    cx1, cy1 = x1 + (x2 - x1) * 0.35, y1
    cx2, cy2 = x2 - (x2 - x1) * 0.35, y2
    path = f"M{x1},{y1} C{cx1},{cy1} {cx2},{cy2} {x2},{y2}"
    if glow:
        emit("path", d=path, fill="none", stroke=color, stroke_width="4", opacity="0.15",
             stroke_dasharray=dash, filter="url(#bigGlow)")
    emit("path", d=path, fill="none", stroke=color, stroke_width=width, opacity=opacity, stroke_dasharray=dash)

def draw_region(path_data, region_id, label, center_x, center_y):
    c = REGION_COLORS[region_id]
    emit("path", d=path_data, fill=c["glow"], filter="url(#bigGlow)")
    emit("path", d=path_data, fill=c["fill"], stroke=c["stroke"],
         stroke_width="1.5", opacity="0.85", filter="url(#glow)")
    emit("path", d=path_data, fill="none", stroke=c["stroke"],
         stroke_width="0.5", opacity="0.4",
         transform=f"scale(0.97) translate({int(center_x*0.03)},{int(center_y*0.03)})")
    text_label(label, center_x, center_y-6, c["stroke"], 11)
    sub = {"PFC":"Executive Control","auditory":"Speech Recognition","wernicke":"LLM / Reasoning",
           "broca":"Voice / TTS","motor":"Device Control","hippocampus":"Memory / Storage"}
    text_label(sub[region_id], center_x, center_y+14, c["stroke"], 7, opacity="0.6")

# ---- SVG Document ----
svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="{W}" height="{H}">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="bigGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="15" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <radialGradient id="bgGlow" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#0d1b2a"/>
      <stop offset="100%" stop-color="{BG}"/>
    </radialGradient>
    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{NEON_CYAN}" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="{NEON_CYAN}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{NEON_CYAN}" stop-opacity="0.1"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1a2744" stroke-width="0.5"/>
    </pattern>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="4" y2="0" stroke="rgba(0,240,255,0.03)" stroke-width="1"/>
    </pattern>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#bgGlow)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <rect width="{W}" height="{H}" fill="url(#scanlines)"/>

  <text x="{CX}" y="55" text-anchor="middle" fill="{NEON_CYAN}"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold"
        letter-spacing="6" opacity="0.6">// JARVIS NEURAL ARCHITECTURE //</text>
  <text x="{CX}" y="80" text-anchor="middle" fill="{NEON_CYAN}"
        font-family="'Courier New', monospace" font-size="10" letter-spacing="3" opacity="0.3">
    CORTICAL NETWORK v2.0 — AI ASSISTANT BRAIN MAP</text>
  <line x1="100" y1="90" x2="{W-100}" y2="90" stroke="{DIM_CYAN}" stroke-width="1" opacity="0.4"/>
''')

# HUD corners
for cx, cy in [(20,20),(W-20,20),(20,H-20),(W-20,H-20)]:
    emit("path", d=f"M{cx},{cy+15} L{cx},{cy} L{cx+15},{cy}",
         fill="none", stroke=NEON_CYAN, stroke_width="1.5", opacity="0.3")

# Status bar
emit("rect", x="30", y=str(H-35), width="200", height="8", rx="4", fill="#1a2744", opacity="0.5")
emit("rect", x="30", y=str(H-35), width="140", height="8", rx="4", fill=NEON_CYAN, opacity="0.4")
text_label("NEURAL ACTIVITY: 72%", 38, H-39, NEON_CYAN, 8, "left", "0.4")
text_label("CORTEX: ONLINE", W-150, H-39, NEON_GREEN, 8, "left", "0.4")

# ====================
# BRAIN REGIONS
# ====================

# Prefrontal Cortex - top front
pfc_path = ("M520,160 C540,145 580,140 610,150 C630,158 640,175 635,195 "
            "C628,220 610,235 590,240 C570,245 545,240 530,225 "
            "C515,210 510,185 520,160Z")
draw_region(pfc_path, "PFC", "PFC", 570, 195)

# Auditory Cortex - left
aud_path = ("M155,320 C140,290 145,255 165,235 C185,218 210,215 230,228 "
            "C248,240 260,268 258,295 C255,325 240,350 220,360 "
            "C200,368 175,360 160,340 C150,325 155,320 155,320Z")
draw_region(aud_path, "auditory", "AUDITORY CORTEX", 203, 290)

# Wernicke's Area - lower center
wern_path = ("M380,460 C395,430 430,415 465,418 C498,420 520,440 525,468 "
             "C530,495 518,530 498,548 C478,562 445,565 418,555 "
             "C395,545 382,520 378,495 C375,475 380,460 380,460Z")
draw_region(wern_path, "wernicke", "WERNICKE'S AREA", 448, 492)

# Broca's Area - lower front
broca_path = ("M580,420 C605,408 635,405 655,418 C672,430 678,455 668,478 "
              "C658,500 635,515 610,518 C588,520 565,512 555,495 "
              "C548,480 550,452 560,435 C568,425 580,420 580,420Z")
draw_region(broca_path, "broca", "BROCA'S AREA", 618, 465)

# Motor Cortex - top right
motor_path = ("M740,230 C760,215 785,212 805,222 C822,232 835,255 835,278 "
              "C830,310 815,335 795,345 C775,354 750,348 738,330 "
              "C725,312 720,280 725,252 C730,240 740,230 740,230Z")
draw_region(motor_path, "motor", "MOTOR CORTEX", 780, 280)

# Hippocampus - center deep
hippo_path = ("M315,380 C330,360 360,352 388,358 C412,363 432,380 435,400 "
              "C438,418 430,440 410,452 C392,462 365,465 345,458 "
              "C325,450 310,430 308,410 C305,395 315,380 315,380Z")
draw_region(hippo_path, "hippocampus", "HIPPOCAMPUS", 372, 408)

# ====================
# NEURAL PATHWAYS
# ====================

paths = [
    (235, 330, 400, 470, NEON_GREEN, "Perception Pathway"),
    (470, 460, 560, 230, NEON_AMBER, "Cognitive Relay"),
    (620, 240, 750, 290, NEON_RED, "Action Command"),
    (760, 270, 640, 220, NEON_RED, "Motor Feedback"),
    (510, 480, 590, 458, NEON_PURPLE, "Expression Pathway"),
    (410, 420, 440, 470, NEON_BLUE, "Memory Recall"),
    (455, 500, 400, 430, NEON_BLUE, "Memory Formation"),
    (540, 230, 400, 400, NEON_AMBER, "Executive Query"),
    (630, 480, 770, 340, NEON_PURPLE, "Speech-Action"),
    (250, 280, 530, 200, NEON_CYAN, "Alert Signal"),
]

for x1, y1, x2, y2, color, label in paths:
    dash = "4,4" if any(w in label for w in ["Feedback","Formation","Speech-Action"]) else ""
    op = "0.35" if dash else "0.45"
    w = "1.2" if dash else "1.5"
    draw_neural_path(x1, y1, x2, y2, color, dash=dash, opacity=op, width=w)
    if any(w in label for w in ["Perception","Cognitive","Action Command",
                                 "Expression","Memory Recall","Executive Query","Alert"]):
        cx, cy = (x1+x2)//2, (y1+y2)//2
        emit("circle", cx=cx, cy=cy, r="3", fill=color, opacity="0.7")

# Pathway labels
path_labels = [
    (317, 400, "MEMORY → LLM", NEON_BLUE),
    (503, 470, "LLM → SPEECH", NEON_PURPLE),
    (612, 265, "→ EXECUTIVE", NEON_AMBER),
    (680, 265, "→ ACTION", NEON_RED),
    (330, 250, "PERCEPTION →", NEON_CYAN),
]
for x, y, txt, col in path_labels:
    text_label(txt, x, y, col, 7, "middle", "0.4")

# ====================
# LEGEND
# ====================
lx, ly = 35, 130
emit("rect", x=lx, y=ly, width="185", height="220", rx="6",
     fill="rgba(10,10,15,0.8)", stroke=DIM_CYAN, stroke_width="1", opacity="0.6")
text_label("CORTICAL REGIONS", lx+92, ly+22, NEON_CYAN, 9, "middle", "0.7")

legend_items = [
    ("PFC — Executive", NEON_AMBER),
    ("Auditory Cortex — STT", NEON_CYAN),
    ("Wernicke's Area — LLM", NEON_GREEN),
    ("Broca's Area — TTS", NEON_PURPLE),
    ("Motor Cortex — Device", NEON_RED),
    ("Hippocampus — Memory", NEON_BLUE),
]
for i, (name, col) in enumerate(legend_items):
    iy = ly + 42 + i * 28
    emit("circle", cx=lx+20, cy=iy-4, r="5", fill="none", stroke=col, stroke_width="1.5", opacity="0.8")
    text_label(name, lx+35, iy, col, 9, "start", "0.7")

emit("line", x1=str(lx+10), y1=str(ly+217), x2=str(lx+175), y2=str(ly+217),
     stroke=DIM_CYAN, stroke_width="1", opacity="0.3")
text_label("— bidirectional pathway", lx+92, ly+233, DIM_CYAN, 7, "middle", "0.4")
text_label("- - - feedback / formation", lx+92, ly+248, DIM_CYAN, 7, "middle", "0.4")

# ====================
# Synaptic dots
# ====================
random.seed(42)
for _ in range(60):
    x = random.randint(120, W-120)
    y = random.randint(120, H-60)
    if any(abs(x-rx)<60 and abs(y-ry)<60 for rx,ry in [(570,195),(203,290),(448,492),
                                                        (618,465),(780,280),(372,408)]):
        continue
    alpha = random.uniform(0.05, 0.2)
    r = random.uniform(1, 2.5)
    emit("circle", cx=x, cy=y, r=f"{r:.1f}", fill=NEON_CYAN, opacity=f"{alpha:.2f}")

# ====================
# Bottom HUD metrics
# ====================
metrics = [
    ("ACTIVE REGIONS", "6/6", NEON_GREEN),
    ("SYNAPTIC PATHWAYS", "10", NEON_CYAN),
    ("NEURAL LATENCY", "42ms", NEON_AMBER),
    ("CORTEX STATUS", "OPTIMAL", NEON_GREEN),
]
mx = 200
for i, (label, value, col) in enumerate(metrics):
    bx = CX - 400 + i * mx
    emit("rect", x=bx, y=str(H-95), width="170", height="45", rx="4",
         fill="rgba(10,10,15,0.6)", stroke=DIM_CYAN, stroke_width="0.5", opacity="0.5")
    text_label(label, bx+85, H-78, DIM_CYAN, 7, "middle", "0.6")
    text_label(value, bx+85, H-60, col, 14, "middle", "0.9", weight="bold")

# ====================
# Neural particles
# ====================
for i in range(15):
    angle = i * 24 * math.pi / 180
    dist = 300 + random.randint(-50, 50)
    px = CX + dist * math.cos(angle)
    py = CY + dist * math.sin(angle) * 0.6
    if 50 < px < W-50 and 100 < py < H-100:
        emit("circle", cx=px, cy=py, r="1", fill=NEON_CYAN, opacity="0.15")

# Frame edge accents
emit("line", x1="0", y1=str(CY), x2="20", y2=str(CY),
     stroke=DIM_CYAN, stroke_width="1", opacity="0.3")
emit("line", x1=str(W), y1=str(CY), x2=str(W-20), y2=str(CY),
     stroke=DIM_CYAN, stroke_width="1", opacity="0.3")
emit("line", x1=str(CX), y1="0", x2=str(CX), y2="20",
     stroke=DIM_CYAN, stroke_width="1", opacity="0.3")
emit("line", x1=str(CX), y1=str(H), x2=str(CX), y2=str(H-20),
     stroke=DIM_CYAN, stroke_width="1", opacity="0.3")

svg.append("</svg>")

# ---- Write Output ----
output_dir = "/root/jarvis-ai-assistent-for-android/docs/design"
os.makedirs(output_dir, exist_ok=True)
svg_path = os.path.join(output_dir, "brain-architecture.svg")
png_path = os.path.join(output_dir, "brain-architecture.png")

with open(svg_path, "w") as f:
    f.write("\n".join(svg))

print(f"SVG saved to {svg_path}")
print(f"File size: {os.path.getsize(svg_path)} bytes")
print(f"SVG lines: {len(svg)}")
