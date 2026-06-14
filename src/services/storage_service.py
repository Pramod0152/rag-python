import asyncio
import uuid

from langchain_core.documents import Document

from infrastructure.db import get_supabase
from infrastructure.embeddings import embed_documents

EMBED_BATCH_SIZE = 8
INSERT_BATCH_SIZE = 100


def _insert_rows(supabase, rows: list[dict]) -> None:
    supabase.table("document_chunks").insert(rows).execute()


async def store_chunks(
    chunks: list[Document],
    filename: str,
    on_progress=None,
) -> dict:
    document_id = str(uuid.uuid4())
    texts = [chunk.page_content for chunk in chunks]
    total = len(texts)
    embeddings: list[list[float]] = []

    if on_progress:
        await on_progress(
            "embedding",
            f"Generating embeddings for {total} chunks...",
            45,
        )

    for i in range(0, total, EMBED_BATCH_SIZE):
        batch = texts[i : i + EMBED_BATCH_SIZE]
        batch_embeddings = await asyncio.to_thread(embed_documents, batch)
        embeddings.extend(batch_embeddings)

        done = min(i + EMBED_BATCH_SIZE, total)
        if on_progress:
            percent = 45 + int(35 * done / total)
            await on_progress(
                "embedding",
                f"Generated embeddings ({done}/{total} chunks)",
                percent,
            )

    if on_progress:
        await on_progress(
            "storing",
            f"Saving {total} chunks to database...",
            85,
        )

    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "chunk_text": chunk.page_content,
                "embedding": embedding,
            }
        )

    supabase = get_supabase()
    for i in range(0, len(rows), INSERT_BATCH_SIZE):
        batch = rows[i : i + INSERT_BATCH_SIZE]
        await asyncio.to_thread(_insert_rows, supabase, batch)

        done = min(i + INSERT_BATCH_SIZE, len(rows))
        if on_progress:
            percent = 85 + int(10 * done / len(rows))
            await on_progress(
                "storing",
                f"Saved {done}/{len(rows)} chunks to database",
                percent,
            )

    if on_progress:
        await on_progress(
            "storing",
            f"Saved {len(rows)} chunks to database",
            95,
        )

    return {
        "document_id": document_id,
        "chunks_created": len(chunks),
        "status": "success",
    }
