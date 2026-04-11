import streamlit as st
from brain import HeistBrain, ZONES
from html import escape
import streamlit.components.v1 as components

st.set_page_config(page_title="Vegas Black Vault", layout="wide")

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

ZONE_TO_FLOOR = {
    "LOBBY": "L1",
    "CASINO": "L0",
    "CASHIER_CAGE": "L0",
    "KITCHEN_L2": "L2",
    "HVAC_SHAFT": "TRANSIT",
    "PARKING_B2": "B2",
    "STAFF_ELEVATOR": "TRANSIT",
    "B3_CORRIDOR": "B3",
    "SURVEILLANCE_HQ": "B3",
    "SECURITY_COMMAND": "B3",
    "COUNT_ROOM": "B3",
    "B3_MAINTENANCE_SHAFT": "B3",
    "B3_ELEVATOR": "B3",
    "B4_VAULT_ANTECHAMBER": "B4",
    "VAULT_CHAMBER": "B4",
}

FLOOR_MAPS = {
    "L1": {
        "title": "Level 1 — Hotel Lobby",
        "nodes": ["LOBBY"],
        "edges": [],
    },
    "L0": {
        "title": "Level 0 — Casino Floor",
        "nodes": ["CASINO", "CASHIER_CAGE"],
        "edges": [("CASINO", "CASHIER_CAGE")],
    },
    "L2": {
        "title": "Level 2 — Kitchen",
        "nodes": ["KITCHEN_L2"],
        "edges": [],
    },
    "B2": {
        "title": "B2 — Parking / Engineering",
        "nodes": ["PARKING_B2"],
        "edges": [],
    },
    "TRANSIT": {
        "title": "Transit Routes",
        "nodes": ["STAFF_ELEVATOR", "HVAC_SHAFT"],
        "edges": [("STAFF_ELEVATOR", "HVAC_SHAFT")],
    },
    "B3": {
        "title": "B3 — Operations",
        "nodes": [
            "SURVEILLANCE_HQ",
            "SECURITY_COMMAND",
            "COUNT_ROOM",
            "B3_CORRIDOR",
            "B3_MAINTENANCE_SHAFT",
            "B3_ELEVATOR",
        ],
        "edges": [
            ("SURVEILLANCE_HQ", "B3_CORRIDOR"),
            ("SECURITY_COMMAND", "B3_CORRIDOR"),
            ("COUNT_ROOM", "B3_CORRIDOR"),
            ("B3_MAINTENANCE_SHAFT", "B3_CORRIDOR"),
            ("B3_ELEVATOR", "B3_CORRIDOR"),
        ],
    },
    "B4": {
        "title": "B4 — Deep Vault",
        "nodes": ["B4_VAULT_ANTECHAMBER", "VAULT_CHAMBER"],
        "edges": [("B4_VAULT_ANTECHAMBER", "VAULT_CHAMBER")],
    },
}


def floor_for_zone(zone_key: str) -> str:
    return ZONE_TO_FLOOR.get(zone_key, "TRANSIT")


def render_floor_map(zone_key: str):
    active_label = ZONES.get(zone_key, {}).get("label", zone_key)

    FLOOR_GRIDS = {
        "LOBBY": {
            "title": "LEVEL 1 — LOBBY",
            "grid": [
                ["X", "X", "X", "X", "X"],
                ["X", "LOBBY", "LOBBY", "LOBBY", "X"],
                ["X", "LOBBY", "LOBBY", "LOBBY", "X"],
                ["X", "LOBBY", "LOBBY", "LOBBY", "X"],
                ["X", "X", "X", "X", "X"],
            ],
        },
        "CASINO": {
            "title": "GROUND FLOOR — CASINO",
            "grid": [
                ["X", "X", "X", "X", "X", "X", "X"],
                ["X", "CASINO", "CASINO", "CASINO", "CASINO", "CASINO", "X"],
                ["X", "CASINO", "CASINO", "CASINO", "CASINO", "CASINO", "X"],
                ["X", "CASINO", "CASHIER_CAGE", "CASINO", "STAFF_ELEVATOR", "CASINO", "X"],
                ["X", "CASINO", "CASINO", "CASINO", "CASINO", "CASINO", "X"],
                ["X", "CASINO", "KITCHEN_L2", "CASINO", "CASINO", "CASINO", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "KITCHEN_L2": {
            "title": "LEVEL 2 — KITCHEN",
            "grid": [
                ["X", "X", "X", "X", "X", "X"],
                ["X", "KITCHEN_L2", "KITCHEN_L2", "KITCHEN_L2", "KITCHEN_L2", "X"],
                ["X", "KITCHEN_L2", "KITCHEN_L2", "HVAC_SHAFT", "KITCHEN_L2", "X"],
                ["X", "KITCHEN_L2", "KITCHEN_L2", "KITCHEN_L2", "KITCHEN_L2", "X"],
                ["X", "KITCHEN_L2", "KITCHEN_L2", "KITCHEN_L2", "KITCHEN_L2", "X"],
                ["X", "X", "X", "X", "X", "X"],
            ],
        },
        "HVAC_SHAFT": {
            "title": "HVAC SYSTEM",
            "grid": [
                ["X", "HVAC_SHAFT", "X"],
                ["HVAC_SHAFT", "HVAC_SHAFT", "HVAC_SHAFT"],
                ["X", "HVAC_SHAFT", "X"],
            ],
        },
        "PARKING_B2": {
            "title": "B2 — PARKING",
            "grid": [
                ["X", "X", "X", "X", "X"],
                ["X", "PARKING_B2", "PARKING_B2", "STAFF_ELEVATOR", "X"],
                ["X", "PARKING_B2", "PARKING_B2", "PARKING_B2", "X"],
                ["X", "PARKING_B2", "PARKING_B2", "PARKING_B2", "X"],
                ["X", "X", "X", "X", "X"],
            ],
        },
        "STAFF_ELEVATOR": {
            "title": "TRANSIT — STAFF ELEVATOR",
            "grid": [
                ["X", "X", "X", "X", "X"],
                ["X", "PARKING_B2", "PARKING_B2", "STAFF_ELEVATOR", "X"],
                ["X", "CASINO", "CASINO", "STAFF_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "STAFF_ELEVATOR", "X"],
                ["X", "X", "X", "X", "X"],
            ],
        },
        "B3_CORRIDOR": {
            "title": "B3 — SECURITY CORE",
            "grid": [
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "SURVEILLANCE_HQ": {
            "title": "B3 — SECURITY CORE",
            "grid": [
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "SECURITY_COMMAND": {
            "title": "B3 — SECURITY CORE",
            "grid": [
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "COUNT_ROOM": {
            "title": "B3 — SECURITY CORE",
            "grid": [
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "B3_ELEVATOR": {
            "title": "B3 — SECURITY CORE",
            "grid": [
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "B3_MAINTENANCE_SHAFT": {
            "title": "B3 — SECURITY CORE",
            "grid": [
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "SURVEILLANCE_HQ", "X", "SECURITY_COMMAND", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "COUNT_ROOM", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_ELEVATOR", "X"],
                ["X", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_CORRIDOR", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X", "X", "X"],
            ],
        },
        "B4_VAULT_ANTECHAMBER": {
            "title": "B4 — VAULT LEVEL",
            "grid": [
                ["X", "X", "VAULT_CHAMBER", "X", "X"],
                ["X", "B4_VAULT_ANTECHAMBER", "B4_VAULT_ANTECHAMBER", "B4_VAULT_ANTECHAMBER", "X"],
                ["X", "B4_VAULT_ANTECHAMBER", "CORE", "B4_VAULT_ANTECHAMBER", "X"],
                ["X", "B3_ELEVATOR", "B4_VAULT_ANTECHAMBER", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X"],
            ],
        },
        "VAULT_CHAMBER": {
            "title": "B4 — VAULT LEVEL",
            "grid": [
                ["X", "X", "VAULT_CHAMBER", "X", "X"],
                ["X", "B4_VAULT_ANTECHAMBER", "B4_VAULT_ANTECHAMBER", "B4_VAULT_ANTECHAMBER", "X"],
                ["X", "B4_VAULT_ANTECHAMBER", "CORE", "B4_VAULT_ANTECHAMBER", "X"],
                ["X", "B3_ELEVATOR", "B4_VAULT_ANTECHAMBER", "B3_MAINTENANCE_SHAFT", "X"],
                ["X", "X", "X", "X", "X"],
            ],
        },
    }

    floor = FLOOR_GRIDS.get(zone_key)
    if not floor:
        st.info(f"No map available for {zone_key}")
        return

    grid = floor["grid"]
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    cells = []
    player_marked = False

    for row in grid:
        for cell in row:
            if cell == zone_key and not player_marked:
                cell_value = f"{cell} (YOU)"
                player_marked = True
            else:
                cell_value = cell
            if cell_value == "X":
                cls = "wall"
            elif cell_value.endswith(" (YOU)"):
                cls = "you"
            elif cell_value in {"CORE"}:
                cls = "core"
            elif cell_value in {"STAFF_ELEVATOR", "B3_ELEVATOR"}:
                cls = "elevator"
            elif cell_value in {"HVAC_SHAFT", "B3_MAINTENANCE_SHAFT"}:
                cls = "shaft"
            else:
                cls = "zone"
            label = cell_value.replace("_", " ")
            cells.append(f'<div class="cell {cls}">{escape(label)}</div>')

    html = f"""
    <div style="background:linear-gradient(180deg,#0b1020,#140f22);border:1px solid rgba(0,212,255,0.18);border-radius:16px;padding:16px;margin:8px 0 18px 0;">
      <div style="color:#7dd3fc;font-weight:800;font-size:1rem;margin-bottom:6px;">Tactical Map</div>
      <div style="color:#a78bfa;font-size:.88rem;margin-bottom:14px;">{escape(floor["title"])} | Current position: {escape(active_label)}</div>
      <div class="map-grid" style="grid-template-columns: repeat({cols}, minmax(82px, 1fr));">
        {''.join(cells)}
      </div>
    </div>

    <style>
      body {{
        margin: 0;
        background: transparent;
        font-family: Arial, sans-serif;
      }}
      .map-grid {{
        display: grid;
        gap: 8px;
      }}
      .cell {{
        min-height: 58px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 8px;
        font-size: 11px;
        font-weight: 700;
        line-height: 1.15;
        letter-spacing: .02em;
        border: 1px solid rgba(255,255,255,0.08);
      }}
      .cell.wall {{
        background: rgba(255,255,255,0.04);
        color: #55607a;
      }}
      .cell.zone {{
        background: rgba(59,130,246,0.14);
        color: #dbeafe;
        border-color: rgba(59,130,246,0.35);
      }}
      .cell.you {{
        background: rgba(34,197,94,0.22);
        color: #ecfdf5;
        border: 2px solid rgba(34,197,94,0.9);
        box-shadow: 0 0 18px rgba(34,197,94,0.2);
      }}
      .cell.core {{
        background: rgba(251,191,36,0.18);
        color: #fef3c7;
        border-color: rgba(251,191,36,0.45);
      }}
      .cell.elevator {{
        background: rgba(168,85,247,0.18);
        color: #f3e8ff;
        border-color: rgba(168,85,247,0.42);
      }}
      .cell.shaft {{
        background: rgba(20,184,166,0.18);
        color: #ccfbf1;
        border-color: rgba(20,184,166,0.45);
      }}
    </style>
    """

    components.html(html, height=max(460, 220 + rows * 100), scrolling=False)







# --- STATE INIT ---
if "show_map" not in st.session_state:
    st.session_state.show_map = False
if "heat_level" not in st.session_state:
    st.session_state.heat_level = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "You are in the Hotel Lobby. Give your orders, Mastermind."}]
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "zone" not in st.session_state:
    st.session_state.zone = "LOBBY"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "victory" not in st.session_state:
    st.session_state.victory = False

# Sync backend brain with Streamlit state
brain.current_zone = st.session_state.zone
brain.inventory = [item["key"] for item in st.session_state.inventory]
brain.heat = st.session_state.heat_level
brain.game_over = st.session_state.game_over
brain.victory = st.session_state.victory

# --- SIDEBAR HUD ---
with st.sidebar:
    st.title("📟 HEIST HUD")

    st.subheader("🔥 HEAT LEVEL")
    st.progress(min(st.session_state.heat_level / 100.0, 1.0))
    st.write(f"**Heat:** {st.session_state.heat_level}%")

    st.divider()

    st.subheader("📍 CURRENT ZONE")
    zone_data = ZONES.get(st.session_state.zone, {})
    st.write(f"**{zone_data.get('label', st.session_state.zone)}**")
    st.caption(zone_data.get("flavor", ""))

    with st.expander("Zone Scanner", expanded=True):
        st.write("**Exits:**", " · ".join(zone_data.get("exits", [])) or "None")
        st.write("**Objects:**", " · ".join(zone_data.get("objects", [])) or "None")
        st.write("**Threats:**", " · ".join(zone_data.get("threats", [])) or "None")

    if st.button("Open Tactical Map", use_container_width=True):
        st.session_state.show_map = True

    st.divider()

    st.subheader("🎒 INTEL & INVENTORY")
    if st.session_state.inventory:
        for item in st.session_state.inventory:
            st.write(f"• **{item['label']}**")
    else:
        st.write("Empty")

st.title("Vegas Black Vault")

if st.session_state.show_map:
    col1, col2 = st.columns([6, 1])

    with col1:
        st.subheader("Tactical Map")

    with col2:
        if st.button("Close Map", use_container_width=True):
            st.session_state.show_map = False
            st.rerun()

    render_floor_map(st.session_state.zone)


# --- MAIN CHAT AREA ---
st.title("Vegas Black Vault")

if st.session_state.game_over:
    st.error("🚨 GAME OVER. Operative captured. Refresh to restart.")
elif st.session_state.victory:
    st.success("💎 VICTORY. The Velvet Ace is yours.")

# Render previous messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("heat_delta", 0) > 0:
            st.caption(f"🔥 Heat +{msg['heat_delta']}")

# Input Field
user_move = st.chat_input("What is your next move?")

if user_move and not st.session_state.game_over and not st.session_state.victory:
    # 1. Show user message
    st.session_state.chat_history.append({"role": "user", "content": user_move})
    with st.chat_message("user"):
        st.write(user_move)
        
    # 2. Get AI GM response
    with st.chat_message("assistant"):
        with st.spinner("Oracle is processing..."):
            result = brain.play_move(user_move)
            st.write(result["story"])
            if result.get("heat_delta", 0) > 0:
                st.caption(f"🔥 Heat +{result['heat_delta']}")
    
    # 3. Save to state
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": result["story"],
        "heat_delta": result["heat_delta"]
    })
    st.session_state.heat_level = result["total_heat"]
    st.session_state.zone = result["zone"]
    st.session_state.game_over = result["game_over"]
    st.session_state.victory = result["victory"]
    
    # 4. Handle new inventory items
    existing_keys = {i["key"] for i in st.session_state.inventory}
    for item in result["new_items"]:
        if item["key"] not in existing_keys:
            st.session_state.inventory.append(item)
            st.toast(f"Acquired: {item['label']}!", icon="📦")
            
    # Force a rerun to update the sidebar HUD
    st.rerun()