import streamlit as st
from brain import HeistBrain, ZONES

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