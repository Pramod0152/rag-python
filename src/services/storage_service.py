import uuid
from langchain_core.documents import Document
from infrastructure.db import get_supabase
from infrastructure.embeddings import embed_documents


async def store_chunks(chunks: list[Document], filename: str) -> dict:
    document_id = str(uuid.uuid4())
    texts = [chunk.page_content for chunk in chunks]

    embeddings = embed_documents(texts)

    supabase = get_supabase()

    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "chunk_text": chunk.page_content,
                "embedding": embedding,  # supabase-py accepts plain list of floats
            }
        )

    supabase.table("document_chunks").insert(rows).execute()

    return {
        "document_id": document_id,
        "chunks_created": len(chunks),
        "status": "success",
    }
