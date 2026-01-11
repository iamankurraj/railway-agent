# app/nodes/llm_node.py
import json, re, logging
from langchain_openai import ChatOpenAI
from app.state import AgentState

from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)

# Initialize OpenAI model (you can use gpt-4o-mini or gpt-4-turbo)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run(state: AgentState) -> AgentState:
    """LLM reasoning node — interprets user intent and fills query params."""
    user_query = state.input or ""
    system_prompt = (
        "You are part of a Smart Railway Query System. "
        "Understand what the user wants and convert it into structured JSON. "
        "Return ONLY JSON with these keys: intent, origin, destination, class_name, min_price."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    try:
        response = llm.invoke(messages).content
        logger.info("🧠 LLM raw output: %s", response)

        parsed = json.loads(re.search(r"\{.*\}", response, re.S).group(0))
    except Exception as e:
        logger.warning("⚠️ Failed to parse LLM output: %s", e)
        parsed = {"intent": "search_trains", "origin": None, "destination": None}

    # Merge LLM output into agent state
    state.params.update(parsed)
    state.intent = parsed.get("intent", "search_trains")
    print(f"🧠 LLM interpreted intent → {parsed}")
    return state
