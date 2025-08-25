from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, job_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(job_id, set()).add(ws)

    def disconnect(self, job_id: str, ws: WebSocket):
        conns = self.active.get(job_id)
        if conns:
            conns.discard(ws)
            if not conns:
                self.active.pop(job_id, None)

    async def send(self, job_id: str, message: dict):
        # fan-out to all listeners of this job_id
        for ws in list(self.active.get(job_id, set())):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(job_id, ws)
