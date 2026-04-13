import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL WIN PATH (optimised — ~15 moves minimum):
#   START: CASINO
#   CASINO → CASHIER_CAGE              (grab B3_KEYCARD from lockbox)
#   CASHIER_CAGE → STAFF_ELEVATOR      (needs B3_KEYCARD)
#   STAFF_ELEVATOR → B3_CORRIDOR
#   B3_CORRIDOR → SECURITY_COMMAND     (read sticky note → VAULT_PIN)
#   B3_CORRIDOR → COUNT_ROOM           (grab keys → VAULT_KEYS)
#   B3_CORRIDOR → VAULT_ELEVATOR       (needs B3_KEYCARD) → B4_VAULT_ANTECHAMBER
#   B4_VAULT_ANTECHAMBER → VAULT_CHAMBER (needs VAULT_KEYS + VAULT_PIN) → VICTORY
#   B4_VAULT_ANTECHAMBER → VAULT_ELEVATOR (B3_KEYCARD — works both ways) → B3_CORRIDOR
# ALTERNATE ROUTE (longer, more atmospheric):
#   CASINO → KITCHEN_L2 → HVAC_SHAFT → B3_CORRIDOR  (still works)
# NOTE: No laser grids. No weight sensors. Vault elevator is bidirectional with keycard.
#       Staff elevator is intermediate zone between CASHIER_CAGE and B3_CORRIDOR.
# ══════════════════════════════════════════════════════════════════════════════

ZONES = {
    "LOBBY": {
        "label": "L1 — Hotel Lobby",
        "exits": ["CASINO"],
        "objects": ["Reception desk", "Security camera cluster", "Guest elevator"],
        "threats": ["Emily Park (receptionist)", "2 plainclothes guards"],
        "required_items": [],
        "flavor": "The marble atrium hums with tourists, all oblivious."
    },
    "CASINO": {
        "label": "L0 — Casino Floor",
        "exits": ["LOBBY", "KITCHEN_L2", "CASHIER_CAGE"],
        "objects": ["Slot machine bank", "ATM cluster", "Marcus Reed patrol path"],
        "threats": ["Marcus Reed (12-min patrol loop)", "Melissa Warburton (dealer, highly alert)"],
        "required_items": [],
        "flavor": "150,000 sq ft of distraction — the perfect cover."
    },
    "CASHIER_CAGE": {
        "label": "L0 — Cashier Cage",
        "exits": ["CASINO", "STAFF_ELEVATOR"],
        "objects": [
            "Key lockbox on wall — contains the B3 Keycard",
            "Guard rotation board",
            "Staff service elevator (concealed behind supervisor's desk — B3 Keycard required)"
        ],
        "threats": ["2 armed cashier guards"],
        "required_items": [],
        "flavor": "Rows of cash behind thick glass. The keycard lockbox is right there — and behind the supervisor's desk, a concealed staff elevator drops straight to B3."
    },
    "KITCHEN_L2": {
        "label": "L2 — Kitchen",
        "exits": ["CASINO", "HVAC_SHAFT"],
        "objects": ["Steam vents (camera blind spot)", "HVAC maintenance access panel — loose cover, no tools needed"],
        "threats": ["Miguel Das (janitor, careless but present)"],
        "required_items": [],
        "flavor": "Steam and grease — and a loose vent panel no one bothered to fix."
    },
    "HVAC_SHAFT": {
        "label": "HVAC Vertical Shaft",
        "exits": ["KITCHEN_L2", "B3_CORRIDOR"],
        "objects": ["80x80 cm duct — traversable", "Filter panel (20 sec to remove, no tools)"],
        "threats": [
            "Movement creates noise audible from B3 — move slowly",
            "No cameras inside the shaft (confirmed blind spot)"
        ],
        "required_items": [],
        "flavor": "Dark, tight, and the only route that skips every checkpoint."
    },
    "STAFF_ELEVATOR": {
        "label": "Staff Service Elevator",
        "exits": ["CASHIER_CAGE", "B3_CORRIDOR"],
        "objects": ["Keycard reader", "Floor selector — Casino level and B3"],
        "threats": ["No cameras inside the shaft"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "Unmarked, unmonitored, and not on any public map. One swipe takes you straight to B3."
    },
    "B3_CORRIDOR": {
        "label": "B3 — Central Corridor",
        "exits": ["SURVEILLANCE_HQ", "SECURITY_COMMAND", "COUNT_ROOM", "VAULT_ELEVATOR", "HVAC_SHAFT", "STAFF_ELEVATOR"],
        "objects": ["HVAC shaft junction", "Staff service elevator (returns to Cashier Cage via Casino level)"],
        "threats": [
            "Rick Green (distracted, checks phone every 3-5 min)"
        ],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The spine of their operation. One distracted guard between you and everything."
    },
    "SURVEILLANCE_HQ": {
        "label": "B3 — Surveillance HQ",
        "exits": ["B3_CORRIDOR"],
        "objects": [
            "Primary camera control terminal",
            "Camera loop device port — loop device is here",
            "Vault camera feed (B4)"
        ],
        "threats": ["Eric Chen (technician, checks systems hourly)"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "1,240 eyes on a single screen. Kill this room and you're a ghost."
    },
    "SECURITY_COMMAND": {
        "label": "B3 — Security Command",
        "exits": ["B3_CORRIDOR"],
        "objects": [
            "Sensor control panel (disables B4 motion sensors)",
            "Desk with top drawer — vault PIN written on a sticky note inside"
        ],
        "threats": ["2 guards on rotation", "Radio check every 10 min"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The guards stare at monitors. Someone was very careless with the desk drawers."
    },
    "COUNT_ROOM": {
        "label": "B3 — Count Room",
        "exits": ["B3_CORRIDOR"],
        "objects": [
            "Cash processing equipment",
            "Key lockbox on wall — contains Vault Key ALPHA and Vault Key BETA (both inside)"
        ],
        "threats": ["Albert King (vault staff, strict routine)", "2 armed escorts"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "Millions move through here daily. Both vault keys sit in the lockbox."
    },
    "VAULT_ELEVATOR": {
        "label": "Vault Elevator",
        "exits": ["B3_CORRIDOR", "B4_VAULT_ANTECHAMBER"],
        "objects": ["Keycard reader (both floors)", "Floor selector panel — B3 and B4 buttons"],
        "threats": ["Keycard required to activate on both floors"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "One swipe, one floor — works going down to B4 or back up to B3."
    },
    "B4_VAULT_ANTECHAMBER": {
        "label": "B4 — Vault Antechamber",
        "exits": ["VAULT_ELEVATOR", "VAULT_CHAMBER"],
        "objects": [
            "Motion sensors (disable from Security Command sensor panel)",
            "Vault door with dual keyhole and PIN keypad",
            "Elevator keycard reader (B3_KEYCARD — returns to B3)"
        ],
        "threats": [
            "Motion sensors — active unless disabled from Security Command",
            "5 vault security staff patrolling"
        ],
        "required_items": [],
        "flavor": "20 metres underground. The vault door ahead, the elevator behind — your exit is the same keycard that got you in."
    },
    "VAULT_CHAMBER": {
        "label": "B4 — VAULT CHAMBER",
        "exits": ["B4_VAULT_ANTECHAMBER"],
        "objects": ["Diamonds", "Gold bullion", "Rare collectibles", "VIP collateral"],
        "threats": [],
        "required_items": ["VAULT_KEYS", "VAULT_PIN"],
        "flavor": "TARGET ACQUIRED. The vault is open. Take only what you came for."
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ITEM DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
ITEM_DEFINITIONS = {
    "B3_KEYCARD": {
        "label": "B3 Keycard",
        "desc": "Grants access to all B3 zones and the B4 elevator. Found in Cashier Cage lockbox."
    },
    "VAULT_KEYS": {
        "label": "Vault Keys (Alpha + Beta)",
        "desc": "Both physical keys required to open the vault door. Stored in Count Room lockbox."
    },
    "VAULT_PIN": {
        "label": "Vault PIN Code",
        "desc": "4-digit PIN for the B4 vault keypad. Written on a sticky note in Security Command desk top drawer."
    },
    "CAMERA_LOOP_DEVICE": {
        "label": "Camera Loop Device",
        "desc": "Loops B3/B4 camera feed for up to 3 minutes. Found in Surveillance HQ. Not required but highly useful."
    },
    "SENSORS_DISABLED": {
        "label": "B4 Sensors: Offline",
        "desc": "Motion sensors disabled at Security Command. B4 approach is clear."
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ZONE_ITEMS — items granted when player SEARCHES a zone
# ══════════════════════════════════════════════════════════════════════════════

ZONE_ITEMS = {
    "CASHIER_CAGE":    ["B3_KEYCARD"],
    "SURVEILLANCE_HQ": ["CAMERA_LOOP_DEVICE"],
    "COUNT_ROOM":      ["VAULT_KEYS"],
    "SECURITY_COMMAND": ["VAULT_PIN", "SENSORS_DISABLED"],
}

# ══════════════════════════════════════════════════════════════════════════════
# KEY_ITEM_HINTS — items requiring a hint first, then player action
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
}



# ══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════════════════════════

def _extract_text(response) -> str:
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
        self.current_zone = "CASINO"
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



    def _try_move(self, user_move: str) -> str | None:
        move_lower = user_move.lower()

        # ── Context-aware routing ─────────────────────────────────────────────
        ELEVATOR_WORDS = ["elevator", "lift", "staff elevator", "service elevator",
                          "concealed elevator", "supervisor"]
        # From CASHIER_CAGE, elevator goes to STAFF_ELEVATOR (intermediate zone)
        if self.current_zone == "CASHIER_CAGE":
            if any(e in move_lower for e in ELEVATOR_WORDS):
                return "STAFF_ELEVATOR"
        # From B4_VAULT_ANTECHAMBER, elevator goes back up to VAULT_ELEVATOR
        if self.current_zone == "B4_VAULT_ANTECHAMBER":
            if any(e in move_lower for e in ELEVATOR_WORDS) or "b3" in move_lower:
                return "VAULT_ELEVATOR"
        # ─────────────────────────────────────────────────────────────────────

        zone_hints = {
            "lobby":              "LOBBY",
            "casino":             "CASINO",
            "kitchen":            "KITCHEN_L2",
            "hvac":               "HVAC_SHAFT",
            "vent":               "HVAC_SHAFT",
            "duct":               "HVAC_SHAFT",
            "cashier":            "CASHIER_CAGE",
            "cage":               "CASHIER_CAGE",
            "b3 corridor":        "B3_CORRIDOR",
            "corridor":           "B3_CORRIDOR",
            "surveillance":       "SURVEILLANCE_HQ",
            "security command":   "SECURITY_COMMAND",
            "count room":         "COUNT_ROOM",
            # staff elevator (cashier cage ↔ b3) — specific hints before generic
            "staff elevator":     "STAFF_ELEVATOR",
            "service elevator":   "STAFF_ELEVATOR",
            "concealed elevator": "STAFF_ELEVATOR",
            # vault elevator (b3 ↔ b4)
            "vault elevator":     "VAULT_ELEVATOR",
            "b3 elevator":        "VAULT_ELEVATOR",
            "secure elevator":    "VAULT_ELEVATOR",
            "elevator to b4":     "VAULT_ELEVATOR",
            "elevator":           "VAULT_ELEVATOR",
            "antechamber":        "B4_VAULT_ANTECHAMBER",
            "vault antechamber":  "B4_VAULT_ANTECHAMBER",
            "vault chamber":      "VAULT_CHAMBER",
            "vault":              "VAULT_CHAMBER",
            "b4":                 "B4_VAULT_ANTECHAMBER",
            "b3":                 "B3_CORRIDOR",
        }
        movement_verbs = [
            "move to", "go to", "enter", "head to", "proceed to", "sneak into",
            "climb into", "crawl into", "take the elevator", "walk to",
            "run to", "get to", "slip into", "drop into", "descend to",
            # natural alternatives players commonly type:
            "got into", "got to", "get into", "go into", "went to", "went into",
            "move into", "moved into", "moved to", "head into", "sneak to",
            "sneak in", "slip to", "slip in", "make my way", "make it to",
            "navigate to", "navigate into", "step into", "step to",
            "duck into", "duck to", "creep into", "creep to",
            "slide into", "slide to", "push into", "push to",
            "go through", "pass through",
            # elevator / access action verbs:
            "use the", "use", "ride", "take the", "activate",
        ]
        if not any(v in move_lower for v in movement_verbs):
            return None
        for hint, zone_key in zone_hints.items():
            if hint in move_lower:
                return zone_key
        return None

    def _can_enter(self, zone_key: str) -> tuple[bool, str]:
        zone = ZONES.get(zone_key, {})
        required = zone.get("required_items", [])
        missing = [r for r in required if r not in self.inventory]
        if missing:
            labels = [ITEM_DEFINITIONS.get(m, {}).get("label", m) for m in missing]
            return False, f"Access denied — you need: {', '.join(labels)}"
        return True, ""

    def play_move(self, user_move: str) -> dict:
        if self.game_over:
            return self._dead_response()
        if self.victory:
            return self._victory_response()

        self._load_vectorstore()
        self.move_count += 1

        zone = self._zone_data()
        zone_at_turn_start = self.current_zone  # saved for dual-zone PICKUP validation

        # Movement
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

        new_items: list[dict] = []

        # RAG context
        try:
            relevant_docs = self.vectorstore.similarity_search(user_move, k=2)
            context = "\n---\n".join([d.page_content for d in relevant_docs])
        except Exception:
            context = "No additional classified security data retrieved."

        # Prompt assembly
        zone_summary = (
            f"CURRENT ZONE: {zone.get('label', self.current_zone)}\n"
            f"EXITS: {', '.join(zone.get('exits', []))}\n"
            f"OBJECTS: {', '.join(zone.get('objects', []))}\n"
            f"THREATS: {', '.join(zone.get('threats', []))}\n"
            f"PLAYER INVENTORY: {', '.join(self.inventory) if self.inventory else 'nothing'}\n"
        )

        # Items acquirable in the current zone (for GM guidance)
        # Build a label→key map so label-typed PICKUP values still match
        LABEL_TO_KEY = {v.get("label", "").lower(): k for k, v in ITEM_DEFINITIONS.items()}

        ITEM_PICKUP_RULES = {
            "B3_KEYCARD":        "PHYSICAL — grant if player picks up or takes the keycard from the lockbox",
            "VAULT_KEYS":        "PHYSICAL — grant if player picks up / grabs the vault keys from the lockbox",
            "CAMERA_LOOP_DEVICE": "PHYSICAL — grant if player takes or uses the loop device at the terminal",
            "VAULT_PIN":         "KNOWLEDGE — grant if player reads, notes, memorizes, photographs or otherwise learns the PIN code. 'Noting down' COUNTS.",
            "SENSORS_DISABLED":  "STATE — grant if player disables, deactivates, or turns off the motion sensor panel",
        }

        zone_acquirable = ZONE_ITEMS.get(self.current_zone, [])
        acquirable_note = ""
        if zone_acquirable:
            not_yet_held = [k for k in zone_acquirable if k not in self.inventory]
            if not_yet_held:
                item_lines = []
                for k in not_yet_held:
                    label = ITEM_DEFINITIONS.get(k, {}).get("label", k)
                    rule  = ITEM_PICKUP_RULES.get(k, "grant if player acquires it")
                    item_lines.append(f"  • {k} (\"{label}\") — {rule}")
                acquirable_note = (
                    "ACQUIRABLE ITEMS HERE (output EXACT key in PICKUP tag):\n"
                    + "\n".join(item_lines) + "\n"
                )

        key_item_note = ""
        for item_key, hint_data in KEY_ITEM_HINTS.items():
            if hint_data["zone"] == self.current_zone and item_key not in self.inventory:
                key_item_note += f"\n{hint_data['hint']}\n"
                break

        block_note = f"\nGM BLOCK: {blocked_msg}\n" if blocked_msg else ""

        prompt = f"""
You are the Game Master of a noir heist thriller set in The Velvet Ace Casino, Las Vegas.
Narrate ONLY what is happening RIGHT NOW in the current zone.

CRITICAL RULE: Only reference items, routes, people, and objects explicitly listed in ZONE DATA below.
NEVER invent keycards, tools, NPCs, doors, security systems, or objects not present in the zone data or player inventory.
NEVER mention laser grids or weight sensors — they do not exist in this game.
The ONLY obtainable items in this entire game are: B3 Keycard, Vault Keys (Alpha + Beta), Vault PIN Code, Camera Loop Device.
The B3/B4 elevator requires the B3 Keycard and works in BOTH directions (up to B3 and down to B4).
SECURITY FACTS (RAG — classified documents):
{context}

ZONE DATA:
{zone_summary}
{acquirable_note}
{key_item_note}
{block_note}

PLAYER MOVE:
{user_move}

STRICT GM RULES:
1. Write EXACTLY 1 to 2 short punchy sentences. No fluff.
2. Judge the move realistically. Smart moves succeed. Stupid moves fail.
3. NEVER invent items, people, routes, security systems, or obstacles not listed in ZONE DATA. If it is not in ZONE DATA, it does not exist.
4. NEVER mention laser grids, weight sensors, or any system not listed in ZONE DATA — these do not exist in this game.
5. The elevator between B3 and B4 works with the B3 Keycard in BOTH directions. If the player has the keycard they can always use it to go up OR down.
6. If GM BLOCK is set, narrate the failure naturally.
7. Heat (integer, -10 to 30): -10 to -1 = brilliant; 0 = idle; 1-5 = minor risk; 6-15 = sloppy; 16-30 = reckless.
8. After the story, output EXACTLY on separate lines:
   HEAT: [integer]
   LOCATION: [zone key, e.g. CASHIER_CAGE]
   STATUS: [CLEAR | ALERTED | COMPROMISED | CAPTURED | VICTORY]
   PICKUP: [comma-separated EXACT item keys from ACQUIRABLE ITEMS HERE — or NONE]
9. PICKUP rules (read carefully):
   - PHYSICAL items (keycard, keys, device): grant if player physically takes/grabs/pockets the object.
   - KNOWLEDGE items (VAULT_PIN): grant if player reads, notes, memorizes, photographs or otherwise learns the PIN code. 'Noting down' COUNTS.
   - STATE items (SENSORS_DISABLED): grant if player disables/deactivates the referenced system.
   - Use the EXACT key from ACQUIRABLE ITEMS HERE (e.g. VAULT_PIN, not 'Vault PIN Code').
   - Do NOT grant items not listed in ACQUIRABLE ITEMS HERE.
   - Do NOT grant items already in PLAYER INVENTORY.
   - If nothing acquired, output: PICKUP: NONE

Output ONLY the story + 4 tags. Nothing else.
"""

        response = self.llm.invoke(prompt)
        raw = _extract_text(response)

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
            elif stripped.startswith("PICKUP:"):
                tags["pickup"] = stripped.split(":", 1)[1].strip()
            else:
                story_lines.append(line)

        story = " ".join(" ".join(story_lines).split()).strip()
        status = tags.get("status", "CLEAR")
        gm_location = tags.get("location", self.current_zone)

        # ── Zone update (LLM-driven movement) ─────────────────────────────────
        llm_zone_changed = False
        if gm_location in ZONES and not zone_changed:
            prev_zone = self.current_zone
            # Validate: target zone must be a valid exit AND player meets requirements
            exits = ZONES.get(prev_zone, {}).get("exits", [])
            can_enter, _ = self._can_enter(gm_location)
            if gm_location == prev_zone or (gm_location in exits and can_enter):
                self.current_zone = gm_location
                llm_zone_changed = (self.current_zone != prev_zone)

        # ── AI-driven item pickup (PICKUP tag from GM) ─────────────────────────
        # The LLM decides what the player acquired; Python only validates.
        pickup_raw = tags.get("pickup", "NONE").strip()
        if pickup_raw.upper() != "NONE" and pickup_raw:
            # Zones eligible for pickup this turn (where the player was AND where they are now)
            eligible_zones = {self.current_zone, zone_at_turn_start}
            for raw_key in pickup_raw.split(","):
                key = raw_key.strip()
                # Fallback: LLM sometimes outputs the label instead of the key
                if key not in ITEM_DEFINITIONS:
                    key = LABEL_TO_KEY.get(key.lower(), key)
                # Validate: item must exist, be in an eligible zone, not already owned
                if (
                    key in ITEM_DEFINITIONS
                    and any(key in ZONE_ITEMS.get(z, []) for z in eligible_zones)
                    and key not in self.inventory
                ):
                    defn = ITEM_DEFINITIONS[key]
                    self.inventory.append(key)
                    entry = {"key": key, "label": defn.get("label", key), "desc": defn.get("desc", "")}
                    self.intel_log.append(entry)
                    new_items.append(entry)

        IDLE_PHRASES = [
            "wait", "do nothing", "stay", "look around", "think",
            "what should", "where am i", "what do i", "how do i",
            "check inventory", "check map", "what is", "what are",
        ]
        is_idle = any(phrase in user_move.lower() for phrase in IDLE_PHRASES)

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