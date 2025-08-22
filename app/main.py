import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.router import root_router, ws_router, converter_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(root_router, tags=["Root"])
app.include_router(converter_router, tags=["Converter"])
app.include_router(ws_router, tags=["WS"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
