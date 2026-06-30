import os, asyncio, logging
from datetime import datetime
from fastapi.responses import JSONResponse
from typing import Dict, Any
from fastapi.responses import Response
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from app.agent import app as langgraph_app
from langchain_core.messages import HumanMessage
from app.nodes import booking_node
from io import BytesIO

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("server")
app=FastAPI()
PUBLIC_DIR=Path(__file__).resolve().parent/"public"
app.mount("/static",StaticFiles(directory=PUBLIC_DIR),name="static")

class ChatInput(BaseModel):
    input:str
    thread_id:str|None=None
    lang:str="en"

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

thread_states: Dict[str, Dict[str, Any]] = {}

@app.post("/invoke")
async def invoke(payload: ChatInput):
    text = (payload.input or "").strip()
    thread_id = payload.thread_id or "default"
    logger.info("Got input: %s (thread=%s)", text, thread_id)

    saved_state = thread_states.get(thread_id)
    if saved_state:
        messages = saved_state.get("messages", []) + [HumanMessage(content=text)]
        init_state = {**saved_state, "input": text, "messages": messages, "lang": payload.lang}
    else:
        init_state = {
            "input": text,
            "messages": [HumanMessage(content=text)],
            "lang": payload.lang
        }

    out = await asyncio.get_event_loop().run_in_executor(
        None, langgraph_app.invoke, init_state
    )

    if isinstance(out, dict):
        thread_states[thread_id] = out

    # If agent provided a clean JSON result
    if "result" in out:
        try:
            return JSONResponse(content=out["result"])
        except Exception:
            pass

    # If fallback: format natural language output
    resp = out.get("nl_output", "(no output)")
    return JSONResponse(content=[{"info": resp}])


# Booking endpoints for demo booking simulation
class BookingRequest(BaseModel):
    train_id: str
    train_name: str
    date: str
    class_name: str
    passenger_name: str | None = None


@app.post("/booking")
def create_booking(req: BookingRequest):
    passenger = req.passenger_name or "Passenger"
    try:
        rec = booking_node.create_booking(req.train_id, req.train_name, req.date, req.class_name, passenger)
        return JSONResponse(content=rec)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/booking/{pnr}/export")
def export_booking_ics(pnr: str):
    rec = booking_node.get_booking(pnr)
    if not rec:
        return JSONResponse(status_code=404, content={"error": "PNR not found"})

    # simple ICS content
    dtstamp = rec.get("created_at", datetime.utcnow().isoformat())
    start_date = rec.get("date", "2026-07-01")
    summary = f"Train {rec.get('train_name')} ({rec.get('train_id')})"
    description = f"Class: {rec.get('class')}\nPNR: {rec.get('pnr')}\nPassenger: {rec.get('passenger')}"
    ics = (
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//RailwayAgent//EN\n"
        f"BEGIN:VEVENT\nUID:{rec.get('pnr')}\nDTSTAMP:{dtstamp}\n"
        f"DTSTART;VALUE=DATE:{start_date.replace('-', '')}\nSUMMARY:{summary}\nDESCRIPTION:{description}\nEND:VEVENT\nEND:VCALENDAR\n"
    )

    headers = {"Content-Disposition": f"attachment; filename=booking_{pnr}.ics"}
    return Response(content=ics, media_type="text/calendar", headers=headers)


@app.get("/booking/{pnr}/pdf")
def export_booking_pdf(pnr: str):
    rec = booking_node.get_booking(pnr)
    if not rec:
        return JSONResponse(status_code=404, content={"error": "PNR not found"})

    if not REPORTLAB_AVAILABLE:
        return JSONResponse(status_code=500, content={"error": "PDF export requires 'reportlab'. Install via pip install reportlab"})

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x = 50
    y = height - 80
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, f"Booking Confirmation - PNR: {rec.get('pnr')}")
    y -= 30
    c.setFont("Helvetica", 12)
    lines = [
        f"Train: {rec.get('train_name')} ({rec.get('train_id')})",
        f"Date: {rec.get('date')}",
        f"Class: {rec.get('class')}",
        f"Price: ₹{rec.get('price')}",
        f"Passenger: {rec.get('passenger')}",
        f"Created: {rec.get('created_at')}",
    ]

    for line in lines:
        c.drawString(x, y, line)
        y -= 20

    c.showPage()
    c.save()
    buffer.seek(0)

    headers = {"Content-Disposition": f"attachment; filename=booking_{pnr}.pdf"}
    return Response(content=buffer.read(), media_type="application/pdf", headers=headers)

if __name__=="__main__":
    import uvicorn;uvicorn.run(app,host="0.0.0.0",port=8002)
