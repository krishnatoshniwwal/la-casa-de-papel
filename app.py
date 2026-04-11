import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
from brain import HeistBrain, ZONES

st.set_page_config(page_title="Vegas Black Vault", layout="wide")

st.markdown("""
<style>
  .block-container { padding:0!important; max-width:100%!important; }
  header, footer, [data-testid="stStatusWidget"] { visibility:hidden!important; }
  .element-container, .stIFrame, iframe { opacity:1!important; transition:none!important; }
  [data-testid="stVerticalBlock"] { opacity:1!important; }
</style>
""", unsafe_allow_html=True)


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


@st.cache_data
def get_ui_code() -> str:
    try:
        with open("interface.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


defaults = {
    "heat_level":       0,
    "chat_history":     [],
    "inventory":        [],
    "zone":             "LOBBY",
    "zone_data":        ZONES["LOBBY"],
    "visited_zones":    ["LOBBY"],
    "game_over":        False,
    "victory":          False,
    "mission_accepted": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

brain = get_brain()
brain.current_zone = st.session_state.zone
brain.inventory    = [item["key"] for item in st.session_state.inventory]
brain.heat         = st.session_state.heat_level
brain.game_over    = st.session_state.game_over
brain.victory      = st.session_state.victory

# ── Component Listener ───────────────────────────────────────────────────────
# The iframe's sendToPython() navigates the parent window to ?msg=<encoded text>,
# which Streamlit picks up via st.query_params on the next run.
# We decode it, process the move, clear the param, and the re-render fires
# the injected JS block that updates the iframe UI.
raw_msg = st.query_params.get("msg", "")
if raw_msg:
    # URL-decode in case the iframe percent-encoded the text
    try:
        user_move = urllib.parse.unquote(raw_msg)
    except Exception:
        user_move = raw_msg

    # Clear the query param immediately so a page refresh doesn't re-fire
    st.query_params.clear()

    if user_move and not st.session_state.game_over and not st.session_state.victory:
        st.session_state.chat_history.append({
            "role": "user", "content": user_move, "heat_delta": 0
        })
        result = brain.play_move(user_move)

        st.session_state.heat_level  = result["total_heat"]
        st.session_state.zone        = result["zone"]
        st.session_state.zone_data   = result["zone_data"]
        st.session_state.game_over   = result["game_over"]
        st.session_state.victory     = result["victory"]

        if result["zone"] not in st.session_state.visited_zones:
            st.session_state.visited_zones.append(result["zone"])

        existing_keys = {i["key"] for i in st.session_state.inventory}
        for item in result["new_items"]:
            if item["key"] not in existing_keys:
                st.session_state.inventory.append(item)

        st.session_state.chat_history.append({
            "role":       "assistant",
            "content":    result["story"],
            "heat_delta": result["heat_delta"],
            "event":      result.get("event"),
            "new_items":  result["new_items"],
            "zone":       result["zone"],
            "zone_data":  result["zone_data"],
        })


def build_js() -> str:
    """Build the JS injection block that syncs Python state into the iframe UI."""
    lines = []

    # Mission accepted flag
    accepted = "true" if st.session_state.mission_accepted else "false"
    lines.append(f"window._missionAccepted = {accepted};")
    lines.append("if(window._missionAccepted && typeof showGame==='function') showGame();")

    # Heat
    lines.append(
        f"window.receiveFromPython({{type:'heat_set', value:{st.session_state.heat_level}}});"
    )

    # Zone (always send real zone data, even on first load)
    zone_data = st.session_state.zone_data or ZONES.get(st.session_state.zone, {})
    zone_js = json.dumps({
        "zone":    st.session_state.zone,
        "label":   zone_data.get("label", st.session_state.zone),
        "exits":   zone_data.get("exits", []),
        "objects": zone_data.get("objects", []),
        "threats": zone_data.get("threats", []),
        "flavor":  zone_data.get("flavor", ""),
    })
    lines.append(f"window.receiveFromPython({{type:'zone_update', data:{zone_js}}});")

    # Visited zones for fog-of-war
    visited_js = json.dumps(st.session_state.visited_zones)
    lines.append(
        f"window.receiveFromPython({{type:'visited_zones', zones:{visited_js}}});"
    )

    # Inventory
    inv_js = json.dumps(st.session_state.inventory)
    lines.append(
        f"window.receiveFromPython({{type:'inventory_set', items:{inv_js}}});"
    )

    # Game over / victory
    if st.session_state.game_over:
        lines.append("window.receiveFromPython({type:'game_over'});")
    if st.session_state.victory:
        lines.append("window.receiveFromPython({type:'victory'});")

    # Replay full chat history (stateless re-render on each Streamlit run)
    if st.session_state.chat_history:
        lines.append("if(typeof hideWelcome==='function') hideWelcome();")

    for msg in st.session_state.chat_history:
        content    = json.dumps(msg["content"])
        role       = msg["role"]
        heat_delta = msg.get("heat_delta", 0)
        lines.append(
            f"window.appendMessage('{role}', {content}, {heat_delta});"
        )
        ev = msg.get("event")
        if ev:
            lines.append(
                f"window.receiveFromPython({{type:'event',"
                f" event:'{ev.get('type','warning')}',"
                f" msg:{json.dumps(ev.get('msg',''))},"
                f" heatDelta:{ev.get('heatDelta',0)}}});"
            )
        for item in msg.get("new_items", []):
            lines.append(
                f"window.receiveFromPython({{type:'intel_unlock', item:{json.dumps(item)}}});"
            )

    # Re-enable input after AI reply so user can type the next move
    if (st.session_state.chat_history
            and st.session_state.chat_history[-1]["role"] == "assistant"):
        lines.append("if(typeof setInputLock==='function') setInputLock(false);")

    # Scroll to the latest message
    lines.append(
        "const anchor=document.getElementById('msg-anchor');"
        " if(anchor) anchor.scrollIntoView();"
    )
    return "\n".join(lines)


# ── Render ───────────────────────────────────────────────────────────────────
ui_code = get_ui_code()
if not ui_code:
    st.error(
        "interface.html not found — make sure it lives in the same directory as app.py."
    )
    st.stop()

injection = f"<script>setTimeout(()=>{{ {build_js()} }}, 80);</script>"
components.html(ui_code + injection, height=780, scrolling=False)