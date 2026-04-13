import streamlit as st
from brain import HeistBrain, ZONES, ITEM_DEFINITIONS
from html import escape
import streamlit.components.v1 as components
import urllib.parse

# ── FUTURISTIC AVATARS — inline SVG data URIs ─────────────────────────────────
_ORACLE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#030918"/><polygon points="20,3 36,12 36,28 20,37 4,28 4,12" fill="none" stroke="#00d4ff" stroke-width="1.5"/><polygon points="20,8 31,14 31,26 20,32 9,26 9,14" fill="none" stroke="#00d4ff" stroke-width="0.6" opacity="0.4"/><circle cx="20" cy="20" r="6" fill="none" stroke="#00d4ff" stroke-width="1.5"/><circle cx="20" cy="20" r="2.5" fill="#00d4ff"/><line x1="20" y1="3" x2="20" y2="14" stroke="#00d4ff" stroke-width="1" opacity="0.7"/><line x1="20" y1="26" x2="20" y2="37" stroke="#00d4ff" stroke-width="1" opacity="0.7"/><line x1="4" y1="12" x2="14" y2="17" stroke="#00d4ff" stroke-width="0.8" opacity="0.5"/><line x1="36" y1="12" x2="26" y2="17" stroke="#00d4ff" stroke-width="0.8" opacity="0.5"/><line x1="4" y1="28" x2="14" y2="23" stroke="#00d4ff" stroke-width="0.8" opacity="0.5"/><line x1="36" y1="28" x2="26" y2="23" stroke="#00d4ff" stroke-width="0.8" opacity="0.5"/></svg>'
_USER_SVG   = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#1a0020"/><circle cx="20" cy="20" r="14" fill="none" stroke="#ff2d78" stroke-width="1.5"/><circle cx="20" cy="20" r="8" fill="none" stroke="#ff2d78" stroke-width="1" opacity="0.4"/><circle cx="20" cy="20" r="2.5" fill="#ff2d78"/><line x1="20" y1="4" x2="20" y2="11" stroke="#ff2d78" stroke-width="2.2"/><line x1="20" y1="29" x2="20" y2="36" stroke="#ff2d78" stroke-width="2.2"/><line x1="4" y1="20" x2="11" y2="20" stroke="#ff2d78" stroke-width="2.2"/><line x1="29" y1="20" x2="36" y2="20" stroke="#ff2d78" stroke-width="2.2"/><line x1="8" y1="8" x2="12" y2="12" stroke="#ff2d78" stroke-width="1" opacity="0.5"/><line x1="32" y1="8" x2="28" y2="12" stroke="#ff2d78" stroke-width="1" opacity="0.5"/><line x1="8" y1="32" x2="12" y2="28" stroke="#ff2d78" stroke-width="1" opacity="0.5"/><line x1="32" y1="32" x2="28" y2="28" stroke="#ff2d78" stroke-width="1" opacity="0.5"/></svg>'
ORACLE_AVATAR = "data:image/svg+xml," + urllib.parse.quote(_ORACLE_SVG)
USER_AVATAR   = "data:image/svg+xml," + urllib.parse.quote(_USER_SVG)

def render_start_screen():
    st.markdown("""
    <div style="text-align:center; padding:3rem 0 1rem 0;">
      <div style="font-family:'Orbitron',monospace; font-size:3rem; font-weight:900;
                  letter-spacing:0.25em;
                  background:linear-gradient(135deg,#ff2d78,#ffd700,#00d4ff);
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                  filter:drop-shadow(0 0 40px rgba(255,45,120,0.7));">
        VEGAS
      </div>

      <div style="font-family:'Orbitron',monospace; font-size:1.2rem; font-weight:700;
                  letter-spacing:0.5em; color:#ffd700;
                  margin-top:6px; text-shadow:0 0 20px rgba(255,215,0,0.7);">
        BLACK VAULT
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="max-width:700px; margin:auto; padding:20px;
                background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,45,120,0.3);
                border-radius:14px;
                box-shadow:0 0 40px rgba(255,45,120,0.15);">

      <div style="font-family:'Orbitron',monospace; font-size:0.8rem;
                  letter-spacing:0.2em; color:#00d4ff; margin-bottom:12px;">
        ◈ MISSION BRIEF
      </div>

      <div style="font-family:'Rajdhani',sans-serif; font-size:0.95rem;
                  color:rgba(220,220,255,0.8); line-height:1.6;">
        You are a professional heist planner tasked with infiltrating the
        <span style="color:#ffd700;">Velvet Ace Casino</span>.
        <br><br>
        Your objective:
        <br>• Acquire access credentials
        <br>• Breach underground security (B3)
        <br>• Reach the vault (B4)
        <br>• Extract high-value assets
        <br>• You can only scan or search for items once you're already inside that room.
        <br><br>
        Avoid detection. Minimize heat. Execute flawlessly.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        if st.button("◈ START HEIST", use_container_width=True):
            st.session_state.game_started = True
            st.rerun()

st.set_page_config(page_title="Vegas Black Vault", layout="wide", initial_sidebar_state="expanded")

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">

<style>
:root {
  --pink:    #ff2d78;
  --blue:    #00d4ff;
  --purple:  #8b2be2;
  --dpurple: #1a0533;
  --gold:    #ffd700;
  --black:   #06020f;
  --glass:   rgba(255,255,255,0.04);
  --glass2:  rgba(255,45,120,0.08);
}

#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stStatusWidget"] { visibility: hidden; }
[data-testid="stToolbarActions"] { visibility: hidden; }
header[data-testid="stHeader"] {
  background: transparent !important;
  box-shadow: none !important;
}
[data-testid="stSidebarCollapseButton"] button {
  background: rgba(255,45,120,0.15) !important;
  border: 1px solid rgba(255,45,120,0.5) !important;
  border-radius: 6px !important;
  color: #ff2d78 !important;
}
[data-testid="stSidebarCollapsedControl"] {
  visibility: visible !important;
  display: flex !important;
  background: rgba(255,45,120,0.15) !important;
  border: 1px solid rgba(255,45,120,0.5) !important;
  border-radius: 6px !important;
}
[data-testid="stSidebarCollapsedControl"] button { visibility: visible !important; color: #ff2d78 !important; }
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg { fill: #ff2d78 !important; }

.stApp {
  background: var(--black) !important;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(139,43,226,0.35) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 90% 90%, rgba(0,212,255,0.15) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 10% 80%, rgba(255,45,120,0.12) 0%, transparent 60%) !important;
  font-family: 'Rajdhani', sans-serif !important;
}
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(139,43,226,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139,43,226,0.06) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: gridScroll 20s linear infinite;
  pointer-events: none;
  z-index: 0;
}
@keyframes gridScroll {
  0%   { background-position: 0 0; }
  100% { background-position: 60px 60px; }
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0e0020 0%, #06020f 100%) !important;
  border-right: 1px solid rgba(139,43,226,0.4) !important;
  box-shadow: 4px 0 40px rgba(139,43,226,0.15) !important;
}
[data-testid="stSidebar"] > div { padding-top: 1rem !important; }

.main .block-container {
  padding: 0.5rem 2rem 1rem 2rem !important;
}

h1, h2, h3 { font-family: 'Orbitron', monospace !important; color: #fff !important; }

.stButton > button {
  background: linear-gradient(135deg, rgba(255,45,120,0.15), rgba(139,43,226,0.2)) !important;
  border: 1px solid rgba(255,45,120,0.6) !important;
  color: #ff2d78 !important;
  font-family: 'Orbitron', monospace !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.1em !important;
  border-radius: 6px !important;
  transition: all 0.25s ease !important;
  text-transform: uppercase !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, rgba(255,45,120,0.35), rgba(139,43,226,0.4)) !important;
  border-color: var(--pink) !important;
  box-shadow: 0 0 20px rgba(255,45,120,0.4), inset 0 0 20px rgba(255,45,120,0.05) !important;
  color: #fff !important;
}

[data-testid="stChatInput"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(0,212,255,0.4) !important;
  border-radius: 12px !important;
  box-shadow: 0 0 20px rgba(0,212,255,0.1), inset 0 0 30px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: #e0f0ff !important;
  font-family: 'Share Tech Mono', monospace !important;
  font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: rgba(0,212,255,0.4) !important; }

[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }

[data-testid="stExpander"] {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid rgba(139,43,226,0.3) !important;
  border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
  color: rgba(200,180,255,0.9) !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-weight: 600 !important;
}

[data-testid="stToast"] {
  background: rgba(255,215,0,0.12) !important;
  border: 1px solid rgba(255,215,0,0.5) !important;
  color: #ffd700 !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(139,43,226,0.5); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── ANIMATED BACKGROUND ────────────────────────────────────────────────────────
def render_bg():
    components.html("""
    <style>
      body { margin:0; overflow:hidden; background:transparent; }
      canvas { position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:-1; opacity:0.35; }
    </style>
    <canvas id="c"></canvas>
    <script>
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    let W, H, buildings=[], particles=[];
    function resize(){ W=c.width=window.innerWidth; H=c.height=window.innerHeight; init(); }
    function randBetween(a,b){ return a+Math.random()*(b-a); }
    function init(){
      buildings=[];
      const count = Math.floor(W/38);
      for(let i=0;i<count;i++){
        const w=randBetween(22,55), h=randBetween(60,H*0.52), x=i*(W/count)+randBetween(-4,4);
        buildings.push({x,w,h,windows:Array.from({length:Math.floor(h/18)},()=>({
          on:Math.random()>0.35,
          color:Math.random()<0.5?'#ff2d78':Math.random()<0.5?'#00d4ff':'#ffd700',
          flicker:Math.random()<0.06
        }))});
      }
      particles=[];
      for(let i=0;i<60;i++) particles.push({
        x:Math.random()*W,y:Math.random()*H,r:randBetween(0.5,2.5),
        vx:randBetween(-0.3,0.3),vy:randBetween(-0.6,-0.1),
        color:['#ff2d78','#00d4ff','#8b2be2','#ffd700'][Math.floor(Math.random()*4)],
        alpha:randBetween(0.2,0.8)
      });
    }
    function drawSkyline(){
      const grd=ctx.createLinearGradient(0,H*0.48,0,H);
      grd.addColorStop(0,'rgba(139,43,226,0.22)'); grd.addColorStop(0.4,'rgba(255,45,120,0.08)'); grd.addColorStop(1,'rgba(6,2,15,0)');
      ctx.fillStyle=grd; ctx.fillRect(0,H*0.48,W,H*0.52);
      buildings.forEach(b=>{
        const top=H-b.h;
        const bg=ctx.createLinearGradient(b.x,top,b.x+b.w,top);
        bg.addColorStop(0,'rgba(20,5,40,0.92)'); bg.addColorStop(1,'rgba(10,2,25,0.92)');
        ctx.fillStyle=bg; ctx.fillRect(b.x,top,b.w,b.h);
        ctx.strokeStyle='rgba(139,43,226,0.25)'; ctx.lineWidth=0.5; ctx.strokeRect(b.x,top,b.w,b.h);
        b.windows.forEach((win,i)=>{
          if(win.flicker&&Math.random()<0.02) win.on=!win.on;
          if(!win.on) return;
          const wy=top+8+i*16, cols=Math.floor(b.w/12);
          for(let col=0;col<cols;col++){
            ctx.fillStyle=win.color; ctx.globalAlpha=0.6+Math.random()*0.3;
            ctx.shadowColor=win.color; ctx.shadowBlur=6;
            ctx.fillRect(b.x+4+col*11,wy,6,8);
          }
        });
        ctx.globalAlpha=1; ctx.shadowBlur=0;
      });
    }
    function drawParticles(){
      particles.forEach(p=>{
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle=p.color; ctx.globalAlpha=p.alpha*(0.6+0.4*Math.sin(Date.now()*0.003+p.x));
        ctx.shadowColor=p.color; ctx.shadowBlur=8; ctx.fill();
        ctx.globalAlpha=1; ctx.shadowBlur=0;
        p.x+=p.vx; p.y+=p.vy;
        if(p.y<-5){p.y=H+5;p.x=Math.random()*W;} if(p.x<0)p.x=W; if(p.x>W)p.x=0;
      });
    }
    function loop(){ ctx.clearRect(0,0,W,H); drawSkyline(); drawParticles(); requestAnimationFrame(loop); }
    window.addEventListener('resize',resize); resize(); loop();
    </script>
    """, height=0)

render_bg()


# ── CURSOR GRID EFFECT ─────────────────────────────────────────────────────────
components.html("""
<script>
(function() {
  var pdoc = window.parent.document;

  /* Remove any stale canvas from a previous Streamlit hot-reload */
  var old = pdoc.getElementById('vbv-cursor-grid');
  if (old) old.remove();

  /* Create canvas directly in parent body */
  var canvas = pdoc.createElement('canvas');
  canvas.id = 'vbv-cursor-grid';
  canvas.style.cssText = [
    'position:fixed', 'top:0', 'left:0',
    'width:100vw', 'height:100vh',
    'pointer-events:none',
    'z-index:99999',
    'display:block'
  ].join(';');
  pdoc.body.appendChild(canvas);

  var ctx = canvas.getContext('2d');
  var CELL = 36;
  var cells = {};

  function resize() {
    canvas.width  = window.parent.innerWidth;
    canvas.height = window.parent.innerHeight;
  }

  function onMove(e) {
    var col = Math.floor(e.clientX / CELL);
    var row = Math.floor(e.clientY / CELL);
    var key = col + '_' + row;
    cells[key] = { x: col * CELL, y: row * CELL, alpha: 1.0 };

    var nb = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];
    for (var i = 0; i < nb.length; i++) {
      var nc = col + nb[i][0], nr = row + nb[i][1];
      var nk = nc + '_' + nr;
      if (!cells[nk] || cells[nk].alpha < 0.35)
        cells[nk] = { x: nc * CELL, y: nr * CELL, alpha: 0.35 };
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    var keys = Object.keys(cells);
    for (var i = keys.length - 1; i >= 0; i--) {
      var k = keys[i], c = cells[k];
      if (c.alpha <= 0.004) { delete cells[k]; continue; }

      ctx.globalAlpha = c.alpha * 0.18;
      ctx.fillStyle   = '#ff2d78';
      ctx.fillRect(c.x, c.y, CELL, CELL);

      ctx.globalAlpha  = c.alpha * 0.65;
      ctx.strokeStyle  = '#ff2d78';
      ctx.lineWidth    = 1;
      ctx.shadowColor  = '#ff2d78';
      ctx.shadowBlur   = 12 * c.alpha;
      ctx.strokeRect(c.x + 0.5, c.y + 0.5, CELL - 1, CELL - 1);
      ctx.shadowBlur   = 0;
      ctx.globalAlpha  = 1;

      c.alpha *= 0.88;
    }
    requestAnimationFrame(draw);
  }

  resize();
  pdoc.addEventListener('mousemove', onMove);
  window.parent.addEventListener('resize', resize);
  draw();
})();
</script>
""", height=0)


# ── BRAIN ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_brain() -> HeistBrain:
    brain = HeistBrain()
    try:
        from langchain_chroma import Chroma
        brain.vectorstore = Chroma(
            persist_directory=brain.db_path,
            embedding_function=brain.embeddings
        )
    except Exception:
        pass
    return brain

brain = get_brain()

ZONE_ICONS = {
    "LOBBY": "🏨", "CASINO": "🎰", "CASHIER_CAGE": "💰",
    "KITCHEN_L2": "🍳", "HVAC_SHAFT": "🌀",
    "B3_CORRIDOR": "🔐", "SURVEILLANCE_HQ": "📹",
    "SECURITY_COMMAND": "📡",
    "STAFF_ELEVATOR": "🛗", "VAULT_ELEVATOR": "🛗", "B4_VAULT_ANTECHAMBER": "🚪", "VAULT_CHAMBER": "💎",
}

ITEM_ICONS = {
    "B3_KEYCARD": "💳", "VAULT_PIN": "🔢",
    "VAULT_KEYS": "🗝️", "CAMERA_LOOP_DEVICE": "📷",
    "SENSORS_DISABLED": "🔕",
}

ZONE_TO_FLOOR = {
    "LOBBY": "L1", "CASINO": "L0", "CASHIER_CAGE": "L0",
    "KITCHEN_L2": "L2", "HVAC_SHAFT": "TRANSIT",
    "B3_CORRIDOR": "B3", "SURVEILLANCE_HQ": "B3",
    "SECURITY_COMMAND": "B3",
    "STAFF_ELEVATOR": "TRANSIT",
    "VAULT_ELEVATOR": "B3", "B4_VAULT_ANTECHAMBER": "B4", "VAULT_CHAMBER": "B4",
}

# ── FLOOR MAP DATA ─────────────────────────────────────────────────────────────
_B3_GRID = [
    ["X","SURVEILLANCE_HQ","SURVEILLANCE_HQ","X","SECURITY_COMMAND","X"],
    ["X","SURVEILLANCE_HQ","SURVEILLANCE_HQ","X","SECURITY_COMMAND","X"],
    ["X","B3_CORRIDOR","B3_CORRIDOR","B3_CORRIDOR","B3_CORRIDOR","X"],
    ["X","B3_CORRIDOR","B3_CORRIDOR","B3_CORRIDOR","B3_CORRIDOR","X"],
    ["X","STAFF_ELEVATOR","HVAC_SHAFT","B3_CORRIDOR","VAULT_ELEVATOR","X"],
    ["X","X","X","X","X","X"],
]

_CASINO_GRID = [
    ["X","X","X","X","X","X"],
    ["X","CASINO","CASINO","CASINO","CASINO","X"],
    ["X","CASINO","CASHIER_CAGE","CASINO","CASINO","X"],
    ["X","CASINO","CASINO","CASINO","CASINO","X"],
    ["X","CASINO","KITCHEN_L2","CASINO","CASINO","X"],
    ["X","X","X","X","X","X"],
]

FLOOR_GRIDS = {
    "LOBBY": {
        "title": "LEVEL 1 — LOBBY",
        "grid": [
            ["X","X","X","X","X"],
            ["X","LOBBY","LOBBY","LOBBY","X"],
            ["X","LOBBY","LOBBY","LOBBY","X"],
            ["X","LOBBY","LOBBY","LOBBY","X"],
            ["X","X","CASINO","X","X"],
        ],
    },
    "CASINO":     {"title": "GROUND FLOOR — CASINO",              "grid": _CASINO_GRID},
    "KITCHEN_L2": {"title": "GROUND FLOOR — CASINO",              "grid": _CASINO_GRID},
    "CASHIER_CAGE": {
        "title": "L0 — CASHIER CAGE",
        "grid": [
            ["X","CASINO","X"],
            ["X","CASHIER_CAGE","X"],
            ["X","CASHIER_CAGE","X"],
            ["X","STAFF_ELEVATOR","X"],
        ],
    },
    "STAFF_ELEVATOR": {
        "title": "STAFF SERVICE ELEVATOR",
        "grid": [
            ["X","CASHIER_CAGE","X"],
            ["X","STAFF_ELEVATOR","X"],
            ["X","STAFF_ELEVATOR","X"],
            ["X","B3_CORRIDOR","X"],
        ],
    },
    "HVAC_SHAFT": {
        "title": "HVAC VERTICAL SHAFT",
        "grid": [
            ["X","KITCHEN_L2","X"],
            ["X","HVAC_SHAFT","X"],
            ["X","HVAC_SHAFT","X"],
            ["X","B3_CORRIDOR","X"],
        ],
    },
    "B3_CORRIDOR":      {"title": "B3 — SECURITY CORE", "grid": _B3_GRID},
    "SURVEILLANCE_HQ":  {"title": "B3 — SECURITY CORE", "grid": _B3_GRID},
    "SECURITY_COMMAND": {"title": "B3 — SECURITY CORE", "grid": _B3_GRID},
    "VAULT_ELEVATOR":   {"title": "B3 — SECURITY CORE", "grid": _B3_GRID},
    "B4_VAULT_ANTECHAMBER": {
        "title": "B4 — VAULT LEVEL",
        "grid": [
            ["X","X","VAULT_CHAMBER","X","X"],
            ["X","B4_VAULT_ANTECHAMBER","B4_VAULT_ANTECHAMBER","B4_VAULT_ANTECHAMBER","X"],
            ["X","B4_VAULT_ANTECHAMBER","CORE","B4_VAULT_ANTECHAMBER","X"],
            ["X","VAULT_ELEVATOR","B4_VAULT_ANTECHAMBER","X","X"],
            ["X","X","X","X","X"],
        ],
    },
    "VAULT_CHAMBER": {
        "title": "B4 — VAULT LEVEL",
        "grid": [
            ["X","X","VAULT_CHAMBER","X","X"],
            ["X","B4_VAULT_ANTECHAMBER","B4_VAULT_ANTECHAMBER","B4_VAULT_ANTECHAMBER","X"],
            ["X","B4_VAULT_ANTECHAMBER","CORE","B4_VAULT_ANTECHAMBER","X"],
            ["X","VAULT_ELEVATOR","B4_VAULT_ANTECHAMBER","X","X"],
            ["X","X","X","X","X"],
        ],
    },
}


def _bubble_height(text: str, base: int = 90, chars_per_line: int = 80, line_h: int = 22) -> int:
    """Estimate iframe height needed for a chat bubble — avoids excess whitespace."""
    lines = max(1, len(text) // chars_per_line + text.count("\n"))
    return base + lines * line_h


def render_floor_map(zone_key: str):
    active_label = ZONES.get(zone_key, {}).get("label", zone_key)
    floor = FLOOR_GRIDS.get(zone_key)
    if not floor:
        return

    grid = floor["grid"]
    rows_count = len(grid)
    cols = len(grid[0]) if grid else 0
    cells = []

    def same_zone(r, c, r2, c2):
        """Return True if two cells belong to the same visual zone block."""
        if r2 < 0 or r2 >= rows_count or c2 < 0 or c2 >= cols:
            return False
        return grid[r][c] == grid[r2][c2] and grid[r][c] != "X"

    def is_you_cell(r, c):
        """True if this cell belongs to the player zone."""
        if r < 0 or r >= rows_count or c < 0 or c >= cols:
            return False
        return grid[r][c] == zone_key

    for ri, row in enumerate(grid):
        for ci, cell in enumerate(row):
            cell_value = cell

            if cell_value == "X":
                cls = "wall"
            elif cell_value == "CORE":
                cls = "core"
            elif cell_value == "ELEVATOR":
                cls = "elevator"
            elif cell_value in {"STAFF_ELEVATOR", "VAULT_ELEVATOR"}:
                cls = "staff_elevator"
            elif cell_value in {"HVAC_SHAFT", "B3_MAINTENANCE_SHAFT"}:
                cls = "shaft"
            elif cell_value == "VAULT_CHAMBER":
                cls = "vault"
            else:
                cls = "zone"

            label = "" if cell_value == "X" else cell_value.replace("_", " ")
            icon  = ZONE_ICONS.get(cell_value, "")

            # Show label/icon only on the top-left representative cell of merged block
            is_top  = not same_zone(ri, ci, ri - 1, ci)
            is_left = not same_zone(ri, ci, ri, ci - 1)
            show_content = (is_top and is_left) and cell_value != "X"

            # Compute neighbour merges (for zone border suppression)
            merge_top    = same_zone(ri, ci, ri - 1, ci)
            merge_bottom = same_zone(ri, ci, ri + 1, ci)
            merge_left   = same_zone(ri, ci, ri, ci - 1)
            merge_right  = same_zone(ri, ci, ri, ci + 1)

            # border-radius: only on outer corners
            def cr(t, l): return "0" if (t or l) else "10px"
            tl = cr(merge_top, merge_left)
            tr = cr(merge_top, merge_right)
            bl = cr(merge_bottom, merge_left)
            br = cr(merge_bottom, merge_right)
            radius_style = f"border-radius:{tl} {tr} {br} {bl};"

            # Suppress shared borders between same-zone cells
            bs = []
            if merge_top:    bs.append("border-top:none;")
            if merge_bottom: bs.append("border-bottom:none;")
            if merge_left:   bs.append("border-left:none;")
            if merge_right:  bs.append("border-right:none;")
            border_style = "".join(bs)

            # Margin gap only on outer edges (between different zones)
            gap = "2px"
            mt = "0" if merge_top    else gap
            mb = "0" if merge_bottom else gap
            ml = "0" if merge_left   else gap
            mr = "0" if merge_right  else gap
            margin_style = f"margin:{mt} {mr} {mb} {ml};"

            inline = radius_style + border_style + margin_style

            inner = (
                f'<span class="cell-icon">{icon}</span>'
                f'<span class="cell-label">{escape(label)}</span>'
            ) if show_content else ""

            # YOU highlighting: per-cell green border on exposed edges only.
            # Works for rectangles, L-shapes, and any irregular room geometry.
            you_overlay = ""
            if is_you_cell(ri, ci):
                # Which sides are exposed (not touching another YOU cell)?
                exp_top    = not is_you_cell(ri - 1, ci)
                exp_bottom = not is_you_cell(ri + 1, ci)
                exp_left   = not is_you_cell(ri, ci - 1)
                exp_right  = not is_you_cell(ri, ci + 1)

                # Build per-side border for the inset overlay div
                bw = "2px"
                green = "rgba(0,255,136,0.92)"
                none  = "none"
                bt = f"{bw} solid {green}" if exp_top    else none
                bb = f"{bw} solid {green}" if exp_bottom else none
                bl_s = f"{bw} solid {green}" if exp_left   else none
                br_s = f"{bw} solid {green}" if exp_right  else none

                # Corner radius on exposed outer corners only
                otl = "8px" if (exp_top and exp_left)    else "0"
                otr = "8px" if (exp_top and exp_right)   else "0"
                obl = "8px" if (exp_bottom and exp_left) else "0"
                obr = "8px" if (exp_bottom and exp_right) else "0"

                # Badge only on the top-left corner of the YOU region
                badge = ""
                if exp_top and exp_left:
                    badge = '<span class="you-badge">◈ YOU</span>'

                you_overlay = (
                    f'<div class="you-cell-hl" style="' 
                    f'border-top:{bt};border-bottom:{bb};' 
                    f'border-left:{bl_s};border-right:{br_s};' 
                    f'border-radius:{otl} {otr} {obr} {obl};">' 
                    f'{badge}</div>'
                )

            cells.append(
                f'<div class="cell {cls}" style="{inline}">' 
                f'{you_overlay}' 
                f'{inner}' 
                f'</div>'
            )

    st.markdown("""
    <div id="vbv-map-backdrop" style="
      position: fixed; inset: 0;
      background: rgba(6,2,15,0.88);
      backdrop-filter: blur(7px);
      -webkit-backdrop-filter: blur(7px);
      z-index: 998;
      transition: opacity 0.3s ease;
      display: none; opacity: 0;
    "></div>
    """, unsafe_allow_html=True)

    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <script>
    (function() {{
      var f = window.frameElement;
      if (!f) return;
      f.id = 'vbv-map-iframe';
      f.style.position='fixed'; f.style.top='50%'; f.style.height='88vh';
      f.style.border='none'; f.style.borderRadius='18px'; f.style.zIndex='999';
      f.style.boxShadow='0 0 80px rgba(255,45,120,0.4), 0 0 160px rgba(139,43,226,0.2)';
      f.style.opacity='0'; f.style.display='none';
      f.style.transition='left 0.3s ease, width 0.3s ease, opacity 0.25s ease';
      function recentre() {{
        var main = window.parent.document.querySelector('.main .block-container')
                || window.parent.document.querySelector('[data-testid="stMain"]')
                || window.parent.document.querySelector('.stMain');
        if (main) {{
          var rect=main.getBoundingClientRect(), cx=rect.left+rect.width/2, w=Math.min(rect.width*0.96,960);
          f.style.left=cx+'px'; f.style.width=w+'px'; f.style.transform='translate(-50%,-50%)';
        }} else {{
          f.style.left='50%'; f.style.width='min(94vw,960px)'; f.style.transform='translate(-50%,-50%)';
        }}
      }}
      recentre();
      var sidebar=window.parent.document.querySelector('[data-testid="stSidebar"]');
      if(sidebar) new MutationObserver(function(){{
        recentre();
        var t2=0, iv2=setInterval(function(){{ recentre(); if(++t2>10) clearInterval(iv2); }},50);
      }}).observe(sidebar,{{attributes:true,attributeFilter:['style','class']}});
      window.addEventListener('resize',recentre);
    }})();
    function closeMap() {{
      var f=window.parent.document.getElementById('vbv-map-iframe');
      var bd=window.parent.document.getElementById('vbv-map-backdrop');
      if(f)  {{ f.style.opacity='0';  setTimeout(function(){{ f.style.display='none'; }},260); }}
      if(bd) {{ bd.style.opacity='0'; setTimeout(function(){{ bd.style.display='none'; }},260); }}
    }}
    </script>
    <style>
    *,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
    html,body {{ width:100%; height:100%; background:linear-gradient(140deg,#0a001e 0%,#07020f 100%); font-family:'Share Tech Mono',monospace; overflow:hidden; }}
    .modal-wrap {{ width:100%; height:100%; display:flex; flex-direction:column; border:1px solid rgba(255,45,120,0.45); border-radius:18px; overflow:hidden; }}
    .modal-header {{ display:flex; align-items:center; justify-content:space-between; padding:14px 20px; flex-shrink:0; background:linear-gradient(90deg,rgba(255,45,120,0.1),rgba(139,43,226,0.12)); border-bottom:1px solid rgba(255,45,120,0.22); }}
    .modal-title {{ font-family:'Orbitron',monospace; font-size:0.82rem; font-weight:900; letter-spacing:0.2em; color:#ff2d78; text-shadow:0 0 16px rgba(255,45,120,0.9); }}
    .modal-sub {{ font-size:0.68rem; color:rgba(0,212,255,0.75); letter-spacing:0.07em; margin-top:3px; }}
    .close-btn {{ background:rgba(255,45,120,0.12); border:1px solid rgba(255,45,120,0.55); color:#ff2d78; border-radius:8px; padding:8px 18px; cursor:pointer; font-family:'Orbitron',monospace; font-size:0.65rem; font-weight:700; letter-spacing:0.15em; transition:all 0.2s ease; }}
    .close-btn:hover {{ background:rgba(255,45,120,0.3); box-shadow:0 0 20px rgba(255,45,120,0.45); color:#fff; border-color:#ff2d78; }}
    .modal-body {{ flex:1; overflow-y:auto; padding:18px 20px; }}
    .map-grid {{ display:grid; gap:0; grid-template-columns:repeat({cols},minmax(72px,1fr)); }}
    .cell {{ min-height:62px; border-radius:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:6px 4px; position:relative; }}
    .cell-icon {{ font-size:1rem; line-height:1.2; }}
    .cell-label {{ font-size:8.5px; font-weight:700; line-height:1.2; letter-spacing:0.04em; margin-top:3px; }}
    .wall           {{ background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.04); }}
    .zone           {{ background:rgba(0,212,255,0.08);  border:1px solid rgba(0,212,255,0.28);  color:#a0d8ef; }}
    .core           {{ background:rgba(255,215,0,0.12);  border:1px solid rgba(255,215,0,0.45);  color:#fef3c7; }}
    .elevator       {{ background:rgba(139,43,226,0.18); border:1px solid rgba(139,43,226,0.52); color:#e9d5ff; }}
    .staff_elevator {{ background:rgba(139,43,226,0.22); border:1px solid rgba(139,43,226,0.62); color:#f3e8ff; }}
    .shaft          {{ background:rgba(20,184,166,0.14); border:1px solid rgba(20,184,166,0.4);  color:#99f6e4; }}
    .vault          {{ background:rgba(255,215,0,0.18);  border:1px solid rgba(255,215,0,0.75);  color:#ffd700; animation:vaultGlow 2.5s ease-in-out infinite; }}
    @keyframes vaultGlow {{ 0%,100% {{ box-shadow:0 0 16px rgba(255,215,0,0.3); }} 50% {{ box-shadow:0 0 30px rgba(255,215,0,0.6); }} }}
    .legend {{ display:flex; gap:16px; flex-wrap:wrap; margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06); }}
    .leg {{ font-size:8.5px; letter-spacing:0.06em; opacity:0.7; }}
    .you-leg {{ color:#00ff88; }} .zone-leg {{ color:#00d4ff; }} .vault-leg {{ color:#ffd700; }} .elev-leg {{ color:#a78bfa; }} .shaft-leg {{ color:#2dd4bf; }}
    /* YOU: per-cell inset border overlay — works for any room shape */
    .you-cell-hl {{
      position:absolute; inset:0; pointer-events:none;
      background:rgba(0,255,136,0.07);
      animation:youPulse 2s ease-in-out infinite;
      z-index:5;
    }}
    @keyframes youPulse {{
      0%,100% {{ box-shadow:inset 0 0 10px rgba(0,255,136,0.15); }}
      50%      {{ box-shadow:inset 0 0 20px rgba(0,255,136,0.30); }}
    }}
    .you-badge {{
      position:absolute; top:4px; left:5px;
      font-size:6.5px; color:#00ff88; letter-spacing:0.08em;
      text-shadow:0 0 8px #00ff88; white-space:nowrap; z-index:6;
    }}
    </style>
    <div class="modal-wrap">
      <div class="modal-header">
        <div>
          <div class="modal-title">◈ TACTICAL MAP</div>
          <div class="modal-sub">{escape(floor["title"])} &nbsp;|&nbsp; POS: {escape(active_label)}</div>
        </div>
        <button class="close-btn" onclick="closeMap()">✕ &nbsp;CLOSE MAP</button>
      </div>
      <div class="modal-body">
        <div class="map-grid">{''.join(cells)}</div>
        <div class="legend">
          <span class="leg you-leg">◈ YOU</span>
          <span class="leg zone-leg">■ ZONE</span>
          <span class="leg vault-leg">◆ VAULT</span>
          <span class="leg elev-leg">▲ ELEVATOR</span>
          <span class="leg shaft-leg">≈ SHAFT</span>
        </div>
      </div>
    </div>
    """, height=1)


# ── SIDEBAR HUD ─────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:0.5rem 0 1.2rem 0;">
          <div style="font-family:'Orbitron',monospace; font-size:1.05rem; font-weight:900;
                      letter-spacing:0.18em; color:#ff2d78;
                      text-shadow:0 0 20px rgba(255,45,120,0.9),0 0 40px rgba(255,45,120,0.4);">
            VEGAS
          </div>
          <div style="font-family:'Orbitron',monospace; font-size:0.65rem; font-weight:700;
                      letter-spacing:0.35em; color:#ffd700;
                      text-shadow:0 0 12px rgba(255,215,0,0.7); margin-top:2px;">
            BLACK VAULT
          </div>
          <div style="width:60%; height:1px; background:linear-gradient(90deg,transparent,#ff2d78,transparent);
                      margin:10px auto 0 auto;"></div>
        </div>
        """, unsafe_allow_html=True)

        heat = st.session_state.heat_level
        heat_pct = min(heat / 100.0, 1.0)
        if heat < 30:
            bar_color = "#00d4ff"; glow = "rgba(0,212,255,0.6)"; label = "COLD"
        elif heat < 60:
            bar_color = "#ffd700"; glow = "rgba(255,215,0,0.6)"; label = "WARM"
        elif heat < 85:
            bar_color = "#ff6b35"; glow = "rgba(255,107,53,0.7)"; label = "HOT"
        else:
            bar_color = "#ff2d78"; glow = "rgba(255,45,120,0.9)"; label = "CRITICAL"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,45,120,0.2);
                    border-radius:12px; padding:14px 16px; margin-bottom:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-family:'Orbitron',monospace; font-size:0.6rem; font-weight:700;
                         letter-spacing:0.15em; color:rgba(255,150,150,0.8);">🔥 HEAT LEVEL</span>
            <span style="font-family:'Orbitron',monospace; font-size:0.65rem; font-weight:900;
                         color:{bar_color}; text-shadow:0 0 10px {glow};">{heat}% · {label}</span>
          </div>
          <div style="height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden;">
            <div style="height:100%; width:{heat_pct*100:.1f}%;
                        background:linear-gradient(90deg,{bar_color}88,{bar_color});
                        border-radius:4px; box-shadow:0 0 12px {glow},0 0 4px {glow};
                        transition:width 0.6s cubic-bezier(.4,0,.2,1);"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        zone_data = ZONES.get(st.session_state.zone, {})
        zone_icon = ZONE_ICONS.get(st.session_state.zone, "📍")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(139,43,226,0.12),rgba(0,212,255,0.06));
                    border:1px solid rgba(139,43,226,0.35); border-radius:12px;
                    padding:14px 16px; margin-bottom:14px;">
          <div style="font-family:'Orbitron',monospace; font-size:0.55rem; letter-spacing:0.18em;
                      color:rgba(200,150,255,0.7); margin-bottom:6px;">◈ CURRENT ZONE</div>
          <div style="font-size:1.3rem; margin-bottom:4px;">{zone_icon}</div>
          <div style="font-family:'Orbitron',monospace; font-size:0.75rem; font-weight:700;
                      color:#e0d0ff; letter-spacing:0.05em; margin-bottom:6px;">
            {escape(zone_data.get('label', st.session_state.zone))}
          </div>
          <div style="font-family:'Rajdhani',sans-serif; font-size:0.8rem; color:rgba(200,200,255,0.55);
                      font-style:italic; line-height:1.4;">
            {escape(zone_data.get('flavor', ''))}
          </div>
        </div>
        """, unsafe_allow_html=True)

        exits_str   = " · ".join(zone_data.get("exits",   [])) or "None"
        objects_str = " · ".join(zone_data.get("objects", [])) or "None"
        threats_str = " · ".join(zone_data.get("threats", [])) or "None"

        with st.expander("◈ ZONE SCANNER", expanded=True):
            st.markdown(f"""
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; line-height:1.8;">
              <div><span style="color:#00d4ff; letter-spacing:0.1em;">EXITS</span><br>
                   <span style="color:rgba(200,230,255,0.7);">{escape(exits_str)}</span></div>
              <div style="margin-top:8px;"><span style="color:#ffd700; letter-spacing:0.1em;">OBJECTS</span><br>
                   <span style="color:rgba(255,240,180,0.7);">{escape(objects_str)}</span></div>
              <div style="margin-top:8px;"><span style="color:#ff2d78; letter-spacing:0.1em;">THREATS</span><br>
                   <span style="color:rgba(255,180,200,0.7);">{escape(threats_str)}</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin:6px 0;'></div>", unsafe_allow_html=True)
        components.html("""
        <script>
        function vbvToggleMap() {
            var iframe = window.parent.document.getElementById('vbv-map-iframe');
            var backdrop = window.parent.document.getElementById('vbv-map-backdrop');
            if (!iframe || !backdrop) return;
            var isHidden = iframe.style.display === 'none' || iframe.style.display === '';
            if (isHidden) {
                iframe.style.display = 'block';
                backdrop.style.display = 'block';
                setTimeout(function(){ iframe.style.opacity='1'; backdrop.style.opacity='1'; }, 10);
            } else {
                iframe.style.opacity='0'; backdrop.style.opacity='0';
                setTimeout(function(){ iframe.style.display='none'; backdrop.style.display='none'; }, 260);
            }
        }
        </script>
        <button onclick="vbvToggleMap()" style="
            width:100%; padding:10px 16px; cursor:pointer;
            background:linear-gradient(135deg,rgba(255,45,120,0.15),rgba(139,43,226,0.2));
            border:1px solid rgba(255,45,120,0.6); border-radius:6px;
            color:#ff2d78; font-family:'Orbitron',monospace; font-size:0.7rem;
            font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
            transition:all 0.25s ease;">
            ◈ OPEN TACTICAL MAP
        </button>
        """, height=52)

        st.markdown("<div style='height:1px; background:linear-gradient(90deg,transparent,rgba(139,43,226,0.4),transparent); margin:14px 0;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Orbitron',monospace; font-size:0.58rem; font-weight:700;
                    letter-spacing:0.18em; color:rgba(200,150,255,0.7); margin-bottom:10px;">
          🎒 INTEL &amp; INVENTORY
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.inventory:
            for item in st.session_state.inventory:
                icon = ITEM_ICONS.get(item["key"], "◈")
                desc = ITEM_DEFINITIONS.get(item["key"], {}).get("desc", "")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(255,215,0,0.07),rgba(255,215,0,0.02));
                            border:1px solid rgba(255,215,0,0.3); border-radius:9px;
                            padding:10px 12px; margin-bottom:8px;">
                  <div style="font-size:1rem; margin-bottom:4px;">{icon}</div>
                  <div style="font-family:'Orbitron',monospace; font-size:0.62rem; font-weight:700;
                              color:#ffd700; letter-spacing:0.05em;">{escape(item['label'])}</div>
                  <div style="font-family:'Rajdhani',sans-serif; font-size:0.72rem;
                              color:rgba(255,215,0,0.5); margin-top:3px; line-height:1.3;">
                    {escape(desc)}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem;
                        color:rgba(255,255,255,0.2); text-align:center; padding:12px 0;">
              — empty —
            </div>
            """, unsafe_allow_html=True)


# ── STATE INIT ──────────────────────────────────────────────────────────────────
if "show_map"    not in st.session_state: st.session_state.show_map    = False
if "heat_level"  not in st.session_state: st.session_state.heat_level  = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "You're on the Casino Floor — 150,000 sq ft of noise and distraction. The Cashier Cage is straight ahead. Give your orders, Mastermind.", "heat_delta": 0}]
if "inventory"   not in st.session_state: st.session_state.inventory   = []
if "zone"        not in st.session_state: st.session_state.zone        = "CASINO"
if "game_over"   not in st.session_state: st.session_state.game_over   = False
if "victory"     not in st.session_state: st.session_state.victory     = False
if "game_started" not in st.session_state:
    st.session_state.game_started = False

brain.current_zone = st.session_state.zone
brain.inventory    = [item["key"] for item in st.session_state.inventory]
brain.heat         = st.session_state.heat_level
brain.game_over    = st.session_state.game_over
brain.victory      = st.session_state.victory

if not st.session_state.game_started:
    st.markdown("""
<style>
/* Remove default markdown block styling */
.block-container {
    padding-top: 2rem !important;
}

/* Remove grey box effect */
div[data-testid="stMarkdownContainer"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)
    render_start_screen()
    st.stop()

render_sidebar()


# ── MAIN HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:1.2rem 0 0.5rem 0; position:relative;">
  <div style="font-family:'Orbitron',monospace; font-size:2.4rem; font-weight:900;
              letter-spacing:0.25em; line-height:1;
              background:linear-gradient(135deg,#ff2d78 0%,#ff6b9d 30%,#ffd700 60%,#ff2d78 100%);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
              filter:drop-shadow(0 0 30px rgba(255,45,120,0.6));
              animation:titlePulse 4s ease-in-out infinite;">
    VEGAS
  </div>
  <div style="font-family:'Orbitron',monospace; font-size:0.95rem; font-weight:700;
              letter-spacing:0.55em; color:#ffd700;
              text-shadow:0 0 20px rgba(255,215,0,0.8),0 0 40px rgba(255,215,0,0.3); margin-top:4px;">
    BLACK VAULT
  </div>
  <div style="width:50%; height:1px; background:linear-gradient(90deg,transparent,#ff2d78,#ffd700,transparent);
              margin:12px auto 0 auto;"></div>
</div>
<style>
@keyframes titlePulse {
  0%,100% { filter:drop-shadow(0 0 30px rgba(255,45,120,0.6)); }
  50%      { filter:drop-shadow(0 0 50px rgba(255,45,120,0.9)) drop-shadow(0 0 80px rgba(255,215,0,0.3)); }
}
</style>
""", unsafe_allow_html=True)


# ── GAME OVER / VICTORY BANNERS ────────────────────────────────────────────────
if st.session_state.game_over:
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
    <div style="background:linear-gradient(135deg,rgba(255,0,60,0.15),rgba(80,0,0,0.25));
                border:2px solid rgba(255,45,120,0.7); border-radius:16px; padding:22px 28px;
                margin:16px 0; text-align:center;
                box-shadow:0 0 60px rgba(255,45,120,0.3),inset 0 0 40px rgba(255,0,0,0.05);
                animation:dangerPulse 1s ease-in-out infinite;">
      <div style="font-family:'Orbitron',monospace; font-size:1.5rem; font-weight:900;
                  color:#ff2d78; letter-spacing:0.2em; text-shadow:0 0 30px rgba(255,45,120,1);">
        🚨 OPERATIVE CAPTURED
      </div>
      <div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(255,150,150,0.7);
                  letter-spacing:0.25em; margin-top:8px;">
        MISSION COMPROMISED — REFRESH TO RESTART
      </div>
    </div>
    <style>
    @keyframes dangerPulse {
      0%,100% { border-color:rgba(255,45,120,0.7); box-shadow:0 0 60px rgba(255,45,120,0.3); }
      50%      { border-color:rgba(255,45,120,1);   box-shadow:0 0 90px rgba(255,45,120,0.6); }
    }
    </style>
    """, height=120)

elif st.session_state.victory:
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
    <div style="background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(0,80,0,0.1));
                border:2px solid rgba(255,215,0,0.8); border-radius:16px; padding:22px 28px;
                margin:16px 0; text-align:center;
                box-shadow:0 0 60px rgba(255,215,0,0.35),inset 0 0 40px rgba(255,215,0,0.04);
                animation:victoryPulse 2s ease-in-out infinite;">
      <div style="font-family:'Orbitron',monospace; font-size:1.5rem; font-weight:900;
                  color:#ffd700; letter-spacing:0.2em; text-shadow:0 0 30px rgba(255,215,0,1);">
        💎 THE VELVET ACE IS YOURS
      </div>
      <div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(255,215,100,0.7);
                  letter-spacing:0.25em; margin-top:8px;">
        EXTRACTION COMPLETE — MISSION SUCCESS
      </div>
    </div>
    <style>
    @keyframes victoryPulse {
      0%,100% { box-shadow:0 0 60px rgba(255,215,0,0.35); }
      50%      { box-shadow:0 0 100px rgba(255,215,0,0.65); }
    }
    </style>
    """, height=120)


# ── TACTICAL MAP MODAL (always rendered, shown/hidden via JS only) ─────────────
render_floor_map(st.session_state.zone)


# ── CHAT HISTORY ───────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar=ORACLE_AVATAR):
            content = msg["content"]
            components.html(f"""
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">
            <div style="background:linear-gradient(135deg,rgba(139,43,226,0.1),rgba(0,212,255,0.06));
                        border-left:3px solid rgba(0,212,255,0.7); border-radius:0 12px 12px 0;
                        padding:14px 18px; margin:2px 0; box-shadow:0 0 20px rgba(139,43,226,0.12);">
              <div style="font-family:'Orbitron',monospace; font-size:0.55rem; font-weight:700;
                          letter-spacing:0.2em; color:rgba(0,212,255,0.65); margin-bottom:8px;">
                ◈ ORACLE DISPATCH
              </div>
              <div style="font-family:'Rajdhani',sans-serif; font-size:1rem; color:#dde8ff;
                          line-height:1.65; letter-spacing:0.02em;">
                {escape(content)}
              </div>
              {f'<div style="margin-top:8px;"><span style="font-family:\'Orbitron\',monospace; font-size:0.6rem; color:#ff6b35; letter-spacing:0.1em; background:rgba(255,107,53,0.12); border:1px solid rgba(255,107,53,0.35); border-radius:4px; padding:2px 8px;">🔥 HEAT +{msg["heat_delta"]}</span></div>' if msg.get("heat_delta", 0) > 0 else ''}
            </div>
            """, height=_bubble_height(content))
    else:
        with st.chat_message("user", avatar=USER_AVATAR):
            content = msg["content"]
            components.html(f"""
            <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
            <div style="background:rgba(255,45,120,0.07); border-left:3px solid rgba(255,45,120,0.6);
                        border-radius:0 12px 12px 0; padding:12px 18px;
                        font-family:'Share Tech Mono',monospace; font-size:0.88rem;
                        color:rgba(255,200,220,0.9); letter-spacing:0.03em; line-height:1.5;">
              <span style="color:rgba(255,45,120,0.6); font-size:0.6rem; letter-spacing:0.2em;
                           display:block; margin-bottom:5px;">MASTERMIND INPUT</span>
              {escape(content)}
            </div>
            """, height=_bubble_height(content, base=70))


# ── CHAT INPUT ────────────────────────────────────────────────────────────────
user_move = st.chat_input("⟶  Transmit your next move to Oracle...")

if user_move and not st.session_state.game_over and not st.session_state.victory:
    st.session_state.chat_history.append({"role": "user", "content": user_move})

    with st.chat_message("user", avatar=USER_AVATAR):
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
        <div style="background:rgba(255,45,120,0.07); border-left:3px solid rgba(255,45,120,0.6);
                    border-radius:0 12px 12px 0; padding:12px 18px;
                    font-family:'Share Tech Mono',monospace; font-size:0.88rem;
                    color:rgba(255,200,220,0.9); letter-spacing:0.03em; line-height:1.5;">
          <span style="color:rgba(255,45,120,0.6); font-size:0.6rem; letter-spacing:0.2em;
                       display:block; margin-bottom:5px;">MASTERMIND INPUT</span>
          {escape(user_move)}
        </div>
        """, height=_bubble_height(user_move, base=70))

    with st.chat_message("assistant", avatar=ORACLE_AVATAR):
        with st.spinner("◈ Patching into Oracle frequency..."):
            result = brain.play_move(user_move)

        heat_badge = ""
        if result.get("heat_delta", 0) > 0:
            heat_badge = (
                f'<div style="margin-top:8px;">'
                f'<span style="font-family:\'Orbitron\',monospace; font-size:0.6rem; color:#ff6b35; '
                f'letter-spacing:0.1em; background:rgba(255,107,53,0.12); '
                f'border:1px solid rgba(255,107,53,0.35); border-radius:4px; padding:2px 8px;">'
                f'🔥 HEAT +{result["heat_delta"]}</span></div>'
            )

        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">
        <div style="background:linear-gradient(135deg,rgba(139,43,226,0.1),rgba(0,212,255,0.06));
                    border-left:3px solid rgba(0,212,255,0.7); border-radius:0 12px 12px 0;
                    padding:14px 18px; margin:2px 0; box-shadow:0 0 20px rgba(139,43,226,0.12);">
          <div style="font-family:'Orbitron',monospace; font-size:0.55rem; font-weight:700;
                      letter-spacing:0.2em; color:rgba(0,212,255,0.65); margin-bottom:8px;">
            ◈ ORACLE DISPATCH
          </div>
          <div style="font-family:'Rajdhani',sans-serif; font-size:1rem; color:#dde8ff;
                      line-height:1.65; letter-spacing:0.02em;">
            {escape(result['story'])}
          </div>
          {heat_badge}
        </div>
        """, height=_bubble_height(result['story']))

        event = result.get("event")
        if event:
            etype = event.get("type", "")
            emsg  = event.get("msg", "")
            if etype == "danger":
                color, glow, icon = "#ff2d78", "rgba(255,45,120,0.6)", "🚨"
            elif etype == "warning":
                color, glow, icon = "#ff6b35", "rgba(255,107,53,0.6)", "⚠️"
            else:
                color, glow, icon = "#ffd700", "rgba(255,215,0,0.6)", "✅"

            components.html(f"""
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
            <div style="margin-top:8px; background:rgba(0,0,0,0.3);
                        border:1px solid {color}80; border-radius:10px; padding:10px 16px;
                        box-shadow:0 0 20px {glow};
                        font-family:'Orbitron',monospace; font-size:0.65rem; font-weight:700;
                        color:{color}; letter-spacing:0.12em; text-align:center;
                        text-shadow:0 0 12px {glow};">
              {icon} {escape(emsg)}
            </div>
            """, height=56)

    st.session_state.chat_history.append({
        "role":       "assistant",
        "content":    result["story"],
        "heat_delta": result["heat_delta"],
    })
    st.session_state.heat_level = result["total_heat"]
    st.session_state.zone       = result["zone"]
    st.session_state.game_over  = result["game_over"]
    st.session_state.victory    = result["victory"]

    existing_keys = {i["key"] for i in st.session_state.inventory}
    for item in result["new_items"]:
        if item["key"] not in existing_keys:
            st.session_state.inventory.append(item)
            st.toast(f"◈ ACQUIRED: {item['label']}", icon="💰")

    st.rerun()