import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader


def extract_document(filename: str, content: bytes) -> str:
    """
    Extracts plain text from raw document bytes based on file extension.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        text = "\n".join(doc.page_content for doc in documents)
        return fix_spaced_text(text)
    finally:
        os.unlink(tmp_path)


def fix_spaced_text(text: str) -> str:
    """
    Collapses text where individual characters are separated by single spaces
    (common in Canva-exported PDFs), while preserving real word boundaries
    marked by double spaces.
    """
    lines = text.split("\n")
    fixed_lines = []

    for line in lines:
        if _looks_spaced_out(line):
            # Double space = word boundary, single space = char separator
            words = line.split("  ")
            fixed_words = ["".join(w.split(" ")) for w in words if w]
            fixed_lines.append(" ".join(fixed_words))
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def _looks_spaced_out(line: str) -> bool:
    """
    Heuristic: a line is 'spaced out' if removing all spaces and comparing
    lengths shows that >70% of non-space characters are followed by a space
    (i.e. nearly every character is isolated).
    """
    stripped = line.strip()
    if len(stripped) < 4:
        return False

    # Count single-char tokens vs total tokens when split by single space
    tokens = stripped.split(" ")
    single_char_tokens = sum(1 for t in tokens if len(t) == 1)

    return len(tokens) > 3 and (single_char_tokens / len(tokens)) > 0.6
