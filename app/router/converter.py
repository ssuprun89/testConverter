from typing import List

from fastapi import APIRouter, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect

from app.managers import ConverterManager
from app.services import websocket_client

router = APIRouter(prefix="/api/convert")


@router.post("/{job_id}/")
async def convert(job_id: str, files: List[UploadFile] = File(...)):
    try:
        buf = await ConverterManager.run_converter(files, job_id)
        return StreamingResponse(
            content=buf,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{job_id}_files.zip"'}
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400, headers={"Content-Type": "application/json"})

router_ws = APIRouter(prefix="/ws/convert")


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