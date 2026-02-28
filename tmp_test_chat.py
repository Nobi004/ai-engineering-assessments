from fastapi.testclient import TestClient
from assessments.rag_chatbot.routers import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# first ingest to ensure docs exist
from assessments.rag_chatbot.services import RAGService
import asyncio
asyncio.run(RAGService.ingest_documents("acme-corp"))

# proper body
resp = client.post("/api/02-rag/chat", json={"query": "tell me about the company"})
print("status", resp.status_code, "body", resp.json())

# missing query still should error
resp2 = client.post("/api/02-rag/chat", json={})
print("status2", resp2.status_code, "body", resp2.json())

# using query parameter
resp3 = client.post("/api/02-rag/chat?query=hello")
print("status3", resp3.status_code, "body", resp3.json())
