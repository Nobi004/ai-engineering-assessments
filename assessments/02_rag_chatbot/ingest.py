import asyncio
from assessments.02_rag_chatbot.services import RAGService

async def main():
    print("🚀 Ingesting company documents...")
    count = await RAGService.ingest_documents("acme-corp")
    print(f"✅ Ingested {count} chunks for acme-corp")

if __name__ == "__main__":
    asyncio.run(main())