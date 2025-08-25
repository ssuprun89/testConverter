import asyncio
import enum
import os
import shutil
import subprocess
import tempfile
import zipfile
from io import BytesIO

from fastapi import UploadFile
from fastapi.datastructures import Headers

from app.services import websocket_client


class ConvertStatus(enum.Enum):
    STARTED = "Started"
    VALIDATED = "Validated"
    CONVERTING = "Converting"
    CONVERTED = "Converted"
    PUT_TO_ZIP = "PutToZip"
    FINISHED = "Finished"


class ConverterManager:

    def __init__(self, job_id, files):
        self.job_id = job_id
        self.files = files

    async def send_ws(self, status: ConvertStatus, files):
        status_progress = {
            ConvertStatus.STARTED: 10,
            ConvertStatus.VALIDATED: 20,
            ConvertStatus.CONVERTING: 30,
            ConvertStatus.CONVERTED: 60,
            ConvertStatus.PUT_TO_ZIP: 90,
            ConvertStatus.FINISHED: 100,
        }
        create_name = lambda i: (
            i.filename.split()[0] if "|" in i.filename else i.filename
        )
        await websocket_client.send(
            self.job_id,
            {
                create_name(i): {
                    "status": status.value,
                    "progress": status_progress[status],
                }
                for i in files
            },
        )

    async def validated(self):
        new_files = []
        for file in self.files:
            filename, ext = os.path.splitext(file.filename)
            if ext.lower() in [".doc", ".docx"]:
                await self.send_ws(ConvertStatus.VALIDATED, [file])
            elif ext == ".zip" and file.content_type in [
                "application/zip",
                "application/x-zip-compressed",
            ]:
                content = await file.read()
                with zipfile.ZipFile(BytesIO(content), "r") as z:
                    for name in z.namelist():
                        if "/" in name:
                            continue
                        ext = os.path.splitext(name)[1].lower()
                        if ext in [".doc", ".docx"]:
                            with z.open(name) as f:
                                new_files.append(
                                    UploadFile(
                                        filename=f"{filename}|{name}",
                                        file=BytesIO(f.read()),
                                        headers=Headers(
                                            {
                                                "content-disposition": f'form-data; name="files"; filename="{filename}_{name}"',
                                                "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            }
                                        ),
                                    )
                                )
            else:
                return False

        self.files += new_files
        self.files = [
            file
            for file in self.files
            if os.path.splitext(file.filename)[1].lower() in [".doc", ".docx"]
        ]
        return True

    async def convert_file(self, temp_input_dir, file, temp_output_dir):
        file_path = os.path.join(temp_input_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        output_file = os.path.join(
            temp_output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.pdf"
        )
        await self.send_ws(ConvertStatus.CONVERTING, [file])
        cmd = [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            file_path,
            "--outdir",
            temp_output_dir,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        await self.send_ws(ConvertStatus.CONVERTED, [file])

        return file, output_file

    async def run_converter(self):
        await self.send_ws(ConvertStatus.STARTED, self.files)
        if not await self.validated():
            raise Exception("Converter failed")

        temp_input_dir = tempfile.mkdtemp()
        temp_output_dir = tempfile.mkdtemp()

        tasks = [
            self.convert_file(temp_input_dir, file, temp_output_dir)
            for file in self.files
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        buf = BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file, f_path_output in results:
                await self.send_ws(ConvertStatus.PUT_TO_ZIP, [file])
                zf.write(f_path_output, os.path.basename(f_path_output))
        await self.send_ws(ConvertStatus.FINISHED, self.files)
        buf.seek(0)
        shutil.rmtree(temp_input_dir)
        shutil.rmtree(temp_output_dir)
        return buf
