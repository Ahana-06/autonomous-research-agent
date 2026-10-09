"""
Ingestion pipeline: turns a list of PDF file paths into a persisted
ChromaDB collection of embedded chunks, ready for similarity search.
"""
import os
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

import config

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Lazily instantiate (and cache) the embedding model."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    return _embeddings


def load_and_split_pdfs(pdf_paths: List[str]) -> List[Document]:
    """Load each PDF page-by-page and split into overlapping chunks.

    Each chunk keeps metadata about its originating file name and page
    number, which is what powers the [Internal-N] citations later on.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    all_chunks: List[Document] = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        pages = loader.load()
        chunks = splitter.split_documents(pages)
        source_name = os.path.basename(path)
        for chunk in chunks:
            chunk.metadata["source"] = source_name
            # PyPDFLoader already sets "page" (0-indexed); make it 1-indexed
            # for a friendlier citation display.
            if "page" in chunk.metadata:
                chunk.metadata["page"] = chunk.metadata["page"] + 1
        all_chunks.extend(chunks)
    return all_chunks


def build_vectorstore(
    pdf_paths: List[str],
    persist_directory: str = None,
) -> Tuple[Chroma, int]:
    """Chunk the given PDFs and (re)build the persisted Chroma collection.

    Returns the vectorstore handle and the number of chunks indexed.
    """
    persist_directory = persist_directory or config.CHROMA_DIR
    chunks = load_and_split_pdfs(pdf_paths)

    if not chunks:
        raise ValueError("No text could be extracted from the supplied PDFs.")

    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=config.COLLECTION_NAME,
        persist_directory=persist_directory,
    )
    return vectorstore, len(chunks)


def load_existing_vectorstore(persist_directory: str = None) -> Chroma:
    """Open an already-built Chroma collection without re-ingesting."""
    persist_directory = persist_directory or config.CHROMA_DIR
    embeddings = get_embeddings()
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
