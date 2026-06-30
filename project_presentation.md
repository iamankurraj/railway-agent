# Railway Agent Project Presentation

This document is a complete, non-technical walkthrough of the `railway-agent` project.
It is designed as a slide-style presentation in Markdown with clear explanations, architecture depth, and pros/cons.

---

## Slide 1: Title

**Smart Railway Query System**

- A demo-ready AI-based assistant for Indian railway travel queries.
- Helps users search trains, check fares, reserve seats, and download booking receipts.
- Built as a full-stack project with Python backend and browser-based frontend.

---

## Slide 2: What the Project Does

- Lets a user ask natural language questions about trains.
- Supports queries like:
  - "When does the Deccan Queen depart?"
  - "Show sleeper trains from Pune to Mumbai."
  - "Book an AC 2-tier seat on train 1005."
- Produces results in a friendly, chat-style interface.
- Simulates booking creation and provides calendar and PDF exports.

---

## Slide 3: Who It Helps

- Travelers who want train schedules and fare details.
- Non-technical users who prefer asking questions in plain language.
- Demo audiences exploring how AI can help booking assistants.

---

## Slide 4: Project Structure

### Main folders and files

- `server.py`
  - The backend server and the main API entry point.
- `app/`
  - Core application logic, including AI pipeline nodes.
- `data/`
  - Static JSON datasets for trains and fares.
- `public/`
  - Frontend user interface files.
- `requirements.txt`
  - Python packages required for the app.

---

## Slide 5: Backend Overview

- Uses **FastAPI** to handle web requests.
- Exposes:
  - `/invoke` for natural language query processing.
  - `/booking` to simulate booking a train.
  - `/booking/{pnr}/export` for calendar export.
  - `/booking/{pnr}/pdf` for PDF export.
- Keeps booking state in `data/bookings.json`.

---

## Slide 6: Frontend Overview

- Simple browser UI built with HTML, CSS, and JavaScript.
- Lets users:
  - enter a text query,
  - view train search results,
  - choose class options,
  - reserve a seat,
  - download booking exports.
- Includes language switching between English, Hindi, and Marathi.

---

## Slide 7: What `app/` Contains

### Main responsibilities

- `app/agent.py`
  - Defines the AI pipeline and how data flows.
- `app/state.py`
  - Holds the conversation and booking state.
- `app/prompts.py`
  - Contains prompts for the AI model.
- `app/audio_search.py`
  - Supports speech input (optional). 
- `app/utils.py`
  - Utility helpers used by the backend.
- `app/nodes/`
  - Individual processing steps, each performing one task.

---

## Slide 8: Core Pipeline Nodes

### Processing nodes in `app/nodes/`

- `input_node.py`
  - Extracts route, train, class, price, date, and booking intent from plain text.
- `llm_node.py`
  - Uses the language model to decide the user’s intent.
- `query_node.py`
  - Searches trains and filters by class or price.
- `fare_query_node.py`
  - Handles explicit fare queries.
- `booking_flow_node.py`
  - Manages multi-step booking and missing information.
- `response_node.py`
  - Converts results into readable output for the user.

---

## Slide 9: How the System Understands Queries

- User input is first analyzed by `input_node.py`.
- The system extracts key values such as:
  - origin and destination,
  - class type,
  - price limits,
  - date,
  - train name or number.
- Examples of extracted data:
  - "Pune to Mumbai"
  - "AC 2-tier"
  - "tomorrow"

---

## Slide 10: Language Model Role

- `llm_node.py` sends the processed text to an AI model.
- The model decides whether the user wants:
  - a train search,
  - a fare lookup,
  - a schedule answer,
  - a booking action.
- This is the smart decision-making stage.

---

## Slide 11: Search and Query Handling

- `query_node.py` performs the actual train search.
- It loads train data from `data/trains.json`.
- It can:
  - find matching trains,
  - filter by ticket class,
  - sort by route and price,
  - create a disambiguation prompt when multiple trains match.

---

## Slide 12: Booking Flow

- `booking_flow_node.py` carries booking intent through the system.
- It handles:
  - train selection,
  - missing booking fields,
  - multi-step follow-up questions,
  - booking confirmation.
- If data is incomplete, the assistant asks for:
  - class or date,
  - passenger name.

---

## Slide 13: Booking Simulation and Persistence

- `booking_node.py` simulates booking creation.
- It updates seat availability in `data/trains.json`.
- It stores bookings in `data/bookings.json`.
- Each booking gets a generated PNR.
- Users can download:
  - a calendar event file (`.ics`),
  - a PDF booking confirmation.

---

## Slide 14: Architecture in Depth

### System flow summary

1. User submits a query through the browser.
2. The browser calls `/invoke` on the backend.
3. Backend builds an `AgentState` object.
4. The agent pipeline executes nodes in sequence.
5. The language model interprets intent.
6. The appropriate search or booking path runs.
7. Final response is returned as JSON.
8. Frontend renders results or prompts the user for follow-up.

---

## Slide 15: How State is Managed

- Every interaction goes through `AgentState`.
- The state carries:
  - the user message,
  - the detected intent,
  - extracted parameters,
  - selected train details,
  - pending booking data,
  - follow-up stage information.
- This allows the assistant to continue a conversation naturally.

---

## Slide 16: Advantages of the System

- **User-friendly:** natural language input feels conversational.
- **Modular:** each node has a single responsibility.
- **Multi-step booking:** supports follow-up questions for missing data.
- **Export-friendly:** booking receipts available as PDF and calendar file.
- **Quick demo-ready:** simple UI with practical functionality.
- **Flexible querying:** supports train names, routes, classes, and price filters.

---

## Slide 17: Disadvantages and Limitations

- **Not a live booking system:** it simulates bookings using static JSON data.
- **Model dependency:** AI parsing depends on OpenAI or similar service availability.
- **Limited dataset:** only the trains and fares stored in `data/` are available.
- **No real payment support:** booking is simulated without actual ticket purchase.
- **Basic error handling:** some edge cases may return generic messages.
- **UI is simple:** good for demos, but not a full production portal.

---

## Slide 18: Future Improvements

- Connect to a real train booking API.
- Add user authentication and saved profiles.
- Support richer voice input and mobile-friendly UI.
- Improve train schedule accuracy with real-time data.
- Add advanced dialogue memory for longer conversations.
- Build a richer dashboard for booking history and analytics.

---

## Slide 19: File and Folder Summary

### Root files
- `server.py` — main web server.
- `requirements.txt` — required Python packages.
- `test.py` — utility or test script.
- `readme.md` — project documentation.

### `app/`
- `agent.py` — AI workflow and graph definition.
- `state.py` — shared state object for conversations.
- `prompts.py` — AI prompt templates.
- `audio_search.py` — speech recognition support.
- `utils.py` — helper utilities.

### `app/nodes/`
- Each file is a processing step in the AI workflow.
- Responsible for parsing, intent detection, search, booking, and response formatting.

### `data/`
- `trains.json` — available trains, schedules, and classes.
- `getFare.json` — fare details used for price queries.
- `searchTrain.json` — additional train search dataset.
- `bookings.json` — simulated booking records.

### `public/`
- `index.html` — browser interface.
- `script.js` — client-side logic and result rendering.
- `style.css` — visual styling.

---

## Slide 20: Non-Technical Summary

- This project is a friendly demo assistant for train travel.
- It takes questions like "Which train should I take from Pune to Mumbai?"
- It uses AI to understand what the user wants.
- It shows results, handles simple booking steps, and creates a booking ticket.
- It is built for demonstration, learning, and early prototypes.

---

## Slide 21: Key Takeaway

- The system demonstrates how AI can turn normal speech or text into a travel planning assistant.
- It is a strong demo of AI-driven conversation, search, and booking flow.
- The architecture makes it easy to extend with more capabilities later.

---

## Slide 22: How to Run It

- Create a Python environment and install packages from `requirements.txt`.
- Run `server.py`.
- Open the browser at the server URL.
- Type a train query and interact with the assistant.

---

## Slide 23: Why This is a Good Demo

- Combines realistic booking concepts with AI-driven language understanding.
- Has visual output and actionable buttons.
- Includes a clear backend-to-frontend flow.
- Offers realistic booking-like exports without real payment risk.
- Shows how static data and AI can create a useful prototype.

---

## Slide 24: Final Notes

- The project is ideal for a product pitch or rapid prototype.
- It is not production-ready, but it shows the full concept clearly.
- Additional work can make it real by plugging in live booking APIs and better UI polish.

---

*End of presentation summary.*
