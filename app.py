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
    floor_key = floor_for_zone(zone_key)
    active_label = ZONES.get(zone_key, {}).get("label", zone_key)

    FLOOR_LAYOUTS = {
        "L1": {
            "title": "Level 1 — Hotel Lobby",
            "width": 420,
            "height": 220,
            "rooms": {
                "LOBBY": {"x": 110, "y": 60, "w": 200, "h": 90},
            },
            "links": [],
        },
        "L0": {
            "title": "Level 0 — Casino Floor",
            "width": 520,
            "height": 260,
            "rooms": {
                "CASINO": {"x": 40, "y": 70, "w": 240, "h": 120},
                "CASHIER_CAGE": {"x": 340, "y": 90, "w": 130, "h": 80},
            },
            "links": [("CASINO", "CASHIER_CAGE")],
        },
        "L2": {
            "title": "Level 2 — Kitchen",
            "width": 420,
            "height": 220,
            "rooms": {
                "KITCHEN_L2": {"x": 105, "y": 60, "w": 210, "h": 90},
            },
            "links": [],
        },
        "B2": {
            "title": "B2 — Parking / Engineering",
            "width": 460,
            "height": 240,
            "rooms": {
                "PARKING_B2": {"x": 90, "y": 65, "w": 260, "h": 100},
            },
            "links": [],
        },
        "TRANSIT": {
            "title": "Transit Routes",
            "width": 500,
            "height": 240,
            "rooms": {
                "STAFF_ELEVATOR": {"x": 60, "y": 70, "w": 150, "h": 90},
                "HVAC_SHAFT": {"x": 290, "y": 70, "w": 150, "h": 90},
            },
            "links": [("STAFF_ELEVATOR", "HVAC_SHAFT")],
        },
        "B3": {
            "title": "B3 — Operations",
            "width": 620,
            "height": 340,
            "rooms": {
                "SURVEILLANCE_HQ": {"x": 40, "y": 40, "w": 150, "h": 80},
                "SECURITY_COMMAND": {"x": 235, "y": 40, "w": 150, "h": 80},
                "COUNT_ROOM": {"x": 430, "y": 40, "w": 150, "h": 80},
                "B3_CORRIDOR": {"x": 170, "y": 145, "w": 280, "h": 60},
                "B3_MAINTENANCE_SHAFT": {"x": 50, "y": 240, "w": 180, "h": 70},
                "B3_ELEVATOR": {"x": 390, "y": 240, "w": 180, "h": 70},
            },
            "links": [
                ("SURVEILLANCE_HQ", "B3_CORRIDOR"),
                ("SECURITY_COMMAND", "B3_CORRIDOR"),
                ("COUNT_ROOM", "B3_CORRIDOR"),
                ("B3_MAINTENANCE_SHAFT", "B3_CORRIDOR"),
                ("B3_ELEVATOR", "B3_CORRIDOR"),
            ],
        },
        "B4": {
            "title": "B4 — Deep Vault",
            "width": 520,
            "height": 260,
            "rooms": {
                "B4_VAULT_ANTECHAMBER": {"x": 70, "y": 85, "w": 170, "h": 90},
                "VAULT_CHAMBER": {"x": 295, "y": 70, "w": 160, "h": 120},
            },
            "links": [("B4_VAULT_ANTECHAMBER", "VAULT_CHAMBER")],
        },
    }

    floor = FLOOR_LAYOUTS[floor_key]

    def center(room):
        return room["x"] + room["w"] / 2, room["y"] + room["h"] / 2

    svg_parts = [
        f'<rect x="0" y="0" width="{floor["width"]}" height="{floor["height"]}" rx="16" fill="#0a0f1a" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>'
    ]

    for x in range(0, floor["width"], 28):
        svg_parts.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{floor["height"]}" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>'
        )
    for y in range(0, floor["height"], 28):
        svg_parts.append(
            f'<line x1="0" y1="{y}" x2="{floor["width"]}" y2="{y}" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>'
        )

    for a, b in floor["links"]:
        ax, ay = center(floor["rooms"][a])
        bx, by = center(floor["rooms"][b])
        svg_parts.append(
            f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="rgba(125,211,252,0.45)" stroke-width="3" stroke-dasharray="8 6"/>'
        )

    for room_key, room in floor["rooms"].items():
        label = escape(ZONES.get(room_key, {}).get("label", room_key))
        is_active = room_key == zone_key
        fill = "rgba(34,197,94,0.18)" if is_active else "rgba(255,255,255,0.05)"
        stroke = "rgba(34,197,94,0.90)" if is_active else "rgba(255,255,255,0.14)"
        tag = "PLAYER POSITION" if is_active else "ZONE"

        svg_parts.append(
            f'''
            <rect x="{room["x"]}" y="{room["y"]}" width="{room["w"]}" height="{room["h"]}" rx="14"
                  fill="{fill}" stroke="{stroke}" stroke-width="2"/>
            <text x="{room["x"] + 12}" y="{room["y"] + 28}" fill="#e5eefc"
                  font-size="16" font-weight="700" font-family="Arial, sans-serif">{label}</text>
            <text x="{room["x"] + 12}" y="{room["y"] + 52}" fill="#93c5fd"
                  font-size="11" font-weight="600" font-family="Arial, sans-serif">{tag}</text>
            '''
        )

        if is_active:
            cx, cy = center(room)
            svg_parts.append(
                f'''
                <circle cx="{cx}" cy="{cy}" r="10" fill="rgba(34,197,94,0.28)" stroke="rgba(34,197,94,0.9)" stroke-width="2"/>
                <circle cx="{cx}" cy="{cy}" r="4" fill="rgba(34,197,94,1)"/>
                '''
            )

    html = f"""
    <div style="border:1px solid rgba(0,212,255,0.18);background:linear-gradient(180deg, rgba(9,12,24,0.98), rgba(18,12,28,0.98));border-radius:16px;padding:16px;margin:8px 0 18px 0;">
      <div style="color:#7dd3fc;font-weight:800;letter-spacing:.04em;margin-bottom:6px;font-size:1rem;">Tactical Map</div>
      <div style="color:#a78bfa;font-size:.88rem;margin-bottom:14px;">{escape(floor["title"])} | Current position: {escape(active_label)}</div>
      <svg width="100%" viewBox="0 0 {floor["width"]} {floor["height"]}" xmlns="http://www.w3.org/2000/svg">
        {''.join(svg_parts)}
      </svg>
    </div>
    """

    components.html(html, height=floor["height"] + 95, scrolling=False)





# --- STATE INIT ---
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

    render_floor_map(st.session_state.zone)
        
    st.divider()
        
    st.subheader("🎒 INTEL & INVENTORY")
    if st.session_state.inventory:
        for item in st.session_state.inventory:
            st.write(f"• **{item['label']}**")
    else:
        st.write("Empty")

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