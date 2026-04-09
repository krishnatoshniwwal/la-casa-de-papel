import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Vegas Heist", layout="wide")
# --- HIDE STREAMLIT MARGINS ---
st.markdown("""
    <style>
        /* 1. Remove padding from the main block */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        /* 2. Hide the white Streamlit header at the very top */
        header {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        /* Target the Streamlit Chat Input Box */
        .stChatInputContainer > div {
            background-color: #09090b !important; /* Dark background */
            border: 1px solid #a855f7 !important; /* Purple neon border */
            border-radius: 8px !important;
        }
        
        /* Change the text color when you type */
        .stChatInputContainer textarea {
            color: #22c55e !important; /* Hacker green text */
        }
        
        /* Style the send arrow */
        .stChatInputContainer button {
            color: #a855f7 !important; 
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. INITIALIZE GAME MEMORY ---
if "heat_level" not in st.session_state:
    st.session_state.heat_level = 0
if "latest_ai_message" not in st.session_state:
    st.session_state.latest_ai_message = "Oracle Online. Awaiting your first move."

# --- 2. NATIVE INPUT (The safe way to talk to Python) ---
# We use Streamlit's native chat box to send messages TO Python
# because getting clicks OUT of a custom HTML iframe is notoriously buggy.
user_move = st.chat_input("Enter your command...")

if user_move:
    # --- MEMBER B's LOGIC GOES HERE ---
    # Example: response, heat_added = rag_engine.process(user_move)
    
    # For now, we simulate a response:
    st.session_state.latest_ai_message = f"Executing '{user_move}'... The system logs have been updated."
    st.session_state.heat_level += 5

# --- 3. LOAD THE HTML ---
try:
    with open("interface.html", "r", encoding="utf-8") as f:
        ui_code = f.read()
except FileNotFoundError:
    st.error("Error: Could not find interface.html in this folder.")
    st.stop()

# --- 4. THE ANTI-FLICKER INJECTION ---
current_heat = st.session_state.heat_level

# 1. We aggressively find the hardcoded "22" in your HTML and replace it with the REAL heat
ui_code = ui_code.replace("let heat         = 22;", f"let heat = {current_heat};")
ui_code = ui_code.replace('<div id="heat-value">22</div>', f'<div id="heat-value">{current_heat}</div>')
ui_code = ui_code.replace('style="width:22%"', f'style="width:{current_heat}%"')

# 2. We inject the JS payload (Without the 500ms delay, because the iframe is fresh anyway)
payload = {
    "type": "ai_response",
    "content": st.session_state.latest_ai_message,
    "heatDelta": 0 # We set this to 0 because we already hardcoded the new heat above!
}

import json
injection_script = f"""
<script>
    // Fire immediately upon load
    if (typeof window.receiveFromPython === 'function') {{
        window.receiveFromPython({json.dumps(payload)});
    }}
</script>
"""

# Glue them together
final_html = ui_code + injection_script

# --- 5. RENDER THE MASTERPIECE ---
components.html(final_html, height=750, scrolling=False) 
# Note: I changed height to 350 so it only shows the top dashboard, leaving room for the chat!