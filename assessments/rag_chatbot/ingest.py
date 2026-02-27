import asyncio
import os, sys

# ensure project root is on Python path so imports work regardless of cwd
# this file lives in assessments/rag_chatbot, so go up two levels
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if root not in sys.path:
    sys.path.insert(0, root)

from assessments.rag_chatbot.services import RAGService

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Ingest documents into RAG vector store")
    parser.add_argument("--company-id", default="acme-corp", help="Identifier used in metadata")
    parser.add_argument(
        "--docs-path",
        default="data/uploads/02_rag/company_docs",
        help="Directory containing documents to ingest (relative to project root if not absolute)",
    )
    return parser.parse_args()

async def main(company_id: str, docs_path: str):
    print("🚀 Ingesting company documents...")
    count = await RAGService.ingest_documents(company_id, docs_path)
    print(f"✅ Ingested {count} chunks for {company_id}")

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.company_id, args.docs_path))