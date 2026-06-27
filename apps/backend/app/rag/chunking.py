"""Recursive text chunking + token counting (LangChain splitter, tiktoken)."""

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoder.encode(text))


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )
    return [c for c in splitter.split_text(text) if c.strip()]
