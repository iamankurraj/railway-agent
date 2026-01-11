import os, asyncio, logging
from fastapi.responses import JSONResponse
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from app.agent import app as langgraph_app
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("server")
app=FastAPI()
PUBLIC_DIR=Path(__file__).resolve().parent/"public"
app.mount("/static",StaticFiles(directory=PUBLIC_DIR),name="static")

class ChatInput(BaseModel):
    input:str
    thread_id:str|None=None

@app.get("/",response_class=HTMLResponse)
def index()->HTMLResponse:
    html_path=PUBLIC_DIR/"index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))

# @app.post("/invoke")
# async def invoke(payload: ChatInput):
#     text = (payload.input or "").strip()
#     logger.info("Got input: %s", text)

#     async def gen():
#         # ✅ Include both keys required by LangGraph
#         init_state: Dict[str, Any] = {
#             "input": text,
#             "messages": [HumanMessage(content=text)],
#         }

#         # Run LangGraph app in background thread
#         out = await asyncio.get_event_loop().run_in_executor(
#             None, langgraph_app.invoke, init_state
#         )

#         # Extract and stream response line-by-line
#         resp = out.get("nl_output", "(no output)")
#         for line in resp.split("\n"):
#             yield line + "\n"
#             await asyncio.sleep(0.01)

#     return StreamingResponse(gen(), media_type="text/plain")

@app.post("/invoke")
async def invoke(payload: ChatInput):
    text = (payload.input or "").strip()
    logger.info("Got input: %s", text)

    # Initialize graph state with both input and messages
    init_state: Dict[str, Any] = {
        "input": text,
        "messages": [HumanMessage(content=text)],
    }

    # Run the LangGraph pipeline
    out = await asyncio.get_event_loop().run_in_executor(
        None, langgraph_app.invoke, init_state
    )

    # If agent provided a clean JSON result
    if "result" in out:
        try:
            return JSONResponse(content=out["result"])
        except Exception:
            pass

    # If fallback: format natural language output
    resp = out.get("nl_output", "(no output)")
    return JSONResponse(content=[{"info": resp}])

if __name__=="__main__":
    import uvicorn;uvicorn.run(app,host="0.0.0.0",port=8002)
