# app/state.py
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

class AgentState(BaseModel):
    messages: List[BaseMessage] = []
    input: str = ""
    intent: str = ""
    params: Dict[str, Any] = {}
    result: Any = None
    nl_output: str = ""
    lang: str = "en"
    selected_train: Optional[Dict[str, Any]] = None
    pending_booking: Optional[Dict[str, Any]] = None
    followup_stage: Optional[str] = None