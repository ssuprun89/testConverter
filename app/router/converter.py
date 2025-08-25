from typing import List

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.managers import ConverterManager

router = APIRouter(prefix="/api/convert")


@router.post("/{job_id}/")
async def convert(job_id: str, files: List[UploadFile] = File(...)):
    try:
        buf = await ConverterManager(job_id, files).run_converter()
        return StreamingResponse(
            content=buf,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{job_id}_files.zip"'
            },
        )
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=400,
            headers={"Content-Type": "application/json"},
        )
