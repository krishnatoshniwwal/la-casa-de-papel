import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI                         
from langchain_huggingface import HuggingFaceEmbeddings         
from langchain_chroma import Chroma

load_dotenv()
api_key = os.getenv("XAI_API_KEY")

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
        "objects": ["620 cameras", "ATM cluster", "Slot machine bank", "MARCUS REED patrol path"],
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
    "HVAC_SHAFT": {
        "label": "HVAC Vertical Shaft",
        "exits": ["KITCHEN_L2", "B3_CORRIDOR"],
        "objects": ["80x80 cm main duct", "Filter panel (20 sec to remove)", "Jorge Ramirez maintenance log"],
        "threats": ["Thermal sensors (26-28°C safe range)", "Movement noise"],
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
    "STAFF_ELEVATOR": {
        "label": "Staff Elevator",
        "exits": ["CASINO", "PARKING_B2", "B3_CORRIDOR"],
        "objects": ["Keycard reader", "Floor selector panel"],
        "threats": ["Keycard required for B3 access"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The panel glows. B3 is one swipe away — if you have the card."
    },
    "CASHIER_CAGE": {
        "label": "L0 — Cashier Cage",
        "exits": ["CASINO"],
        "objects": ["Security terminal (guard schedules)", "Count room access door", "Rick Green rotation sheet"],
        "threats": ["2 armed cashier guards"],
        "required_items": [],
        "flavor": "Rows of cash behind thick glass. The guard schedule is pinned to the wall."
    },
    "B3_CORRIDOR": {
        "label": "B3 — Central Corridor",
        "exits": ["SURVEILLANCE_HQ", "SECURITY_COMMAND", "COUNT_ROOM", "B3_ELEVATOR", "B3_MAINTENANCE_SHAFT"],
        "objects": ["Biometric gate (fingerprint + keycard)", "Laser grid emitters", "Maintenance shaft junction"],
        "threats": ["Rick Green (distracted, checks phone every 3-5 min)", "Laser grid (IR, 0.08 m/s max safe speed)"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "The spine of their operation. One blind guard and a 12-minute recalibration window."
    },
    "SURVEILLANCE_HQ": {
        "label": "B3 — Surveillance HQ",
        "exits": ["B3_CORRIDOR"],
        "objects": ["Primary camera control terminal", "Camera loop device port", "Vault camera feed (B4)", "Eric Chen duty log"],
        "threats": ["Eric Chen (technician, checks systems hourly)", "No windows, 24/7 staffed"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "1,240 eyes on a single screen. Kill this room and you're a ghost."
    },
    "SECURITY_COMMAND": {
        "label": "B3 — Security Command",
        "exits": ["B3_CORRIDOR"],
        "objects": ["Guard rotation board", "Radio dispatch unit", "VAULT PIN document (taped under desk)", "Spare B4 keycard"],
        "threats": ["2 guards on rotation", "Radio check every 10 min"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "They wrote the vault PIN on a sticky note. Old habits die hard."
    },
    "COUNT_ROOM": {
        "label": "B3 — Count Room",
        "exits": ["B3_CORRIDOR"],
        "objects": ["Cash processing equipment", "Albert King timesheet", "Dual vault key — KEY ALPHA"],
        "threats": ["Albert King (vault staff, strict routine)", "2 armed escorts"],
        "required_items": ["B3_KEYCARD"],
        "flavor": "Millions move through here daily. Key Alpha sits in the lockbox — unguarded between 03:00–03:15."
    },
    "B3_MAINTENANCE_SHAFT": {
        "label": "B3 — Maintenance Shaft",
        "exits": ["B3_CORRIDOR", "B4_VAULT_ANTECHAMBER"],
        "objects": ["Camera blind spot (confirmed)", "Vent to B4 antechamber", "Biometric relay cable"],
        "threats": ["Thermal sensors (lag 1 sec after cooling)"],
        "required_items": [],
        "flavor": "Not on any public schematic. Drops straight to the vault antechamber."
    },
    "B3_ELEVATOR": {
        "label": "B3→B4 Secure Elevator",
        "exits": ["B3_CORRIDOR", "B4_VAULT_ANTECHAMBER"],
        "objects": ["Retina + fingerprint scanner", "Dual authorization panel"],
        "threats": ["Iris scanner", "Fingerprint scanner", "Dual auth required — two people"],
        "required_items": ["B3_KEYCARD", "BIOMETRIC_BYPASS"],
        "flavor": "Two keys, two faces, one door. Unless you have a bypass."
    },
    "B4_VAULT_ANTECHAMBER": {
        "label": "B4 — Vault Antechamber",
        "exits": ["B3_MAINTENANCE_SHAFT", "B3_ELEVATOR", "VAULT_CHAMBER"],
        "objects": ["Motion sensors", "Thermal sensors", "Dual-key vault door", "Vault PIN keypad"],
        "threats": ["Motion sensors (2mm trigger threshold)", "10-15 vault security staff", "Custodian pair"],
        "required_items": [],
        "flavor": "You're 20 meters underground. The vault door is the only thing between you and everything."
    },
    "VAULT_CHAMBER": {
        "label": "B4 — VAULT CHAMBER 🎯",
        "exits": ["B4_VAULT_ANTECHAMBER"],
        "objects": ["Diamonds", "Jewelry", "Gold bullion", "VIP collateral", "Rare collectibles", "10-20 storage chambers"],
        "threats": ["Time-lock (20 sec open window)", "Alarm if weight sensors triggered wrong"],
        "required_items": ["VAULT_PIN", "KEY_ALPHA", "KEY_BETA"],
        "flavor": "TARGET ACQUIRED. 20 seconds. Take only what you came for."
    }
}

ITEM_DEFINITIONS = {
    "B3_KEYCARD":        {"label": "B3 Keycard",           "desc": "Grants access to all B3 zones and the secure elevator"},
    "VAULT_PIN":         {"label": "Vault PIN Code",        "desc": "4-digit code for the B4 vault keypad (found in Security Command)"},
    "KEY_ALPHA":         {"label": "Vault Key — ALPHA",     "desc": "First of two keys required for vault unlock (Count Room, 03:00–03:15 window)"},
    "KEY_BETA":          {"label": "Vault Key — BETA",      "desc": "Second vault key (carried by Albert King)"},
    "BIOMETRIC_BYPASS":  {"label": "Biometric Bypass",      "desc": "Cloned fingerprint/retina data; allows solo B4 elevator access"},
    "CAMERA_LOOP_DEVICE":{"label": "Camera Loop Device",    "desc": "Loops B3/B4 surveillance feed for 3 minutes"},
    "GUARD_SCHEDULE":    {"label": "Guard Rotation Sheet",  "desc": "Exact shift times, breaks, patrol loops — invaluable for timing"},
    "LASER_SPECS":       {"label": "Laser Grid Specs",      "desc": "Emitter positions, recalibration gaps, edge vulnerabilities"},
}

ITEM_TRIGGERS = {
    "B3_KEYCARD":         ["keycard", "key card", "swipe card", "access card", "badge"],
    "VAULT_PIN":          ["vault pin", "pin code", "combination", "sticky note", "under desk", "4 digit"],
    "KEY_ALPHA":          ["key alpha", "vault key", "dual key", "count room key"],
    "KEY_BETA":           ["key beta", "albert king", "king's key"],
    "BIOMETRIC_BYPASS":   ["biometric bypass", "clone fingerprint", "fake retina", "spoof biometric"],
    "CAMERA_LOOP_DEVICE": ["loop device", "camera loop", "loop feed", "surveillance loop"],
    "GUARD_SCHEDULE":     ["guard schedule", "rotation sheet", "patrol schedule", "shift times"],
    "LASER_SPECS":        ["laser specs", "laser grid", "emitter specs", "recalibration gap"],
}


# Items auto-granted when the player searches/scouts the correct zone.
ZONE_ITEMS = {
    "CASHIER_CAGE":     ["B3_KEYCARD", "GUARD_SCHEDULE"],
    "SECURITY_COMMAND": ["B3_KEYCARD"],
    "SURVEILLANCE_HQ":  ["LASER_SPECS", "CAMERA_LOOP_DEVICE"],
    "COUNT_ROOM":       ["KEY_ALPHA", "KEY_BETA"],
}

# Key items that require the AI to hint first — player must act on the hint.
KEY_ITEM_HINTS = {
    "VAULT_PIN": {
        "zone": "SECURITY_COMMAND",
        "hint": (
            "HINT TO GM: The player is in Security Command. "
            "There is a sticky note with the vault PIN taped under the desk — "
            "drop a subtle clue that something is hidden under the desk without "
            "naming it directly. Do NOT award the item yet."
        ),
    },
    "BIOMETRIC_BYPASS": {
        "zone": "SURVEILLANCE_HQ",
        "hint": (
            "HINT TO GM: The player is in Surveillance HQ. "
            "The terminal here holds biometric records for all B4-authorised staff. "
            "Hint that the system could be exploited to extract or clone credentials "
            "without naming it directly. Do NOT award the item yet."
        ),
    },
}


class HeistBrain:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # keep this
            model_kwargs={"device": "cpu"},
            encode_kwargs={"batch_size": 32}
        )
        self.llm = ChatOpenAI(
            model="grok-3-mini",          # or "grok-3" for the full model
            temperature=0.75,
            max_retries=3,
            api_key=api_key,
            base_url="https://api.x.ai/v1"   # xAI's OpenAI-compatible endpoint
        )
        self.db_path = "./chroma_db"
        self.vectorstore = None
        self.current_zone = "LOBBY"
        self.inventory = []
        self.intel_log = []
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

    def _zone_data(self):
        z = ZONES.get(self.current_zone, {})
        return z

    def _check_item_triggers(self, user_move: str) -> list[str]:
        """Keyword-triggered grant — used for key items that need deliberate player action."""
        move_lower = user_move.lower()
        triggered = []
        for item_key, keywords in ITEM_TRIGGERS.items():
            if item_key not in self.inventory:
                for kw in keywords:
                    if kw in move_lower:
                        triggered.append(item_key)
                        break
        return triggered

    def _check_zone_search(self, user_move: str) -> list[str]:
        """Auto-grant findable items when the player searches the current zone.
        Key items (VAULT_PIN, BIOMETRIC_BYPASS) are excluded — they need hint-then-act."""
        SEARCH_VERBS = [
            "search", "scout", "look", "examine", "check", "inspect",
            "sweep", "scan", "explore", "investigate", "look around",
            "case the", "survey", "recon"
        ]
        move_lower = user_move.lower()
        if not any(v in move_lower for v in SEARCH_VERBS):
            return []
        key_items = set(KEY_ITEM_HINTS.keys())
        granted = []
        for item_key in ZONE_ITEMS.get(self.current_zone, []):
            if item_key not in self.inventory and item_key not in key_items:
                granted.append(item_key)
        return granted

    def _try_move(self, user_move: str) -> str | None:
        move_lower = user_move.lower()
        zone_hints = {
            "lobby":               "LOBBY",
            "casino":              "CASINO",
            "kitchen":             "KITCHEN_L2",
            "hvac":                "HVAC_SHAFT",
            "vent":                "HVAC_SHAFT",
            "duct":                "HVAC_SHAFT",
            "parking":             "PARKING_B2",
            "staff elevator":      "STAFF_ELEVATOR",
            "cashier":             "CASHIER_CAGE",
            "cage":                "CASHIER_CAGE",
            "b3 corridor":         "B3_CORRIDOR",
            "corridor":            "B3_CORRIDOR",
            "surveillance":        "SURVEILLANCE_HQ",
            "security command":    "SECURITY_COMMAND",
            "count room":          "COUNT_ROOM",
            "maintenance shaft":   "B3_MAINTENANCE_SHAFT",
            "b3 elevator":         "B3_ELEVATOR",
            "antechamber":         "B4_VAULT_ANTECHAMBER",
            "vault antechamber":   "B4_VAULT_ANTECHAMBER",
            "vault":               "VAULT_CHAMBER",
            "b4":                  "B4_VAULT_ANTECHAMBER",
            "b3":                  "B3_CORRIDOR",
        }
        movement_verbs = ["move to", "go to", "enter", "head to", "proceed to", "sneak into",
                          "climb into", "crawl into", "take the elevator", "walk to", "run to", "get to"]
        is_movement = any(v in move_lower for v in movement_verbs)
        if not is_movement:
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

        target_zone = self._try_move(user_move)
        blocked_msg = ""
        zone_changed = False

        if target_zone:
            if target_zone not in zone.get("exits", []) and target_zone != self.current_zone:
                blocked_msg = f"[NOT_CONNECTED: {target_zone} is not reachable from {self.current_zone}]"
            else:
                can_enter, reason = self._can_enter(target_zone)
                if can_enter:
                    self.current_zone = target_zone
                    zone = self._zone_data()
                    zone_changed = True
                else:
                    blocked_msg = f"[ACCESS_DENIED: {reason}]"

        # ── Item discovery (two-tier) ─────────────────────────────────────────
        # Tier 1: auto-grant on search actions in the current zone
        zone_search_keys = self._check_zone_search(user_move)
        # Tier 2: keyword-triggered grant (player acted on a hint)
        keyword_keys     = self._check_item_triggers(user_move)
        all_new_keys     = list(dict.fromkeys(zone_search_keys + keyword_keys))

        new_items = []
        for key in all_new_keys:
            defn = ITEM_DEFINITIONS.get(key, {})
            self.inventory.append(key)
            entry = {"key": key, "label": defn.get("label", key), "desc": defn.get("desc", "")}
            self.intel_log.append(entry)
            new_items.append(entry)

        try:
            relevant_docs = self.vectorstore.similarity_search(user_move, k=2)
            context = "\n---\n".join([d.page_content for d in relevant_docs])
        except Exception:
            context = "No additional classified security data retrieved."

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
            new_items_note = f"\nPLAYER JUST ACQUIRED: {', '.join(labels)} — mention this discovery in the story.\n"

        # Inject hint nudge for key items when player is in the right zone
        key_item_note = ""
        for item_key, hint_data in KEY_ITEM_HINTS.items():
            if hint_data["zone"] == self.current_zone and item_key not in self.inventory:
                key_item_note += f"\n{hint_data['hint']}\n"
                break  # one hint at a time

        block_note = f"\nGM BLOCK: {blocked_msg}\n" if blocked_msg else ""

        prompt = f"""
You are the Game Master of a noir heist thriller set in The Velvet Ace Casino, Las Vegas.
Your job is to judge player actions FAIRLY using the SECURITY FACTS and ZONE DATA below.

═══ SECURITY FACTS (from classified documents) ═══
{context}

═══ ZONE DATA ═══
{zone_summary}
{new_items_note}
{key_item_note}
{block_note}

═══ PLAYER MOVE ═══
{user_move}

═══ GM RULES ═══
1. Write EXACTLY 1 to 2 short sentences. Be incredibly concise, fast-paced, and punchy. Do not waste words.
2. Judge the move REALISTICALLY based on the security facts. Smart moves succeed. Stupid moves fail.
3. If GM BLOCK is set, narrate the failure naturally.
4. If player acquired new items, weave their discovery into the story.
5. After the narrative, output EXACTLY these tags on separate lines:
   HEAT: [integer 0-30 — 0 for brilliant stealth, 30 for reckless exposure]
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

        raw = ""
        if isinstance(response.content, list):
            item = response.content[0] if response.content else {}
            raw = item.get("text", str(item)) if isinstance(item, dict) else str(item)
        else:
            raw = str(response.content)

        lines = raw.strip().split("\n")
        tags = {}
        story_lines = []
        for line in lines:
            stripped = line.strip().replace("*", "")
            if stripped.startswith("HEAT:"):
                try:
                    tags["heat"] = int(stripped.split(":", 1)[1].strip().split()[0])
                except:
                    tags["heat"] = 10
            elif stripped.startswith("LOCATION:"):
                tags["location"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("STATUS:"):
                tags["status"] = stripped.split(":", 1)[1].strip()
            else:
                story_lines.append(line)

        story = " ".join(" ".join(story_lines).split()).strip()
        heat_delta = tags.get("heat", 10)
        status = tags.get("status", "CLEAR")
        gm_location = tags.get("location", self.current_zone)

        if gm_location in ZONES and not zone_changed:
            self.current_zone = gm_location

        event = None
        if status == "CAPTURED":
            self.game_over = True
            heat_delta = 100
            event = {"type": "danger", "msg": "OPERATIVE DOWN — mission compromised", "heatDelta": 100}
        elif status == "VICTORY":
            self.victory = True
            event = {"type": "success", "msg": "TARGET SECURED — initiating extraction", "heatDelta": -20}
        elif status == "COMPROMISED":
            heat_delta = min(heat_delta + 15, 30)
            event = {"type": "danger", "msg": "EXPOSURE — heat rising fast", "heatDelta": heat_delta}
        elif status == "ALERTED":
            heat_delta = min(heat_delta + 8, 25)
            event = {"type": "warning", "msg": "SECURITY ALERT — adapt your approach", "heatDelta": heat_delta}

        self.heat = min(100, self.heat + heat_delta)

        return {
            "story": story,
            "heat_delta": heat_delta,
            "total_heat": self.heat,
            "zone": self.current_zone,
            "zone_data": ZONES.get(self.current_zone, {}),
            "new_items": new_items,
            "event": event,
            "game_over": self.game_over,
            "victory": self.victory,
            "tags": tags,
        }

    def _dead_response(self) -> dict:
        return {
            "story": "You're in a holding cell two floors below the casino, zip-tied to a chair. The Oracle's line is dead. Mission over.",
            "heat_delta": 0,
            "total_heat": 100,
            "zone": self.current_zone,
            "zone_data": {},
            "new_items": [],
            "event": {"type": "danger", "msg": "OPERATIVE CAPTURED — GAME OVER", "heatDelta": 0},
            "game_over": True,
            "victory": False,
            "tags": {},
        }

    def _victory_response(self) -> dict:
        return {
            "story": "The vault is behind you, the city glitters above, and the van is two blocks away. You won.",
            "heat_delta": 0,
            "total_heat": self.heat,
            "zone": "LOBBY",
            "zone_data": {},
            "new_items": [],
            "event": {"type": "success", "msg": "EXTRACTION COMPLETE — THE VELVET ACE IS YOURS", "heatDelta": -30},
            "game_over": False,
            "victory": True,
            "tags": {},
        }

if __name__ == "__main__":
    brain = HeistBrain()
    print("Building vector database from ./data...")
    brain.index_documents()
    print("Database built! You can now run the Streamlit app.")