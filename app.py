import streamlit as st
import streamlit.components.v1 as components
import json
from brain import HeistBrain

st.set_page_config(page_title="Vegas Heist", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        header {
            visibility: hidden;
        }
        .element-container, .stIFrame, iframe {
            opacity: 1 !important;
            transition: none !important;
        }
        [data-testid="stVerticalBlock"] {
            opacity: 1 !important;
        }
        [data-testid="stStatusWidget"] {
            visibility: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .stChatInputContainer > div {
            background-color: #09090b !important;
            border: 1px solid #a855f7 !important;
            border-radius: 8px !important;
        }
        .stChatInputContainer textarea {
            color: #22c55e !important;
        }
        .stChatInputContainer button {
            color: #a855f7 !important; 
        }
    </style>
""", unsafe_allow_html=True)

# --- FIX 1: Use cache_resource so HeistBrain is built ONCE and shared
# across all reruns and all users — not rebuilt every session.
@st.cache_resource
def get_brain():
    brain = HeistBrain()
    # FIX 2: Pre-warm the vectorstore at startup instead of lazy-loading
    # on the first message (which caused the noticeable first-message delay).
    brain.vectorstore = brain.vectorstore or __import__('langchain_chroma').Chroma(
        persist_directory=brain.db_path,
        embedding_function=brain.embeddings
    )
    return brain

# FIX 3: Cache the raw HTML file read — file I/O on every rerun is wasteful.
@st.cache_data
def get_ui_code():
    try:
        with open("interface.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

if "heat_level" not in st.session_state:
    st.session_state.heat_level = 0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

brain = get_brain()

user_move = st.chat_input("Enter your command...")

if user_move:
    st.session_state.chat_history.append({"role": "user", "content": user_move})

    loading_placeholder = st.empty()
    loading_placeholder.markdown("""
        <style>
            .cyber-loader-container {
                position: fixed;
                bottom: 100px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 999999;
            }
            .cyber-loader {
                border: 1px solid #b400ff;
                padding: 12px 30px;
                background: rgba(10, 8, 20, 0.9);
                backdrop-filter: blur(5px);
                color: #00d4ff;
                font-family: 'Share Tech Mono', monospace;
                letter-spacing: 3px;
                font-size: 14px;
                border-radius: 4px;
                box-shadow: 0 0 15px rgba(180,0,255,0.4);
                animation: neonPulse 1.2s infinite;
            }
            @keyframes neonPulse {
                0% { opacity: 0.8; box-shadow: 0 0 10px rgba(180,0,255,0.3); }
                50% { opacity: 1; box-shadow: 0 0 25px rgba(180,0,255,0.8), inset 0 0 10px rgba(180,0,255,0.4); }
                100% { opacity: 0.8; box-shadow: 0 0 10px rgba(180,0,255,0.3); }
            }
        </style>
        <div class="cyber-loader-container">
            <div class="cyber-loader">
                <span style="color: #ff2d78;">//</span> ORACLE DECRYPTING...
            </div>
        </div>
    """, unsafe_allow_html=True)

    full_response = brain.play_move(user_move)
    loading_placeholder.empty()

    if "HEAT:" in full_response:
        parts = full_response.split("HEAT:")
        story_text = parts[0].strip()
        try:
            parsed_heat = int(parts[1].strip().split()[0])
            st.session_state.heat_level = min(100, st.session_state.heat_level + parsed_heat)
        except:
            st.session_state.heat_level = min(100, st.session_state.heat_level + 10)
    else:
        story_text = full_response
        st.session_state.heat_level = min(100, st.session_state.heat_level + 10)

    st.session_state.chat_history.append({"role": "assistant", "content": story_text})

ui_code = get_ui_code()
if not ui_code:
    st.error("Error: Could not find interface.html in this folder.")
    st.stop()

current_heat = st.session_state.heat_level

# FIX 4: Don't do string replacement on the HTML for heat —
# drive the heat purely via JS injection, keeping the cached
# HTML string untouched (so cache_data actually helps).
history_js = f"window.receiveFromPython({{type: 'heat_set', value: {current_heat}}});\n"

for msg in st.session_state.chat_history:
    safe_content = json.dumps(msg["content"])
    role_str = msg["role"]
    history_js += f"window.appendMessage('{role_str}', {safe_content}, 0);\n"

injection_script = f"""
<script>
    setTimeout(() => {{
        if(typeof hideWelcome === 'function') hideWelcome();
        {history_js}
        const anchor = document.getElementById('msg-anchor');
        if(anchor) anchor.scrollIntoView();
    }}, 50);
</script>
"""

components.html(ui_code + injection_script, height=750, scrolling=False)