from infrastructure.db import get_supabase
from infrastructure.embeddings import embed_query
from config import TOP_K_RESULTS


def retrieve_chunks(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """
    Embeds the query and calls the match_document_chunks RPC in Supabase
    to find the most similar chunks.
    """
    query_embedding = embed_query(query)

    supabase = get_supabase()
    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": top_k,
        },
    ).execute()

    return response.data  # list of {id, document_id, filename, chunk_text, similarity}
