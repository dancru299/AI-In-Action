import os
import json
import queue
import threading
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator

# Đổi working directory về thư mục chứa file này
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import graph từ agent.py (graph được build ở module-level)
from agent import graph

app = FastAPI(title="TravelBuddy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


async def event_generator(message: str) -> AsyncGenerator[str, None]:
    """Chạy LangGraph trong thread riêng và stream events qua SSE."""
    q: queue.Queue = queue.Queue()

    def run_graph():
        try:
            for event in graph.stream(
                {"messages": [("human", message)]},
                stream_mode="updates",
            ):
                q.put(event)
        except Exception as e:
            q.put({"__error__": str(e)})
        finally:
            q.put(None)  # sentinel báo hiệu hoàn thành

    thread = threading.Thread(target=run_graph, daemon=True)
    thread.start()

    loop = asyncio.get_event_loop()

    while True:
        # Chờ event từ queue (blocking) trong executor để không block event loop
        try:
            event = await loop.run_in_executor(None, lambda: q.get(timeout=60))
        except queue.Empty:
            yield f"data: {json.dumps({'type': 'error', 'content': 'Timeout'})}\n\n"
            break

        if event is None:
            break

        if "__error__" in event:
            yield f"data: {json.dumps({'type': 'error', 'content': event['__error__']}, ensure_ascii=False)}\n\n"
            break

        # Xử lý events từ node "agent"
        if "agent" in event:
            for msg in event["agent"]["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        payload = {
                            "type": "tool_call",
                            "name": tc["name"],
                            "args": tc["args"],
                            "id": tc.get("id")
                        }
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                elif hasattr(msg, "content") and msg.content:
                    payload = {"type": "final_answer", "content": msg.content}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Xử lý events từ node "tools"
        elif "tools" in event:
            for msg in event["tools"]["messages"]:
                payload = {
                    "type": "tool_result",
                    "name": getattr(msg, "name", "tool"),
                    "content": msg.content,
                    "id": getattr(msg, "tool_call_id", None)
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        event_generator(req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/")
async def root():
    static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_path)


# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("TravelBuddy Web UI")
    print("Mở trình duyệt: http://localhost:8000")
    print("=" * 50)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
