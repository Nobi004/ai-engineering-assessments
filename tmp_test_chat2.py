from fastapi.testclient import TestClient
from assessments.rag_chatbot.routers import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# prep documents
from assessments.rag_chatbot.services import RAGService
import asyncio
asyncio.run(RAGService.ingest_documents("acme-corp"))

# body request
print("body ->", client.post("/api/02-rag/chat", json={"query":"projects"}).json())
# query param
print("param ->", client.post("/api/02-rag/chat?query=projects").json())
# missing both
resp = client.post("/api/02-rag/chat")
print("missing ->", resp.status_code, resp.json())
