import time
import zipfile
from pathlib import Path
from typing import List
from io import BytesIO

from fastapi import UploadFile

from app.services import websocket_client


class ConverterManager:

    @staticmethod
    def _generate_payload(status, files):
        status_progress = {
            "Started": 10,
            "Finished": 100,
        }

        return {i.filename.split(".")[0]: {"status": status, "progress": status_progress[status]} for i in files}

    @classmethod
    async def run_converter(cls, files: List[UploadFile], job_id: str):
        await websocket_client.send(
            job_id, cls._generate_payload("Started", files)
        )
        time.sleep(3)
        await websocket_client.send(
            job_id,
            cls._generate_payload("Finished", files)
        )
        buf = BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                raw = await f.read()
                out_name = Path(f.filename).name
                zf.writestr(out_name, raw)
        buf.seek(0)
        return buf
