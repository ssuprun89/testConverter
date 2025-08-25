import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.router import converter_router, root_router, ws_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(ws_router, tags=["WS"])
app.include_router(root_router, tags=["Root"])
app.include_router(converter_router, tags=["Converter"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*", "localhost", "127.0.0.1", "192.168.65.1"]
)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
