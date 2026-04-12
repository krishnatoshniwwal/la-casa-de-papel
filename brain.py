import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ══════════════════════════════════════════════════════════════════════════════
# ZONE DEFINITIONS  — single source of truth for map, exits, objects, threats.
#
# CANONICAL WIN PATH:
#   LOBBY → CASINO → CASHIER_CAGE   (search → B3_KEYCARD + GUARD_SCHEDULE)
#   CASINO → KITCHEN_L2 → HVAC_SHAFT (search → MAINTENANCE_LOG)
#   HVAC_SHAFT → B3_MAINTENANCE_SHAFT → B3_CORRIDOR (needs B3_KEYCARD)
#   OR: CASINO → STAFF_ELEVATOR → B3_CORRIDOR (needs B3_KEYCARD)
#   B3_CORRIDOR → SURVEILLANCE_HQ   (search → CAMERA_LOOP_DEVICE + LASER_SPECS;
#                                    interact terminal → BIOMETRIC_BYPASS)
#   B3_CORRIDOR → SECURITY_COMMAND  (interact desk → VAULT_PIN)
#   B3_CORRIDOR → COUNT_ROOM        (search → KEY_ALPHA + KEY_BETA)
#   B3_ELEVATOR (needs B3_KEYCARD + BIOMETRIC_BYPASS) → B4_VAULT_ANTECHAMBER
#   B4_VAULT_ANTECHAMBER → VAULT_CHAMBER (needs VAULT_PIN + KEY_ALPHA + KEY_BETA)
# ══════════════════════════════════════════════════════════════════════════════

ZONES = {
    "LOBBY": {
        "label": "L1 — Hotel Lobby",
        "exits": ["CASINO", "PARKING_B2"],
        "objects": ["Reception desk", "Staff elevator panel", "Security camera cluster"],
        "threats": ["Emily Park (receptionist)", "2 plainclothes guards"],
        "required_items": [],
        "flavor": "The marble atrium hums with tourists, all oblivious."
    },
    "CASINO": {
        "label": "L0 — Casino Floor",
        "exits": ["LOBBY", "KITCHEN_L2", "STAFF_ELEVATOR", "CASHIER_CAGE"],
        "objects": ["620 cameras", "ATM cluster", "Slot machine bank", "Marcus Reed patrol path"],
        "threats": ["Marcus Reed (12-min patrol loop)", "Melissa Warburton (dealer, highly alert)"],
        "required_items": [],
        "flavor": "150,000 sq ft of distraction — the perfect cover."
    },
    "KITCHEN_L2": {
        "label": "L2 — Kitchen",
        "exits": ["CASINO", "HVAC_SHAFT"],
        "objects": ["Steam vents (camera blind spot)", "HVAC maintenance access panel", "Miguel Das cleaning cart"],
        "threats": ["Miguel Das (janitor, careless)"],
        "required_items": [],
        "flavor": "Steam and grease — and a 2-second camera gap no one bothered to fix."
    },
    # FIX #13: HVAC duct air is 22-24C. Human body is ~37C.
    # Thermal sensors safe range (26-28C) is irrelevant here — body heat WILL
    # be detectable. The threat is now accurate: move slowly to minimise the
    # thermal signature differential, not to stay "within a safe range".
    "HVAC_SHAFT": {
        "label": "HVAC Vertical Shaft",
        "exits": ["KITCHEN_L2", "B3_MAINTENANCE_SHAFT"],
        "objects": ["80x80 cm main duct", "Filter panel (20 sec to remove)", "Jorge Ramirez maintenance log"],
        "threats": [
            "Thermal sensors — duct air is 22-24C, body heat (~37C) is detectable; move slowly to minimise signature",
            "Movement creates noise audible from B3"
        ],
        "required_items": [],
        "flavor": "Dark, tight, and the only route that skips every checkpoint."
    },
    "PARKING_B2": {
        "label": "B2 — Parking / Engineering",
        "exits": ["LOBBY", "STAFF_ELEVATOR"],
        "objects": ["HVAC main panel", "Loading docks", "Luis Martinez guard post"],
        "threats": ["Luis Martinez (relaxed, slow response)"],
        "required_items": [],
        "flavor": "Underground concrete. Martinez hasn't moved in 40 minutes."
    },
    # FIX #12: Staff elevator requires NO keycard to ENTER the zone.
    # The keycard is checked only when selecting the B3 floor.
    # B3_CORRIDOR enforces B3_KEYCARD in its own required_items.
    # Entering the elevator cabin itself (e.g. from Casino or B2) is free.
    "STAFF_ELEVATOR": {
        "label": "Staff Elevator",
        "exits": ["CASINO", "PARKING_B2", "B3_CORRIDOR"],
        "objects": ["Keycard reader (B3 floor only)", "Floor selector panel"],
        "threats": ["B3 floor locked without keycard — other floors freely accessible"],
        "required_items": [],
        "flavor": "The panel glows. B3 needs a swipe — every other floor is open."
    },
    "CASHIER_CAGE": {
        "label": "L0 — Cashier Cage",
        "exits": ["CASINO"],
        "objects": [
            "Security terminal with guard schedules",
            "Rick Green rotation sheet",
            "Key lockbox on wall (contains B3 keycard)"
        ],
        "threats": ["2 armed cashier guards"],
        "required_items": [],
        "flavor": "Rows of cash behind thick glass. The keycard lockbox is right there on the wall."
    },
    "B3_CORRIDOR": {
        "label": "B3 — Central Corridor",
        "exits": ["SURVEILLANCE_HQ", "SECURITY_COMMAND", "COUNT_ROOM", "B3_ELEVATOR", "B3_MAINTENANCE_SHAFT"],
        "objects": ["Biometric gate (keycard + fingerprint)", "Laser grid emitters", "Maintenance shaft junction"],
        "threats": [
            "Rick Green (distracted, checks phone every 3-5 min)",
            "Laser grid IR — max safe speed 0.08 m/s, recalibrates every 12 min"
        ],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The spine of their operation. One distracted guard, a 12-minute recalibration window."
    },
    "SURVEILLANCE_HQ": {
        "label": "B3 — Surveillance HQ",
        "exits": ["B3_CORRIDOR"],
        "objects": [
            "Primary camera control terminal",
            "Camera loop device port",
            "Vault camera feed (B4)",
            "Eric Chen duty log",
            "Biometric records terminal (contains fingerprint data of all B4-authorised staff)"
        ],
        "threats": ["Eric Chen (technician, checks systems hourly)", "No windows, 24/7 staffed"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "1,240 eyes on a single screen. Kill this room and you're a ghost."
    },
    "SECURITY_COMMAND": {
        "label": "B3 — Security Command",
        "exits": ["B3_CORRIDOR"],
        "objects": [
            "Guard rotation board",
            "Radio dispatch unit",
            "Sensor control panel (disables B4 motion and thermal sensors)",
            "Desk with drawers (top drawer)"
        ],
        "threats": ["2 guards on rotation", "Radio check every 10 min"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The guards stare at monitors. Someone was very careless with the desk drawers."
    },
    # FIX #2 + #7: Both KEY_ALPHA and KEY_BETA are stored together in the
    # COUNT_ROOM lockbox — not in Security Command (which was wrong in the
    # original property_layout.txt). Objects and flavor updated accordingly.
    "COUNT_ROOM": {
        "label": "B3 — Count Room",
        "exits": ["B3_CORRIDOR"],
        "objects": [
            "Cash processing equipment",
            "Albert King timesheet",
            "Key lockbox on wall (contains Vault Key ALPHA and Vault Key BETA)"
        ],
        "threats": ["Albert King (vault staff, strict routine)", "2 armed escorts"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "Millions move through here daily. Both vault keys sit in the lockbox — unguarded between 03:00–03:15."
    },
    "B3_MAINTENANCE_SHAFT": {
        "label": "B3 — Maintenance Shaft",
        "exits": ["B3_CORRIDOR", "B4_VAULT_ANTECHAMBER", "HVAC_SHAFT"],
        "objects": ["Camera blind spot (confirmed)", "Vent connecting upward to HVAC shaft", "Biometric relay cable"],
        "threats": ["Thermal sensors — body heat detectable, move slowly"],
        "required_items": [],
        "flavor": "Not on any public schematic. Drops straight to the vault antechamber."
    },
    # FIX #4: Added B4_VAULT_ANTECHAMBER to exits. Previously missing,
    # making this zone a permanent dead end.
    "B3_ELEVATOR": {
        "label": "B3→B4 Secure Elevator",
        "exits": ["B3_CORRIDOR", "B4_VAULT_ANTECHAMBER"],
        "objects": ["Keycard reader", "Fingerprint scanner"],
        "threats": [
            "Keycard required",
            "Fingerprint scan required — must match an authorised staff member"
        ],
        "required_items": ["B3_KEYCARD", "BIOMETRIC_BYPASS"],
        "flavor": "One card, one print, one door. The bypass makes it a formality."
    },
    "B4_VAULT_ANTECHAMBER": {
        "label": "B4 — Vault Antechamber",
        "exits": ["B3_ELEVATOR", "B3_MAINTENANCE_SHAFT", "VAULT_CHAMBER"],
        "objects": [
            "Motion sensors (can be disabled from Security Command sensor panel)",
            "Thermal sensors (can be disabled from Security Command sensor panel)",
            "Vault door with dual keyhole",
            "Vault PIN keypad"
        ],
        "threats": [
            "Motion sensors — active unless disabled from Security Command",
            "Thermal sensors — active unless disabled from Security Command",
            "10-15 vault security staff patrolling B4"
        ],
        "required_items": [],
        "flavor": "20 meters underground. The vault door is the only thing between you and everything."
    },
    # FIX #1: Canonical win condition — VAULT_PIN + KEY_ALPHA + KEY_BETA.
    # All .txt documents have been updated to match this exactly.
    "VAULT_CHAMBER": {
        "label": "B4 — VAULT CHAMBER 🎯",
        "exits": ["B4_VAULT_ANTECHAMBER"],
        "objects": [
            "Diamonds", "Jewelry", "Gold bullion",
            "VIP collateral", "Rare collectibles", "10-20 storage chambers"
        ],
        "threats": ["Time-lock (20 sec open window)", "Alarm if weight sensors disturbed incorrectly"],
        "required_items": ["VAULT_PIN", "KEY_ALPHA", "KEY_BETA"],
        "flavor": "TARGET ACQUIRED. 20 seconds. Take only what you came for."
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ITEM DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
ITEM_DEFINITIONS = {
    "B3_KEYCARD": {
        "label": "B3 Keycard",
        "desc": "Grants access to all B3 zones via biometric gate or staff elevator B3 floor. Found in Cashier Cage lockbox."
    },
    "VAULT_PIN": {
        "label": "Vault PIN Code",
        "desc": "4-digit PIN for the B4 vault keypad. Written on a note hidden in Security Command desk top drawer."
    },
    "KEY_ALPHA": {
        "label": "Vault Key — ALPHA",
        "desc": "First of two physical keys required to open the vault door. Stored in Count Room lockbox."
    },
    "KEY_BETA": {
        "label": "Vault Key — BETA",
        "desc": "Second of two physical keys required to open the vault door. Stored alongside KEY_ALPHA in Count Room lockbox."
    },
    "BIOMETRIC_BYPASS": {
        "label": "Biometric Bypass",
        "desc": "Cloned fingerprint data extracted from the Surveillance HQ biometric records terminal. Allows solo B4 elevator access."
    },
    "CAMERA_LOOP_DEVICE": {
        "label": "Camera Loop Device",
        "desc": "Loops the B3/B4 camera feed for up to 3 minutes. Found in Surveillance HQ."
    },
    "GUARD_SCHEDULE": {
        "label": "Guard Rotation Sheet",
        "desc": "Exact shift times, break windows, and patrol loops for all B3 guards. Found in Cashier Cage."
    },
    "LASER_SPECS": {
        "label": "Laser Grid Specs",
        "desc": "Emitter positions, 12-min recalibration gaps, and edge vulnerabilities for the B3 laser grid. Found in Surveillance HQ."
    },
    "MAINTENANCE_LOG": {
        "label": "Ramirez Maintenance Log",
        "desc": "HVAC thermal data log — confirms body heat triggers sensors; recommends very slow movement. Found in HVAC Shaft."
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ZONE_ITEMS — items granted when player SEARCHES a zone.
# FIX #2:  KEY_BETA added to COUNT_ROOM.
# FIX #3:  BIOMETRIC_BYPASS removed (uses hint-then-act via KEY_ITEM_HINTS).
# FIX #8:  B3_KEYCARD and GUARD_SCHEDULE both in CASHIER_CAGE.
# FIX #10: This entire dict was missing — now restored.
# FIX #16: MAINTENANCE_LOG fully defined above and included here.
# ══════════════════════════════════════════════════════════════════════════════
ZONE_ITEMS = {
    "CASHIER_CAGE":    ["B3_KEYCARD", "GUARD_SCHEDULE"],
    "HVAC_SHAFT":      ["MAINTENANCE_LOG"],
    "SURVEILLANCE_HQ": ["CAMERA_LOOP_DEVICE", "LASER_SPECS"],
    "COUNT_ROOM":      ["KEY_ALPHA", "KEY_BETA"],
}

# ══════════════════════════════════════════════════════════════════════════════
# KEY_ITEM_HINTS — items requiring AI hint first, then player action.
# FIX #11: VAULT_PIN now reachable via desk-search mechanic.
# FIX #3:  BIOMETRIC_BYPASS now reachable via terminal-interaction mechanic.
# ══════════════════════════════════════════════════════════════════════════════
KEY_ITEM_HINTS = {
    "VAULT_PIN": {
        "zone": "SECURITY_COMMAND",
        "hint": (
            "HINT TO GM: The player is in Security Command. "
            "There is a sticky note with the 4-digit vault PIN tucked inside the top desk drawer. "
            "Drop a subtle atmospheric clue that the desk looks hastily used or that a drawer "
            "wasn't closed properly. Do NOT name the PIN or say directly what is inside. "
            "Do NOT award the item yet."
        ),
    },
    "BIOMETRIC_BYPASS": {
        "zone": "SURVEILLANCE_HQ",
        "hint": (
            "HINT TO GM: The player is in Surveillance HQ. "
            "The biometric records terminal holds fingerprint data for every B4-authorised staff member. "
            "Hint that the terminal seems to hold more than camera feeds — perhaps credentials or "
            "staff access records — without saying explicitly what can be extracted. "
            "Do NOT award the item yet."
        ),
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ITEM_TRIGGERS — explicit action phrases that grant items immediately.
# Deliberately specific so players must act, not just be nearby.
# KEY_BETA shares trigger phrases with KEY_ALPHA (both in same lockbox).
# ══════════════════════════════════════════════════════════════════════════════
ITEM_TRIGGERS = {
    "B3_KEYCARD": [
        "grab the keycard", "take the keycard", "pocket the keycard",
        "take the key card", "grab the key card",
        "take the badge", "grab the badge",
        "take the access card", "grab the access card",
        "open the lockbox", "grab from the lockbox",
    ],
    "VAULT_PIN": [
        "open the drawer", "check the drawer", "look in the drawer",
        "search the desk", "rifle through the desk",
        "grab the note", "take the note", "read the note",
        "grab the sticky note", "take the sticky note", "read the sticky note",
    ],
    "KEY_ALPHA": [
        "take both keys", "grab both keys",
        "take key alpha", "grab key alpha",
        "open the lockbox", "grab the keys from the lockbox",
        "take the keys", "grab the keys",
    ],
    "KEY_BETA": [
        "take both keys", "grab both keys",
        "take key beta", "grab key beta",
        "open the lockbox", "grab the keys from the lockbox",
        "take the keys", "grab the keys",
    ],
    "BIOMETRIC_BYPASS": [
        "access the terminal", "use the terminal", "hack the terminal",
        "clone the fingerprint", "extract the credentials",
        "download the credentials", "copy the biometric data",
        "extract fingerprint data", "clone fingerprint data",
        "download fingerprint", "access biometric records",
    ],
    "CAMERA_LOOP_DEVICE": [
        "grab the loop device", "take the loop device",
        "plug in the loop device", "loop the cameras",
        "loop the feed", "grab the device", "take the device",
    ],
    "GUARD_SCHEDULE": [
        "grab the schedule", "take the schedule",
        "take the rotation sheet", "grab the rotation sheet",
        "read the schedule", "grab the guard schedule",
    ],
    "LASER_SPECS": [
        "grab the laser specs", "take the laser specs",
        "read the laser specs", "take the specs", "grab the specs",
    ],
    "MAINTENANCE_LOG": [
        "grab the log", "take the log", "pick up the log",
        "read the log", "grab the maintenance log", "take the maintenance log",
        "pick up the maintenance log",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════════════════════════

def _extract_text(response) -> str:
    """Robustly extract plain text from any LangChain/Gemini response format."""
    content = response.content if hasattr(response, "content") else response
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(parts).strip()
    return str(content)


# ══════════════════════════════════════════════════════════════════════════════
# HEIST BRAIN
# ══════════════════════════════════════════════════════════════════════════════

class HeistBrain:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key,
            task_type="retrieval_document"
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0.75,
            max_retries=3,
            google_api_key=api_key
        )
        self.db_path = "./chroma_db"
        self.vectorstore = None
        self.current_zone = "LOBBY"
        self.inventory: list[str] = []
        self.intel_log: list[dict] = []
        self.heat = 0
        self.move_count = 0
        self.game_over = False
        self.victory = False

    def index_documents(self):
        loader = DirectoryLoader("./data", glob="./*.txt", loader_cls=TextLoader)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=50)
        final_docs = splitter.split_documents(docs)
        self.vectorstore = Chroma.from_documents(
            documents=final_docs,
            embedding=self.embeddings,
            persist_directory=self.db_path
        )

    def _load_vectorstore(self):
        if not self.vectorstore:
            self.vectorstore = Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embeddings
            )

    def _zone_data(self) -> dict:
        return ZONES.get(self.current_zone, {})

    # ── Item discovery: zone search ───────────────────────────────────────────
    # FIX #10: This method was entirely absent in the uploaded brain.py.
    def _check_zone_search(self, user_move: str) -> list[str]:
        """
        Grant findable items when the player searches the current zone.
        KEY_ITEM_HINTS items (VAULT_PIN, BIOMETRIC_BYPASS) are excluded —
        they require a hint-then-act flow.
        """
        SEARCH_VERBS = [
            "search", "scout", "look around", "examine", "check", "inspect",
            "sweep", "scan", "explore", "investigate", "case the", "survey",
            "recon", "look for", "hunt for", "ransack", "go through",
        ]
        if not any(v in user_move.lower() for v in SEARCH_VERBS):
            return []
        key_items = set(KEY_ITEM_HINTS.keys())
        granted = []
        for item_key in ZONE_ITEMS.get(self.current_zone, []):
            if item_key not in self.inventory and item_key not in key_items:
                granted.append(item_key)
        return granted

    # ── Item discovery: keyword triggers ─────────────────────────────────────
    def _check_item_triggers(self, user_move: str) -> list[str]:
        move_lower = user_move.lower()
        triggered = []
        for item_key, keywords in ITEM_TRIGGERS.items():
            if item_key not in self.inventory:
                for kw in keywords:
                    if kw in move_lower:
                        triggered.append(item_key)
                        break
        return triggered

    # ── Movement parsing ──────────────────────────────────────────────────────
    def _try_move(self, user_move: str) -> str | None:
        move_lower = user_move.lower()
        zone_hints = {
            "lobby":             "LOBBY",
            "casino":            "CASINO",
            "kitchen":           "KITCHEN_L2",
            "hvac":              "HVAC_SHAFT",
            "vent":              "HVAC_SHAFT",
            "duct":              "HVAC_SHAFT",
            "parking":           "PARKING_B2",
            "staff elevator":    "STAFF_ELEVATOR",
            "cashier":           "CASHIER_CAGE",
            "cage":              "CASHIER_CAGE",
            "b3 corridor":       "B3_CORRIDOR",
            "corridor":          "B3_CORRIDOR",
            "surveillance":      "SURVEILLANCE_HQ",
            "security command":  "SECURITY_COMMAND",
            "count room":        "COUNT_ROOM",
            "maintenance shaft": "B3_MAINTENANCE_SHAFT",
            "b3 elevator":       "B3_ELEVATOR",
            "secure elevator":   "B3_ELEVATOR",
            "antechamber":       "B4_VAULT_ANTECHAMBER",
            "vault antechamber": "B4_VAULT_ANTECHAMBER",
            "vault chamber":     "VAULT_CHAMBER",
            "vault":             "VAULT_CHAMBER",
            "b4":                "B4_VAULT_ANTECHAMBER",
            "b3":                "B3_CORRIDOR",
        }
        movement_verbs = [
            "move to", "go to", "enter", "head to", "proceed to", "sneak into",
            "climb into", "crawl into", "take the elevator", "walk to",
            "run to", "get to", "slip into", "drop into", "descend to",
        ]
        if not any(v in move_lower for v in movement_verbs):
            return None
        for hint, zone_key in zone_hints.items():
            if hint in move_lower:
                return zone_key
        return None

    # ── Access check ──────────────────────────────────────────────────────────
    def _can_enter(self, zone_key: str) -> tuple[bool, str]:
        zone = ZONES.get(zone_key, {})
        required = zone.get("required_items", [])
        missing = [r for r in required if r not in self.inventory]
        if missing:
            labels = [ITEM_DEFINITIONS.get(m, {}).get("label", m) for m in missing]
            return False, f"Access denied — you need: {', '.join(labels)}"
        return True, ""

    # ── Main game loop ────────────────────────────────────────────────────────
    def play_move(self, user_move: str) -> dict:
        if self.game_over:
            return self._dead_response()
        if self.victory:
            return self._victory_response()

        self._load_vectorstore()
        self.move_count += 1

        zone = self._zone_data()

        # ── Movement ──────────────────────────────────────────────────────────
        target_zone = self._try_move(user_move)
        blocked_msg = ""
        zone_changed = False

        if target_zone:
            if target_zone not in zone.get("exits", []) and target_zone != self.current_zone:
                blocked_msg = f"[NOT_CONNECTED: {target_zone} is not directly reachable from {self.current_zone}]"
            else:
                can_enter, reason = self._can_enter(target_zone)
                if can_enter:
                    self.current_zone = target_zone
                    zone = self._zone_data()
                    zone_changed = True
                else:
                    blocked_msg = f"[ACCESS_DENIED: {reason}]"

        # ── Item discovery (two-tier) ─────────────────────────────────────────
        zone_search_keys = self._check_zone_search(user_move)
        keyword_keys     = self._check_item_triggers(user_move)
        all_new_keys     = list(dict.fromkeys(zone_search_keys + keyword_keys))

        new_items: list[dict] = []
        for key in all_new_keys:
            if key not in self.inventory:
                defn = ITEM_DEFINITIONS.get(key, {})
                self.inventory.append(key)
                entry = {"key": key, "label": defn.get("label", key), "desc": defn.get("desc", "")}
                self.intel_log.append(entry)
                new_items.append(entry)

        # ── RAG context ───────────────────────────────────────────────────────
        try:
            relevant_docs = self.vectorstore.similarity_search(user_move, k=2)
            context = "\n---\n".join([d.page_content for d in relevant_docs])
        except Exception:
            context = "No additional classified security data retrieved."

        # ── Prompt assembly ───────────────────────────────────────────────────
        zone_summary = (
            f"CURRENT ZONE: {zone.get('label', self.current_zone)}\n"
            f"EXITS: {', '.join(zone.get('exits', []))}\n"
            f"OBJECTS: {', '.join(zone.get('objects', []))}\n"
            f"THREATS: {', '.join(zone.get('threats', []))}\n"
            f"PLAYER INVENTORY: {', '.join(self.inventory) if self.inventory else 'nothing'}\n"
        )

        new_items_note = ""
        if new_items:
            labels = [i["label"] for i in new_items]
            new_items_note = (
                f"\nPLAYER JUST ACQUIRED: {', '.join(labels)} — "
                f"weave this discovery naturally into the narration.\n"
            )

        key_item_note = ""
        for item_key, hint_data in KEY_ITEM_HINTS.items():
            if hint_data["zone"] == self.current_zone and item_key not in self.inventory:
                key_item_note += f"\n{hint_data['hint']}\n"
                break

        block_note = f"\nGM BLOCK: {blocked_msg}\n" if blocked_msg else ""

        # FIX #17: Single consistent story-length instruction — exactly 2 sentences.
        # FIX #9:  Heat scale clearly defined as integers in range -10 to 30 only.
        prompt = f"""
You are the Game Master of a noir heist thriller set in The Velvet Ace Casino, Las Vegas.
Narrate ONLY what is happening RIGHT NOW in the current zone.

═══ SECURITY FACTS (classified documents) ═══
{context}

═══ ZONE DATA ═══
{zone_summary}
{new_items_note}
{key_item_note}
{block_note}

═══ PLAYER MOVE ═══
{user_move}

═══ STRICT GM RULES ═══

1. Write EXACTLY 1 to 2 short sentences. Be incredibly concise, fast-paced, and punchy. Do not waste words.
2. Judge the move REALISTICALLY based on the security facts. Smart moves succeed. Stupid moves fail.
3. If GM BLOCK is set, narrate the failure naturally.
4. If player acquired new items, weave their discovery into the story.
5. Heat logic:
    Heat scale (-10 to 30):
    -10 to -1: Brilliant, reduces suspicion
    0: Idle / no risk
    1–5: Minor risk
    6–15: Noticeable/sloppy
    16–30: Reckless / near alarm
    50+: Extremely stupid move
    100: Deliberately reveals himself while in a sticky situation
    Rules:
    Don’t give 0 for risky moves
    Don’t over-penalize smart execution
6. After the narrative, output EXACTLY these tags on separate lines:
   HEAT
   LOCATION: [current zone key from the ZONES list, e.g. B3_CORRIDOR]
   STATUS: [one of: CLEAR | ALERTED | COMPROMISED | CAPTURED | VICTORY]

CRITICAL: Output ONLY the 3-sentence story followed by the 3 tags. Nothing else.

Example output format:
The vent grate yields without a sound, cold air rushing past your face as you drop into the maintenance shaft. Rick Green's flashlight sweeps right on schedule — 3 minutes, 12 seconds, just like the schedule said. You're in.
HEAT: 5
LOCATION: HVAC_SHAFT
STATUS: CLEAR
"""

        response = self.llm.invoke(prompt)
        raw = _extract_text(response)

        # ── Parse tags ────────────────────────────────────────────────────────
        lines = raw.strip().split("\n")
        tags: dict = {}
        story_lines: list[str] = []
        for line in lines:
            stripped = line.strip().replace("*", "")
            if stripped.startswith("HEAT:"):
                try:
                    tags["heat"] = int(stripped.split(":", 1)[1].strip().split()[0])
                except Exception:
                    tags["heat"] = 5
            elif stripped.startswith("LOCATION:"):
                tags["location"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("STATUS:"):
                tags["status"] = stripped.split(":", 1)[1].strip()
            else:
                story_lines.append(line)

        story = " ".join(" ".join(story_lines).split()).strip()
        status = tags.get("status", "CLEAR")
        gm_location = tags.get("location", self.current_zone)

        # Honour GM location only if zone is valid and we didn't already move.
        if gm_location in ZONES and not zone_changed:
            self.current_zone = gm_location

        # ── Heat calculation ──────────────────────────────────────────────────
        IDLE_PHRASES = [
            "wait", "do nothing", "stay", "look around", "think",
            "what should", "where am i", "what do i", "how do i",
            "check inventory", "check map", "what is", "what are",
        ]
        is_idle = any(phrase in user_move.lower() for phrase in IDLE_PHRASES)

        # FIX #9: Clamp to the declared range -10..30.
        heat_delta = max(-10, min(30, tags.get("heat", 5)))
        if is_idle:
            heat_delta = 0

        event = None
        if status == "CAPTURED":
            self.game_over = True
            heat_delta = 100
            event = {"type": "danger", "msg": "OPERATIVE DOWN — mission compromised", "heatDelta": 100}
        elif status == "VICTORY":
            self.victory = True
            event = {"type": "success", "msg": "TARGET SECURED — initiating extraction", "heatDelta": heat_delta}
        elif status == "COMPROMISED":
            heat_delta = min(heat_delta + 15, 30)
            event = {"type": "danger", "msg": "EXPOSURE — heat rising fast", "heatDelta": heat_delta}
        elif status == "ALERTED":
            heat_delta = min(heat_delta + 8, 25)
            event = {"type": "warning", "msg": "SECURITY ALERT — adapt your approach", "heatDelta": heat_delta}

        self.heat = max(0, min(100, self.heat + heat_delta))
        if self.heat >= 100 and not self.game_over:
            self.game_over = True
            event = {"type": "danger", "msg": "HEAT CRITICAL — operative burned, mission over", "heatDelta": 0}

        return {
            "story":      story,
            "heat_delta": heat_delta,
            "total_heat": self.heat,
            "zone":       self.current_zone,
            "zone_data":  ZONES.get(self.current_zone, {}),
            "new_items":  new_items,
            "event":      event,
            "game_over":  self.game_over,
            "victory":    self.victory,
            "tags":       tags,
        }

    def _dead_response(self) -> dict:
        return {
            "story":      "You're in a holding cell two floors below the casino, zip-tied to a chair. The Oracle's line is dead.",
            "heat_delta": 0,
            "total_heat": 100,
            "zone":       self.current_zone,
            "zone_data":  {},
            "new_items":  [],
            "event":      {"type": "danger", "msg": "OPERATIVE CAPTURED — GAME OVER", "heatDelta": 0},
            "game_over":  True,
            "victory":    False,
            "tags":       {},
        }

    def _victory_response(self) -> dict:
        return {
            "story":      "The vault is behind you, the city glitters above, and the van is two blocks away. You won.",
            "heat_delta": 0,
            "total_heat": self.heat,
            "zone":       "LOBBY",
            "zone_data":  {},
            "new_items":  [],
            "event":      {"type": "success", "msg": "EXTRACTION COMPLETE — THE VELVET ACE IS YOURS", "heatDelta": -30},
            "game_over":  False,
            "victory":    True,
            "tags":       {},
        }


if __name__ == "__main__":
    brain = HeistBrain()
    print("Building vector database from ./data...")
    brain.index_documents()
    print("Database built. You can now run the Streamlit app.")