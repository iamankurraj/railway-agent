# app/nodes/llm_node.py
import json
import re
import logging
from langchain_openai import ChatOpenAI
from app.state import AgentState

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """
You are the intent parser for a Smart Railway Query System.

Your ONLY job is to read a user's natural language query and return a JSON object.

Valid intents:
- "search_trains"      → user wants to find trains (most common)
- "price_query"        → user is asking about fares, cost, price, how much
- "schedule_query"     → user asking about timings, departure, arrival, schedule
- "availability_check" → user asking about seat availability, seats left
- "route_info"         → user asking about route, stops, which trains go where
- "general_info"       → user asking what this system does, help, examples
- "out_of_domain"      → completely unrelated to railways (e.g. weather, math)

IMPORTANT RULES:
- If the query mentions ANY of: train, from, to, route, between, fare, seat, class, ticket, book,
  depart, arrive, schedule, available, coach, sleeper, AC — use a railway intent, NOT out_of_domain.
- Be generous. "What trains go to Mumbai?" is search_trains, not out_of_domain.
- "How much does it cost from Pune to Delhi?" is price_query.
- "When does the train leave?" is schedule_query.
- Only use out_of_domain for things like "What is 2+2?" or "What's the weather?"

LANGUAGE CONVERSION:
- If the query is in Hindi/Marathi/any other language, ALWAYS convert city/station names to their ENGLISH equivalents.
- Examples:
  * "पुणे" (Marathi) → "pune"
  * "मुंबई" (Hindi/Marathi) → "mumbai"
  * "दिल्ली" (Hindi) → "delhi"
  * "बेंगलुरु" (Hindi/Marathi) → "bangalore"
  * "हैदराबाद" (Hindi) → "hyderabad"
  * "चेन्नई" (Hindi) → "chennai"
  * "कोलकाता" (Hindi) → "kolkata"
  * "जयपुर" (Hindi) → "jaipur"

Extract these fields (use null if not mentioned):
- intent: string (from list above)
- origin: string (city/station name in ENGLISH, lowercase) ← ALWAYS CONVERT
- destination: string (city/station name in ENGLISH, lowercase) ← ALWAYS CONVERT
- class_name: string (e.g. "sleeper", "ac 2-tier", "ac 3-tier", "ac chair car", "second sitting")
- min_price: number or null
- max_price: number or null
- date: string or null (e.g. "2025-11-05", or relative like "tomorrow", "today")
- train_number: string or null
- passenger_name: string or null

If the user is asking to make a reservation or confirm booking, use intent "book_train".

Return ONLY a valid JSON object, no explanation, no markdown.
"""

def run(state: AgentState) -> AgentState:
    """LLM reasoning node — interprets user intent and fills query params."""
    state_dict = state.dict()
    user_query = state.input or ""

    if not user_query:
        state.intent = "general_info"
        return state

    previous_response = state_dict.get("nl_output", "")
    previous_result = state_dict.get("result")
    followup_stage = state_dict.get("followup_stage")
    pending_booking = state_dict.get("pending_booking")
    assistant_content = ""
    if previous_response:
        assistant_content += f"Previous response: {previous_response}\n"
    if previous_result is not None:
        try:
            assistant_content += f"Previous result: {json.dumps(previous_result, ensure_ascii=False)}\n"
        except Exception:
            assistant_content += "Previous result: (unserializable)\n"
    if pending_booking:
        try:
            assistant_content += f"Pending booking: {json.dumps(pending_booking, ensure_ascii=False)}\n"
        except Exception:
            assistant_content += "Pending booking: (unserializable)\n"
    if followup_stage:
        assistant_content += f"Followup stage: {followup_stage}\n"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if assistant_content:
        messages.append({"role": "assistant", "content": assistant_content})
    messages.append({"role": "user", "content": user_query})

    try:
        response = llm.invoke(messages).content
        logger.info("LLM raw output: %s", response)

        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?|```", "", response).strip()
        match = re.search(r"\{.*\}", clean, re.S)
        parsed = json.loads(match.group(0)) if match else {}

    except Exception as e:
        logger.warning("LLM parse failed: %s", e)
        # Safe fallback — assume train search and let query_node handle it
        parsed = {"intent": "search_trains"}

    # Merge into state — LLM output wins over input_node's regex guesses
    # but we don't wipe params that input_node already found
    merged_params = {**state.params, **{
        k: v for k, v in parsed.items()
        if k not in ("intent",) and v is not None
    }}

    state.params = merged_params
    state.intent = parsed.get("intent", state.intent or "search_trains")

    print(f"LLM -> intent={state.intent}, params={state.params}")
    return state