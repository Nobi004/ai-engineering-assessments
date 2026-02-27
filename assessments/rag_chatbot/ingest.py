import asyncio
import os, sys

# ensure project root is on Python path so imports work regardless of cwd
# this file lives in assessments/rag_chatbot, so go up two levels
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if root not in sys.path:
    sys.path.insert(0, root)

from assessments.rag_chatbot.services import RAGService

async def main():
    print("🚀 Ingesting company documents...")
    count = await RAGService.ingest_documents("acme-corp")
    print(f"✅ Ingested {count} chunks for acme-corp")

if __name__ == "__main__":
    asyncio.run(main())