# 🎰 Operation Velvet Ace

### AI-Powered Heist Simulation Game

---

## 🚀 Live Demo

🔗 la-casa-de-papel-azy6gsjuuxmtorm4nn9kev.streamlit.app

---

## 🧠 Overview

**Operation Velvet Ace** is an AI-driven stealth simulation game set inside a high-security casino resort.

The player acts as a professional thief, gathering intelligence, navigating restricted zones, and executing a multi-stage heist. Every move is evaluated by an AI “Game Master” that dynamically determines outcomes, risk levels, and consequences.

---

## 🎮 Gameplay

* Start in the **Lobby / Casino**
* Explore interconnected zones
* Collect key items (Keycards, PIN, Vault Keys)
* Bypass surveillance and security systems
* Infiltrate underground vault (B4)
* Steal the diamonds
* Escape without triggering full alert

---

## 🔥 Core Features

### 🧠 AI Game Master

* Uses LLM to interpret player actions
* Generates contextual outcomes
* Ensures dynamic, non-scripted gameplay

---

### 📁 RAG-Based Intelligence System

* Security data stored as structured files
* Retrieved using vector similarity search
* Injected into LLM prompt for realism

---

### 🗺️ Zone-Based Navigation

* Explicit graph of connected locations
* Enforces valid movement paths
* Prevents unrealistic actions

---

### 🎒 Inventory System

* Items acquired via contextual actions
* Includes:

  * B3 Keycard
  * Vault Keys
  * Vault PIN
  * Camera Loop Device
  * Motion Sensor Disabler
  

---

### 🚨 Heat System

* Tracks player risk level
* Increases based on suspicious actions
* High heat → detection / failure

---

## 🏗️ System Architecture

```text
Player Input
     ↓
HeistBrain (Core Engine)
     ↓
Zone System (Movement Validation)
     ↓
Vector DB (RAG Retrieval)
     ↓
LLM (Decision Engine)
     ↓
Game Response (Story + Heat + State)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/krishnatoshniwwal/la-casa-de-papel.git
cd yourrepo
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Set Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key
```

---

### 4. Run the App

```bash
streamlit run app.py
```

---

## 🌐 Deployment

Deployed using **Streamlit Cloud**:

* Connect GitHub repository
* Select `app.py`
* Add API key via Secrets
* Deploy

---

## 🧠 Model Choices

### LLM: Gemini (via LangChain)

* Used for:

  * Decision making
  * Narrative generation
  * Risk evaluation

**Why Gemini?**

* Strong instruction following
* Suitable for interactive applications

---

### Embeddings: Gemini Embedding Model

* Used for RAG retrieval
* Converts text files into vector space

---

### Vector Database: FAISS / Chroma

* Stores indexed security documents
* Enables fast similarity search

---

## 🧩 Design Decisions

### 1. Separation of Concerns

* **ZONES → Movement logic (hard constraints)**
* **FILES → Real-world intelligence (soft context)**
* **LLM → Decision engine**

This ensures:

* No invalid movement
* Realistic reasoning
* Controlled AI behavior

---

### 2. RAG over Static Prompts

Instead of hardcoding rules:

* Context is dynamically retrieved
* Allows scalable and modular design

---

### 3. LLM as Evaluator, Not Controller

* LLM does NOT control movement
* It only evaluates actions

👉 Prevents hallucinated paths

---

### 4. Minimal State, Maximum Emergence

* Small set of rules
* Complex behavior emerges from interactions

---

## 📊 Evaluation & Performance Insights

### ⏱️ Latency

* Average response time: **7-15 seconds per move**
* Optimized using:

  * Cached vector store
  * Minimal prompt size

---

### 🎯 Accuracy

* Movement correctness: **100% (enforced by ZONES)**
* Item acquisition: deterministic via tags
* Reduced hallucination via strict prompt constraints

---

### 🔁 Robustness

* Handles invalid moves gracefully
* Prevents impossible actions
* Maintains consistent world state

---

### 📈 Observed Gameplay Metrics

* Average successful run: ~15–20 moves
* Heat typically ranges: **30–60% for optimal play**
* Failure rate increases sharply after heat >70%

---

## 🚧 Future Improvements

* Guard AI with state machines (patrol, alert, search)
* Time-based events and scheduling
* Multiple endings (stealth / aggressive / perfect run)
* Enhanced UI (map overlays, animations)
* Multiplayer / competitive mode

---

## 🏆 Hackathon Value

* Demonstrates **applied AI beyond chatbots**

* Combines:

  * RAG
  * Simulation systems
  * Interactive gameplay

* Fully deployable and extensible

---

## 👨‍💻 Authors

**Samarth Patidar, Krishna Toshniwwal, Venkatachala Darshan Gurumurthy**
