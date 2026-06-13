from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text: str, metadata: dict | None = None) -> list[Document]:
    """
    Splits plain text into overlapping chunks suitable for embedding.
    Returns a list of LangChain Document objects (text + metadata).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_text(text)

    documents = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = dict(metadata or {})
        chunk_metadata["chunk_index"] = i
        documents.append(Document(page_content=chunk, metadata=chunk_metadata))

    return documents
