from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.database import init_db
from core.exceptions import AppBaseException
from assessments.workflow_automation.routers import router
from assessments.rag_chatbot.routers import router as rag_router
import asyncio

app = FastAPI(title="AI Engineering Assessment - Assessment 1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppBaseException)
async def app_exception_handler(_, exc: AppBaseException):
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "detail": str(exc)})

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(router)
app.include_router(rag_router)