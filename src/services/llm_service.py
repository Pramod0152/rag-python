from services.retrieval_service import retrieve_chunks
from infrastructure import llm_client

PROMPT_TEMPLATE = """Use the following context to answer the question. If the context doesn't contain enough information, say you don't know.

Context:
{context}

Question: {query}

Answer:"""


def _build_prompt(query: str, chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join(c["chunk_text"] for c in chunks)
    return PROMPT_TEMPLATE.format(context=context, query=query)


async def answer_query(query: str) -> dict:
    chunks = retrieve_chunks(query)
    prompt = _build_prompt(query, chunks)

    answer = await llm_client.complete(prompt)
    sources = list({c["filename"] for c in chunks})

    return {"answer": answer, "sources": sources}


async def stream_answer(query: str):
    chunks = retrieve_chunks(query)
    prompt = _build_prompt(query, chunks)

    async for token in llm_client.stream_complete(prompt):
        yield token
