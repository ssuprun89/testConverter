from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from app.services import websocket_client

router = APIRouter(prefix="/ws/convert")


@router.websocket("/{job_id}/")
async def ws_job(websocket: WebSocket, job_id: str):
    await websocket_client.connect(job_id, websocket)
    try:
        # Receive simple control messages ("cancel", "ping")
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")

    except WebSocketDisconnect:
        pass
    finally:
        websocket_client.disconnect(job_id, websocket)
