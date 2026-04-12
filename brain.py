import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL WIN PATH (simplified):
#   LOBBY → CASINO → CASHIER_CAGE   (search → B3_KEYCARD)
#   CASINO → KITCHEN_L2 → HVAC_SHAFT → B3_CORRIDOR  (needs B3_KEYCARD at gate)
#   B3_CORRIDOR → SURVEILLANCE_HQ   (search → CAMERA_LOOP_DEVICE)
#   B3_CORRIDOR → SECURITY_COMMAND  (interact desk → VAULT_PIN)
#   B3_CORRIDOR → COUNT_ROOM        (search → VAULT_KEYS)
#   B3_CORRIDOR → B3_ELEVATOR (needs B3_KEYCARD) → B4_VAULT_ANTECHAMBER
#   B4_VAULT_ANTECHAMBER → VAULT_CHAMBER (needs VAULT_KEYS + VAULT_PIN)
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
        "exits": ["CASINO"],
        "objects": [
            "Key lockbox on wall — contains the B3 Keycard",
            "Guard rotation board"
        ],
        "threats": ["2 armed cashier guards"],
        "required_items": [],
        "flavor": "Rows of cash behind thick glass. The keycard lockbox is right there on the wall."
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
    "B3_CORRIDOR": {
        "label": "B3 — Central Corridor",
        "exits": ["SURVEILLANCE_HQ", "SECURITY_COMMAND", "COUNT_ROOM", "B3_ELEVATOR", "HVAC_SHAFT"],
        "objects": ["Biometric gate (keycard entry)", "Laser grid emitters", "HVAC shaft junction"],
        "threats": [
            "Rick Green (distracted, checks phone every 3-5 min)",
            "Laser grid — recalibrates every 12 min (brief gap to slip through)"
        ],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The spine of their operation. One distracted guard, a 12-minute recalibration window."
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
        "flavor": "Millions move through here daily. Both vault keys sit in the lockbox — unguarded 03:00-03:15."
    },
    "B3_ELEVATOR": {
        "label": "B3 to B4 Secure Elevator",
        "exits": ["B3_CORRIDOR", "B4_VAULT_ANTECHAMBER"],
        "objects": ["Keycard reader", "Floor selector panel"],
        "threats": ["Keycard required to activate B4 floor"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "One swipe, one floor. The keycard makes it simple."
    },
    "B4_VAULT_ANTECHAMBER": {
        "label": "B4 — Vault Antechamber",
        "exits": ["B3_ELEVATOR", "VAULT_CHAMBER"],
        "objects": [
            "Motion sensors (disable from Security Command sensor panel)",
            "Vault door with dual keyhole and PIN keypad"
        ],
        "threats": [
            "Motion sensors — active unless disabled from Security Command",
            "5 vault security staff patrolling"
        ],
        "required_items": [],
        "flavor": "20 meters underground. The vault door is the only thing between you and everything."
    },
    "VAULT_CHAMBER": {
        "label": "B4 — VAULT CHAMBER",
        "exits": ["B4_VAULT_ANTECHAMBER"],
        "objects": ["Diamonds", "Gold bullion", "Rare collectibles", "VIP collateral"],
        "threats": ["Time-lock (20 sec open window)", "Weight sensors — alarm if items removed incorrectly"],
        "required_items": ["VAULT_KEYS", "VAULT_PIN"],
        "flavor": "TARGET ACQUIRED. 20 seconds. Take only what you came for."
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
        "desc": "Both physical keys required to open the vault door. Stored in Count Room lockbox, unguarded 03:00-03:15."
    },
    "VAULT_PIN": {
        "label": "Vault PIN Code",
        "desc": "4-digit PIN for the B4 vault keypad. Written on a sticky note in Security Command desk top drawer."
    },
    "CAMERA_LOOP_DEVICE": {
        "label": "Camera Loop Device",
        "desc": "Loops B3/B4 camera feed for up to 3 minutes. Found in Surveillance HQ. Not required but highly useful."
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ZONE_ITEMS — items granted when player SEARCHES a zone
# ══════════════════════════════════════════════════════════════════════════════
ZONE_ITEMS = {
    "CASHIER_CAGE":    ["B3_KEYCARD"],
    "SURVEILLANCE_HQ": ["CAMERA_LOOP_DEVICE"],
    "COUNT_ROOM":      ["VAULT_KEYS"],
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
# ITEM_TRIGGERS — explicit action phrases that grant items immediately
# ══════════════════════════════════════════════════════════════════════════════
ITEM_TRIGGERS = {
    "B3_KEYCARD": [
        "grab the keycard", "take the keycard", "pocket the keycard",
        "take the key card", "grab the key card",
        "take the badge", "grab the badge",
        "take the access card", "grab the access card",
        "open the lockbox", "grab from the lockbox",
        "take the card", "grab the card",
    ],

    "VAULT_KEYS": [
        "take both keys", "grab both keys",
        "take the keys", "grab the keys",
        "open the lockbox", "grab the keys from the lockbox",
        "grab the vault keys", "take the vault keys",
        "take key alpha", "grab key alpha",
        "take key beta", "grab key beta",
        "take alpha key", "take beta key",
        "pick up the keys", "collect the keys",
    ],

    "VAULT_PIN": [
        "open the drawer", "check the drawer", "look in the drawer",
        "search the desk", "rifle through the desk",
        "grab the note", "take the note", "read the note",
        "grab the sticky note", "take the sticky note", "read the sticky note",
    ],

    "CAMERA_LOOP_DEVICE": [
        "grab the loop device", "take the loop device",
        "plug in the loop device", "loop the cameras",
        "loop the feed", "grab the device", "take the device",
        "use the terminal", "access the terminal",
    ],
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

    def _check_zone_search(self, user_move: str) -> list[str]:
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

    def _check_item_triggers(self, user_move: str) -> list[str]:
        move_lower = user_move.lower()
        triggered = []

        for item_key, keywords in ITEM_TRIGGERS.items():
            if item_key == "B3_KEYCARD" and self.current_zone != "CASHIER_CAGE":
                continue
            if item_key == "VAULT_KEYS" and self.current_zone != "COUNT_ROOM":
                continue
            if item_key == "VAULT_PIN" and self.current_zone != "SECURITY_COMMAND":
                continue

            if item_key not in self.inventory:
                for kw in keywords:
                    if kw in move_lower:
                        triggered.append(item_key)
                        break

        return triggered

    def _try_move(self, user_move: str) -> str | None:
        move_lower = user_move.lower()
        zone_hints = {
            "lobby":             "LOBBY",
            "casino":            "CASINO",
            "kitchen":           "KITCHEN_L2",
            "hvac":              "HVAC_SHAFT",
            "vent":              "HVAC_SHAFT",
            "duct":              "HVAC_SHAFT",
            "cashier":           "CASHIER_CAGE",
            "cage":              "CASHIER_CAGE",
            "b3 corridor":       "B3_CORRIDOR",
            "corridor":          "B3_CORRIDOR",
            "surveillance":      "SURVEILLANCE_HQ",
            "security command":  "SECURITY_COMMAND",
            "count room":        "COUNT_ROOM",
            "b3 elevator":       "B3_ELEVATOR",
            "secure elevator":   "B3_ELEVATOR",
            "elevator":          "B3_ELEVATOR",
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

        # Item discovery
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

        prompt = f"""
You are the Game Master of a noir heist thriller set in The Velvet Ace Casino, Las Vegas.
Narrate ONLY what is happening RIGHT NOW in the current zone.

CRITICAL RULE: Only reference items, routes, people, and objects explicitly listed in ZONE DATA below.
NEVER invent keycards, tools, NPCs, doors, or objects not present in the zone data or player inventory.
The ONLY obtainable items in this entire game are: B3 Keycard, Vault Keys (Alpha + Beta), Vault PIN Code, Camera Loop Device.

SECURITY FACTS (RAG — classified documents):
{context}

ZONE DATA:
{zone_summary}
{new_items_note}
{key_item_note}
{block_note}

PLAYER MOVE:
{user_move}

STRICT GM RULES:
1. Write EXACTLY 1 to 2 short punchy sentences. No fluff.
2. Judge the move realistically. Smart moves succeed. Stupid moves fail.
3. NEVER invent items, people, or routes not in ZONE DATA.
4. If GM BLOCK is set, narrate the failure naturally.
5. If player acquired new items, weave their discovery into the story.
6. Heat (integer, -10 to 30): -10 to -1 = brilliant; 0 = idle; 1-5 = minor risk; 6-15 = sloppy; 16-30 = reckless.
7. After the story, output EXACTLY on separate lines:
   HEAT: [integer]
   LOCATION: [zone key]
   STATUS: [CLEAR | ALERTED | COMPROMISED | CAPTURED | VICTORY]

Output ONLY the story + 3 tags. Nothing else.
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
            else:
                story_lines.append(line)

        story = " ".join(" ".join(story_lines).split()).strip()
        status = tags.get("status", "CLEAR")
        gm_location = tags.get("location", self.current_zone)

        if gm_location in ZONES and not zone_changed:
            self.current_zone = gm_location

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