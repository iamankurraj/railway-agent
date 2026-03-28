# 🚄 Smart Railway Query System - Complete Project Documentation

**Project Location:** `c:\Users\ankur\developement\railway-agent`  
**Type:** Full-Stack AI-Powered Railway Information System  
**Date:** March 28, 2026

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Pattern](#architecture--design-pattern)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Data Processing Pipeline](#data-processing-pipeline)
7. [Frontend Implementation](#frontend-implementation)
8. [Data Models](#data-models)
9. [Technical Deep Dive](#technical-deep-dive)
10. [Deployment & Execution](#deployment--execution)

---

## 🎯 Project Overview

### Purpose
A **multi-modal, AI-powered railway query assistant** that processes natural language queries (text/speech) and returns intelligent train search results with dynamic filtering, multilingual support, and fare information lookup.

### Key Features
- **Natural Language Processing (NLP):** Converts user questions into structured queries
- **Intent Detection:** Classifies user requests (search trains, price queries, schedule info, etc.)
- **Multi-channel Input:** Text input + Voice/Audio recognition
- **Smart Filtering:** Route-based, price-based, class-based filtering
- **Multilingual Support:** English, Hindi (हिन्दी), Marathi (मराठी) with dynamic translation
- **Fare Information:** Retrieves fare details with cost breakup
- **Responsive Web UI:** Chat interface with sidebar, language switching, history management

### Target Use Case
Indian railway ticket booking and information lookup system for travelers seeking train availability, schedules, fares, and seat classes between different stations/cities.

---

## 🏗️ Architecture & Design Pattern

### Design Pattern: **Agentic Workflow with State Graph**

This project uses **LangGraph** to implement a **Directed Acyclic Graph (DAG)** for processing user queries through multiple stages:

```
[Input Node] 
    ↓ (regex extraction)
[LLM Node] 
    ↓ (intent + param parsing)
    ↙              ↘
[Query Node]     [Fare Query Node]
    ↓              ↓
    ↘              ↙
[Response Node] 
    ↓ (formatting + translation)
[Output]
```

**Why this architecture?**
- **Modular:** Each node has a single responsibility
- **Flexible:** Conditional routing based on intent
- **Scalable:** Easy to add new nodes/intents
- **Maintainable:** Clear separation of concerns
- **Stateful:** Maintains conversation context through `AgentState`

### State Management
The `AgentState` object flows through the pipeline, accumulating data at each node:

```python
{
  messages: [HumanMessage],        # Conversation history
  input: str,                       # Current user query
  intent: str,                      # Detected intent (from LLM)
  params: Dict,                     # Extracted parameters
  result: Any,                      # Query results (trains/fares)
  nl_output: str,                   # Natural language response
  lang: str                         # Target language (en/hi/mr)
}
```

---

## 💻 Technology Stack

### Backend Framework
| Technology | Purpose | Version |
|-----------|---------|---------|
| **FastAPI** | Modern async Python web framework for REST APIs | Latest |
| **Uvicorn** | ASGI server for running FastAPI | Latest |
| **Pydantic** | Data validation using Python type hints | - |

### AI/ML & LLM
| Technology | Purpose | Details |
|-----------|---------|---------|
| **LangChain** | Framework for building LLM applications | Core abstraction layer |
| **LangGraph** | Agentic workflow execution engine | State graph + conditional routing |
| **OpenAI API** | Large Language Model inference | Uses `gpt-4o-mini` (cheaper, faster) |
| **LangChain-OpenAI** | Connector for OpenAI models | ChatOpenAI class |

### Audio/Voice Processing
| Technology | Purpose | Why Used? |
|-----------|---------|----------|
| **Faster-Whisper** | Speech-to-text transcription | Optimized Whisper variant (faster than OpenAI's) |
| **OpenAI-Whisper** | Fallback audio model | High-quality transcription |
| **SoundDevice** | Audio input capture | Cross-platform mic recording |
| **NumPy** | Numerical compute for audio arrays | Audio signal manipulation |
| **Torch** | Deep learning framework | Whisper model dependency |
| **Torchaudio** | Audio processing utilities | Whisper audio handling |

### Semantic Search & Embeddings
| Technology | Purpose | Details |
|-----------|---------|---------|
| **Sentence-Transformers** | Generate semantic embeddings | Optional for semantic search (not currently used actively) |
| **FAISS-CPU** | Facebook AI Similarity Search | Vector similarity matching (optional enhancement) |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Semantic markup structure |
| **CSS3** | Responsive styling with modern layout |
| **Vanilla JavaScript** | Client-side logic (no framework bloat) |

### Configuration & Utilities
| Technology | Purpose |
|-----------|---------|
| **Python-dotenv** | Load API keys from `.env` file securely |

---

## 📁 Project Structure

```
railway-agent/
│
├── 📄 server.py                    # FastAPI server entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 test.py                      # Test file (utility)
│
├── 🗂️  app/                        # Core application logic
│   ├── 📄 __init__.py
│   ├── 📄 agent.py                 # LangGraph DAG setup & compilation
│   ├── 📄 state.py                 # AgentState definition (Pydantic model)
│   ├── 📄 prompts.py               # System prompts for LLM
│   ├── 📄 audio_search.py          # Speech-to-text integration
│   ├── 📄 utils.py                 # Helper functions
│   │
│   ├── 🗂️  nodes/                  # Processing nodes (DAG nodes)
│   │   ├── 📄 input_node.py        # Regex-based parameter extraction
│   │   ├── 📄 llm_node.py          # Intent detection via LLM
│   │   ├── 📄 query_node.py        # Filter & search trains
│   │   ├── 📄 fare_query_node.py   # Fare lookup & filtering
│   │   └── 📄 response_node.py     # Response formatting + translation
│   │
│   └── 🗂️  tools/                  # Data processing utilities
│       ├── 📄 filters.py           # Filtering functions
│       └── 📄 json_loader.py       # JSON data loading with caching
│
├── 🗂️  data/                       # Static JSON datasets
│   ├── 📄 trains.json              # Train availability data
│   ├── 📄 getFare.json             # Fare information by train & class
│   └── 📄 searchTrain.json         # Alternative train dataset
│
├── 🗂️  public/                     # Frontend static files
│   ├── 📄 index.html               # Main HTML template
│   ├── 📄 script.js                # Client-side JavaScript
│   └── 📄 style.css                # UI styling
│
└── 🗂️  __pycache__/               # Compiled Python cache (auto-generated)
```

---

## 🔧 Core Components

### 1. **Server (server.py)**

**Framework:** FastAPI with Uvicorn

**Key Endpoints:**
- `GET /` - Serves the HTML frontend
- `POST /invoke` - Main API endpoint for query processing

**Processing Flow:**
```python
@app.post("/invoke")
async def invoke(payload: ChatInput):
    # 1. Extract user input & language preference
    init_state = {
        "input": text,
        "messages": [HumanMessage(content=text)],
        "lang": payload.lang
    }
    
    # 2. Execute LangGraph pipeline (async)
    out = await asyncio.get_event_loop().run_in_executor(
        None, langgraph_app.invoke, init_state
    )
    
    # 3. Return results as JSON
    return JSONResponse(content=out["result"])
```

**Why async/executor?**
- FastAPI demands non-blocking I/O
- LangGraph's `.invoke()` is blocking/synchronous
- `executor` runs it in a thread pool without blocking the event loop

---

### 2. **Agent/Orchestrator (agent.py)**

**Framework:** LangGraph StateGraph

**Graph Definition:**
```
START
↓
input_node (regex extraction)
↓
llm_node (intent parsing via LLM)
↓
[Conditional Routing]
├─→ price_query intent ──→ fare_query_node
├─→ other intents ────────→ query_node
↓
respond_node (formatting + translation)
↓
END
```

**Key Code:**
```python
def build_graph():
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("input", input_node.run)
    graph.add_node("llm", llm_node.run)
    graph.add_node("query", query_node.run)
    graph.add_node("fare_query", fare_query_node.run)
    graph.add_node("respond", response_node.run)
    
    # Define edges
    graph.set_entry_point("input")
    graph.add_edge("input", "llm")
    
    # Conditional routing function
    graph.add_conditional_edges(
        "llm",
        route_to_query_or_fare,  # Decides next node
        {"fare_query": "fare_query", "query": "query"}
    )
    
    return graph.compile()
```

**Conditional Routing Logic:**
```python
def route_to_query_or_fare(state):
    intent = getattr(state, "intent", "search_trains")
    if intent == "price_query":
        return "fare_query"  # Go to fare lookup
    else:
        return "query"       # Go to train search
```

---

### 3. **State Definition (state.py)**

**Framework:** Pydantic BaseModel

```python
class AgentState(BaseModel):
    messages: List[BaseMessage] = []      # LangChain message history
    input: str = ""                        # Current user query
    intent: str = ""                       # Detected intention (LLM output)
    params: Dict[str, Any] = {}           # Extracted parameters
    result: Any = None                     # Search results
    nl_output: str = ""                    # Natural language response
    lang: str = "en"                       # Target language
```

**Why Pydantic?**
- Type validation at runtime
- Auto schema generation for FastAPI
- Easy serialization/deserialization
- Performance optimized

---

### 4. **Input Node (input_node.py)**

**Purpose:** Extract railway-specific parameters using regex patterns

**What it extracts:**
- `origin`: Departure city (e.g., "Pune")
- `destination`: Arrival city (e.g., "Mumbai")
- `class_name`: Train class (e.g., "AC 2-tier", "Sleeper")
- `min_price`: Price floor (e.g., "above ₹1000")
- `max_price`: Price ceiling (e.g., "below ₹5000")

**Known Cities Database:**
```python
KNOWN_CITIES = [
    "new delhi", "old delhi", "delhi", "mumbai", "pune", "chennai",
    "kolkata", "bangalore", "hyderabad", "ahmedabad", ...
]
```

**Regex Patterns Used:**
```
Pattern 1: "from {origin} to {destination}"
Pattern 2: "from {origin}" (destination only)
Pattern 3: "to {destination}" (origin only)
Pattern 4: "trains {class_name}" (class extraction)
Pattern 5: "above ₹{min_price}" / "below ₹{max_price}"
```

**Example Processing:**
```
Input: "sleeper trains from Pune to Mumbai under ₹5000"

Output: {
  "origin": "Pune",
  "destination": "Mumbai",
  "class_name": "Sleeper",
  "min_price": None,
  "max_price": 5000
}
```

---

### 5. **LLM Node (llm_node.py)**

**Framework:** LangChain OpenAI ChatOpenAI

**Model:** `gpt-4o-mini` (smaller, faster, cheaper variant of GPT-4)

**Purpose:** 
1. Detect intent from free-form text
2. Extract structured parameters with **language conversion**
3. Override/merge with regex-extracted params

**Intent Classification:**
```
- "search_trains"         → Find trains between cities
- "price_query"          → Asking about fares/costs
- "schedule_query"       → Asking about departure/arrival times
- "availability_check"   → Asking about seat counts
- "route_info"           → Asking about stops, which trains go where
- "general_info"         → Help, examples, how to use system
- "out_of_domain"        → Unrelated queries (weather, math, etc.)
```

**Language Conversion:**
```
"पुणे" (Marathi) → "pune"
"मुंबई" (Hindi)  → "mumbai"
"दिल्ली" (Hindi) → "delhi"
```

**System Prompt Strategy:**
- Clear definition of each intent
- Examples for disambiguation
- Language conversion instructions
- JSON-only output (no explanations)

**Output Format:**
```json
{
  "intent": "price_query",
  "origin": "pune",
  "destination": "mumbai",
  "class_name": "sleeper",
  "min_price": null,
  "max_price": 5000,
  "date": null,
  "train_number": null
}
```

**Processing Steps:**
```python
# 1. Call OpenAI LLM
response = llm.invoke(messages)

# 2. Extract JSON (handles markdown fences)
clean = re.sub(r"```(?:json)?|```", "", response)
parsed = json.loads(match.group(0))

# 3. Merge with existing params (LLM output wins)
merged_params = {**state.params, **parsed}

# 4. Update state
state.intent = parsed.get("intent", "search_trains")
state.params = merged_params
```

---

### 6. **Query Node (query_node.py)**

**Purpose:** Main train search engine with filtering

**Data Source:** `data/trains.json` (loaded via cache)

**Processing Logic:**

```python
# 1. Handle special intents
if intent == "general_info":
    return help_message()
if intent == "out_of_domain":
    return out_of_domain_message()

# 2. Require at least one route parameter
if not origin and not destination:
    return "Please specify at least one city"

# 3. Load full train dataset
data = load_json("trains.json")["trains"]

# 4. Apply filters sequentially
if origin and destination:
    results = trains_between(results, origin, destination)
elif origin:
    results = [t for t in results if t["origin"].lower() == origin.lower()]
elif destination:
    results = [t for t in results if t["destination"].lower() == destination.lower()]

if class_name:
    results = filter_by_class_name(results, class_name)

if min_price:
    results = filter_by_min_price(results, min_price)

if max_price:
    results = [t for t in results if any(c["price"] <= max_price for c in t["classes"])]

# 5. Limit results to top 10 for UI performance
results = results[:10]
```

**Filter Functions (tools/filters.py):**

```python
def trains_between(data, origin, destination):
    """Case-insensitive matching"""
    return [t for t in data 
            if t["origin"].lower() == origin.lower() 
            and t["destination"].lower() == destination.lower()]

def filter_by_class_name(data, class_name):
    """Fuzzy class matching"""
    return [t for t in data 
            if any(class_name.lower() in c["class_name"].lower() 
                   for c in t["classes"])]

def filter_by_min_price(data, min_price):
    """At least one class meets minimum price"""
    return [t for t in data 
            if any(c["price"] >= min_price for c in t["classes"])]
```

**Natural Language Output:**
```
"Found 3 train(s) from Pune to Mumbai · Sleeper · above ₹500 · below ₹2000."
```

---

### 7. **Fare Query Node (fare_query_node.py)**

**Purpose:** Lookup fare information with cost breakup

**Data Source:** `data/getFare.json`

**Processing Logic:**
```python
# 1. Parse fare category (general, tatkal)
if "tatkal" in text:
    category = "tatkal"
else:
    category = "general"

# 2. Extract class type (1A, 2A, 3A, SL, 2S)
for c in ["1a", "2a", "3a", "sl", "2s"]:
    if c in text:
        class_type = c.upper()

# 3. Extract route from "from X to Y" pattern
# 4. Filter fares matching all criteria
# 5. Build result with cost breakup
```

**Output Structure:**
```json
{
  "trainNo": "40930",
  "category": "General",
  "classType": "2S",
  "fare": 637,
  "breakup": [
    {"title": "Base Charges", "cost": 619},
    {"title": "Reservation Charges", "cost": 50},
    {"title": "Total Amount", "cost": 637}
  ]
}
```

---

### 8. **Response Node (response_node.py)**

**Purpose:** Format results and handle multilingual translation

**Processing Steps:**

```python
# 1. Convert Pydantic state → dict
state_dict = state.dict()

# 2. Build natural language summary if missing
if not nl_output:
    nl_output = f"Found {len(result)} matching item(s)."

# 3. Dynamic LLM translation (if lang != "en")
if lang in ["hi", "mr"]:
    # Call GPT to translate both nl_output AND all JSON values
    translation_prompt = (
        f"Translate to {lang_name}.\n"
        f"1. Translate nl_output.\n"
        f"2. Translate JSON string values (not keys).\n"
        f"Return valid JSON with 'nl_output' and 'result' keys."
    )
    
    translated = llm.invoke(translation_prompt + json_payload)
    nl_output = translated["nl_output"]
    result = translated["result"]

# 4. Return formatted state
state.nl_output = nl_output
state.result = result
```

**Translation Example:**
```
Input (English):
{
  "nl_output": "Found 2 trains from Pune to Mumbai",
  "result": [{"train_name": "Deccan Queen", ...}]
}

Output (Hindi):
{
  "nl_output": "पुणे से मुंबई तक 2 ट्रेनें मिलीं",
  "result": [{"train_name": "डेक्कन क्वीन", ...}]
}
```

**Why GPT for Translation?**
- Contextual understanding (preserves technical correctness)
- Handles abbreviations intelligently (e.g., "AC 2-tier" → "AC 2-tier" not translated)
- Better than literal/statistical translation
- Cost-effective with `gpt-4o-mini`

---

### 9. **Audio/Speech Processing (audio_search.py)**

**Framework:** Faster-Whisper (optimized STT)

**Purpose:** Convert speech to text for voice queries

**Code:**
```python
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000  # 16kHz standard audio
CHUNK_SECONDS = 4    # Record 4-second chunks

model = WhisperModel("base", device="cpu")  # Base model, CPU inference

def listen_once():
    print("Speak your query...")
    
    # 1. Record audio from microphone
    audio = sd.rec(
        int(SAMPLE_RATE * CHUNK_SECONDS),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()  # Block until recording complete
    
    # 2. Transcribe with Whisper
    segments, _ = model.transcribe(audio, language="en")
    
    # 3. Combine segments into text
    text = " ".join([seg.text for seg in segments]).strip()
    
    return text
```

**Workflow:**
```
🎤 Microphone Input (4 sec, 16kHz)
    ↓
Faster-Whisper STT (Base model)
    ↓
Text Output (e.g., "trains from Pune to Mumbai")
    ↓
Process same as text input (/invoke)
```

**Technical Details:**
- **Sample Rate:** 16kHz (optimal for Whisper)
- **Model:** "base" (small, ~140MB, fast on CPU)
- **Device:** CPU (no GPU required — accessible)
- **Language:** Auto-detects or specify "en"

---

### 10. **Data Loading & Caching (tools/json_loader.py)**

**Purpose:** Efficient JSON dataset loading with caching

**Implementation:**
```python
from functools import lru_cache

@lru_cache(maxsize=32)
def load_json(rel_path: str) -> Any:
    """
    Load JSON from /data directory with in-memory caching.
    Uses LRU cache to avoid repeated disk I/O.
    """
    base_dir = get_base_dir()
    file_path = (base_dir / "data" / rel_path).resolve()
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
```

**Benefits:**
- **@lru_cache:** First call reads disk, subsequent calls served from memory
- **maxsize=32:** Caches up to 32 unique files (overkill for 3 files, but scalable)
- **Performance:** 10,000x faster than repeated disk reads

**Usage:**
```python
data = load_json("trains.json")     # Disk read (slow)
data = load_json("trains.json")     # Memory cache (instant)
```

---

## 📊 Data Processing Pipeline

### End-to-End Query Flow

```
┌─────────────────────────────────────────────────────────────┐
│  USER QUERY (Text or Voice)                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │ Audio Node (Optional)  │
        │ (Speech → Text via     │
        │  Faster-Whisper)       │
        └────────────┬───────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │ Input Node             │
        │ (Regex Extraction)     │
        │                        │
        │ Extracts:              │
        │ - origin/destination   │
        │ - class_name           │
        │ - price range          │
        └────────────┬───────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │ LLM Node               │
        │ (GPT-4o-mini)          │
        │                        │
        │ Detects:               │
        │ - Intent               │
        │ - Parameters (refined) │
        │ - Language conversion  │
        └────────────┬───────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ↓                     ↓
  ┌─────────────────┐    ┌──────────────────┐
  │ Query Node      │    │ Fare Query Node  │
  │ (If search)     │    │ (If price_query) │
  │                 │    │                  │
  │ Loads:          │    │ Loads:           │
  │ trains.json     │    │ getFare.json     │
  │                 │    │                  │
  │ Filters by:     │    │ Filters by:      │
  │ - Route         │    │ - Train number   │
  │ - Class         │    │ - Class type     │
  │ - Price         │    │ - Fare category  │
  └────────┬────────┘    └────────┬─────────┘
           │                      │
           └──────────┬───────────┘
                      │
                      ↓
        ┌────────────────────────┐
        │ Response Node          │
        │ (Formatting + Trans.)  │
        │                        │
        │ If lang != "en":       │
        │ - Call GPT translate   │
        │ - Convert all strings  │
        │   to target language   │
        └────────────┬───────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │ JSON Response          │
        │                        │
        │ {                      │
        │   result: [...],       │
        │   nl_output: "..."     │
        │ }                      │
        └────────────────────────┘
```

### Example Walkthrough

**Input:** "Show me sleeper trains from Pune to Mumbai under ₹2000"

**Node 1: Input Node**
```python
{
  "origin": "pune",
  "destination": "mumbai",
  "class_name": "sleeper",
  "max_price": 2000
}
```

**Node 2: LLM Node**
```python
# LLM recognizes search_trains intent, confirms params
{
  "intent": "search_trains",
  "origin": "pune",
  "destination": "mumbai",
  "class_name": "sleeper",
  "max_price": 2000
}
```

**Node 3: Query Node (routed here)**
```python
# Load trains.json, filter:
# 1. origin='pune' AND destination='mumbai'
# 2. class has 'sleeper'
# 3. Any sleeper class < ₹2000

results = [
  {
    "train_id": "T50",
    "train_name": "Deccan Queen",
    "origin": "Pune",
    "destination": "Mumbai",
    "classes": [
      {"class_name": "Sleeper", "price": 1200},
      {"class_name": "AC 2-Tier", "price": 2500}
    ]
  },
  {
    "train_id": "T51",
    "train_name": "Express Train",
    "origin": "Pune",
    "destination": "Mumbai", 
    "classes": [
      {"class_name": "Sleeper", "price": 1050}
    ]
  }
]

nl_output = "Found 2 train(s) from Pune to Mumbai · Sleeper · below ₹2000."
```

**Node 4: Response Node**
```python
# Lang = "en" → no translation needed
# Return formatted JSON

{
  "result": [...],  # 2 trains
  "nl_output": "Found 2 train(s) from Pune to Mumbai..."
}
```

---

## 🎨 Frontend Implementation

### HTML Structure (public/index.html)

```html
<body>
  <!-- Sidebar: Chat history -->
  <div id="sidebar">
    <h3>🚄 Railway AI</h3>
    <button id="new-chat-btn">+ New Chat</button>
    <div id="history-groups"></div>
  </div>

  <!-- Main App -->
  <div id="app">
    <h1 id="title">🚄 SMART RAILWAY QUERY SYSTEM</h1>
    
    <!-- Language Switcher -->
    <div>
      <button onclick="setLanguage('en')">English</button>
      <button onclick="setLanguage('hi')">हिन्दी</button>
      <button onclick="setLanguage('mr')">मराठी</button>
    </div>

    <!-- Chat Interface -->
    <div id="chat-box">
      <div id="messages"></div>
      
      <form id="form">
        <input id="input" type="text" placeholder="Ask about trains...">
        <button type="button" id="mic-btn">🎙</button>
        <button type="submit" id="ask-btn">Ask</button>
      </form>
    </div>
  </div>
</body>
```

### JavaScript Features (public/script.js)

**Translations Dictionary:**
```javascript
const translations = {
  en: {
    title: "🚄 SMART RAILWAY QUERY SYSTEM",
    placeholder: "Ask about trains...",
    ...
  },
  hi: {
    title: "🚄 स्मार्ट रेलवे पूछताछ प्रणाली",
    placeholder: "ट्रेनों के बारे में पूछें...",
    ...
  },
  mr: {
    title: "🚄 स्मार्ट रेल्वे चौकशी प्रणाली",
    placeholder: "रेल्वेबद्दल विचारा...",
    ...
  }
};
```

**API Integration:**
```javascript
async function sendMessage() {
  const text = document.getElementById("input").value;
  
  const response = await fetch("/invoke", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      input: text,
      lang: currentLang,
      thread_id: null
    })
  });
  
  const data = await response.json();
  displayResults(data);
}
```

**UI Features:**
- **Sidebar Toggle:** Hamburger button for responsive design
- **Language Switching:** Dynamic translation on language change
- **Chat History:** Stores conversations in localStorage
- **Mic Integration:** Voice input button triggers speech recognition
- **Responsive Tables:** Displays train results in formatted table

---

## 📊 Data Models

### trains.json Structure

```json
{
  "trains": [
    {
      "train_id": "T1000",
      "train_name": "Gateway Mail",
      "origin": "Hyderabad",
      "destination": "Jaipur",
      "date": "2026-05-22",
      "departure_time": "19:45",
      "arrival_time": "12:45",
      "classes": [
        {
          "class_name": "AC 1-Tier",
          "price": 4147,
          "seats_available": 186
        },
        {
          "class_name": "Sleeper",
          "price": 606,
          "seats_available": 119
        }
      ]
    }
  ]
}
```

### getFare.json Structure

```json
{
  "fares": [
    {
      "trainNo": "40930",
      "fromStationCode": "HWH",
      "toStationCode": "MAS",
      "data": {
        "general": [
          {
            "classType": "2S",
            "fare": 637,
            "breakup": [
              {"title": "Base Charges", "cost": 619},
              {"title": "Reservation Charges", "cost": 50},
              {"title": "Total Amount", "cost": 637}
            ]
          }
        ],
        "tatkal": [...]
      }
    }
  ]
}
```

---

## 🔬 Technical Deep Dive

### 1. Async/Await & Event Loop Management

**Problem:** LangGraph's `.invoke()` is synchronous (blocking).

**Solution:** Use thread executor to run in background thread.

```python
@app.post("/invoke")
async def invoke(payload: ChatInput):
    # FastAPI runs in async event loop
    
    # Run synchronous LangGraph in thread pool
    out = await asyncio.get_event_loop().run_in_executor(
        None,                    # Use default executor
        langgraph_app.invoke,   # Blocking function
        init_state              # Arguments
    )
    
    return JSONResponse(content=out["result"])
```

**Why this works:**
- FastAPI event loop doesn't block on I/O
- Thread pool handles CPU-bound work
- User doesn't wait for long-running graph

---

### 2. LLM Prompt Engineering

**System Prompt Strategy:**

```
1. Clear Intent Definitions
   - List all valid intents upfront
   
2. Disambiguation Rules
   - How to handle edge cases
   - "Be generous" approach (prefer railway intent)
   
3. Language Conversion Examples
   - Case-by-case Hindi/Marathi → English mappings
   
4. Strict Output Format
   - "Return ONLY valid JSON, no explanation"
   - Prevents markdown wrapping
```

**Error Handling:**

```python
try:
    clean = re.sub(r"```(?:json)?|```", "", response)
    parsed = json.loads(json_match.text)
except:
    # Fallback to safe defaults
    parsed = {"intent": "search_trains"}
```

---

### 3. Regex Pattern Design

**Complexity Levels:**

```python
# Level 1: Exact phrase matching
r"from\s+(.+?)\s+to\s+(.+?)" 

# Level 2: Case-insensitive with fuzzy alternation
r"\b(ac\s?1\s?-?\s?tier|ac\s?2\s?-?\s?tier|sleeper)\b"

# Level 3: Prioritize known cities (longest match)
sorted(KNOWN_CITIES, key=len, reverse=True)  # "new delhi" before "delhi"

# Level 4: Handle currency symbols
r"(?:₹|rs|\$)\s*(\d+)"
```

---

### 4. Semantic Search Architecture (Optional Future)

**Current:** Regex + LLM + exact keyword matching

**Future (Unused Currently):**
```python
# Generate embeddings for city names
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create FAISS index for similarity search
import faiss
embeddings = model.encode(KNOWN_CITIES)
faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
faiss_index.add(embeddings)

# Query with fuzzy matching
query_embedding = model.encode("Bangalore")
_, indices = faiss_index.search(query_embedding, k=3)
# Returns top-3 closest city names
```

**Benefits:** Handles typos, abbreviations, accent variations.

---

### 5. Caching Strategy

**Multi-Layer Caching:**

```python
# Layer 1: In-memory LRU cache (JSON files)
@lru_cache(maxsize=32)
def load_json(rel_path):
    return json.load(open(...))

# Layer 2: LLM response caching (implicit in OpenAI API)
# - Repeated queries benefit from token caching

# Layer 3: Frontend localStorage
localStorage.setItem("lang", currentLang)
localStorage.getItem("lang")
```

---

### 6. Multilingual Translation Pipeline

**Challenges:**
1. Only translate values, not JSON keys
2. Preserve special formatting (₹, numbers, abbreviations)
3. Handle abbreviations intelligently

**Solution:**
```python
translation_prompt = (
    "REQUIREMENTS:\n"
    "- Translate ONLY string values, NOT keys\n"
    "- Keep figures, currency (₹), and abbreviations unchanged\n"
    "- Keep 'AC 2-tier' as 'AC 2-tier' (technical term)\n"
    "- Translate natural language descriptions\n"
    "\n"
    "Target language: Hindi\n"
    "Input JSON:\n" + json_payload
)

response = llm.invoke(translation_prompt)
```

---

## 🚀 Deployment & Execution

### Running the Server

**Prerequisites:**
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
```

**Start Server:**
```bash
python server.py
# or
uvicorn app:app --host 0.0.0.0 --port 8002
```

**Access URL:**
```
http://localhost:8002
```

### Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=sk-...
```

Loaded via `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Testing

**Manual Test (Text):**
```bash
curl -X POST http://localhost:8002/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": "trains from Pune to Mumbai",
    "lang": "en"
  }'
```

**Voice Test:**
```python
from app.audio_search import listen_once
from app.agent import invoke_text

spoken_text = listen_once()
result = invoke_text(spoken_text)
print(result)
```

### Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Regex extraction | ~5ms | Input node |
| LLM inference | 500-1500ms | Network + model |
| Dataset filtering | 10-50ms | Depends on dataset size |
| Translation (if needed) | 500-1000ms | Extra LLM call |
| **Total request** | 1-3 seconds | Typical end-to-end |

### Scaling Strategies

1. **Caching:** Reuse LLM responses for identical queries
2. **Async queues:** Queue requests during traffic spikes
3. **Database:** Replace JSON files with PostgreSQL for 1M+ trains
4. **Distributed:** Run multiple Uvicorn workers behind Nginx
5. **Vector DB:** Use embedding indexes for semantic search

---

## 📚 Technical Terminology Reference

| Term | Meaning |
|------|---------|
| **DAG** (Directed Acyclic Graph) | Processing pipeline where data flows one direction, no cycles |
| **LLM** (Large Language Model) | GPT-4, Claude, etc. — neural networks pretrained on huge text |
| **Prompt Engineering** | Crafting system/user prompts to guide LLM behavior |
| **Intent Detection** | Classifying user queries into categories |
| **Regex** (Regular Expression) | Pattern matching in strings (e.g., `/from (.+?) to (.+?)/`) |
| **Async/Await** | Non-blocking I/O pattern in Python (prevents thread blocking) |
| **Pydantic** | Data validation library using type hints |
| **LRU Cache** | Least-Recently-Used cache (auto-evicts old entries) |
| **STT** (Speech-to-Text) | Audio transcription (Whisper model) |
| **Embedding** | Vector representation of text (for semantic similarity) |
| **FAISS** | Facebook AI Similarity Search — fast vector indexing |
| **JSON** | JavaScript Object Notation — human-readable data format |
| **RESTful API** | Web API using HTTP methods (GET, POST, etc.) |
| **CORS** | Cross-origin resource sharing — allows frontend to call backend |

---

## 🎯 Summary Table

| Component | Technology | Purpose | Performance |
|-----------|-----------|---------|-------------|
| **Server** | FastAPI + Uvicorn | REST API + static files | ~1-3 sec/request |
| **Orchestration** | LangGraph | State graph + routing | ~1-2 sec |
| **Intent Parsing** | GPT-4o-mini | LLM reasoning | ~500-1500ms |
| **Search** | Python (JSON + regex) | Train filtering | ~10-50ms |
| **Translation** | GPT-4o-mini | Multilingual | ~500-1000ms |
| **Audio Input** | Faster-Whisper | Speech recognition | ~2-5 sec |
| **Frontend** | HTML/CSS/JS | Chat UI | Real-time |
| **Data** | JSON static files | Train/fare database | In-memory after cache |

---

**End of Documentation**

*Created: March 28, 2026*  
*Project: Smart Railway Query System*  
*Author: Railway Agent Team*
