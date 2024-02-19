from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from etl.document import Document, DocumentChunk
from etl.document_storage import DocumentStorage
from distutils.dir_util import copy_tree

import os

EMBEDING_STORAGE = os.environ.get("EMBEDING_STORAGE")


class EmbeddingProcessor:

    def __init__(
        self,
        embeddings=OpenAIEmbeddings(),
    ):
        self.embeddings = embeddings

    def embed_document(self, doc: Document) -> FAISS:
        chunks = []
        metadatas = []
        for chunk in doc.chunks:
            chunks.append(chunk.content)
            metadatas.append(chunk.metadata)

        embeddings = OpenAIEmbeddings()
        vectorStore = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
        vectorStore.save_local(EMBEDING_STORAGE, doc.filename)

    def deactivate_index(self, filename: str):
        os.rename(
            os.path.join(EMBEDING_STORAGE, filename + ".pkl"),
            os.path.join(EMBEDING_STORAGE, filename + ".pkl.deactivated"),
        )
        os.rename(
            os.path.join(EMBEDING_STORAGE, filename + ".faiss"),
            os.path.join(EMBEDING_STORAGE, filename + ".faiss.deactivated"),
        )

    def reactivate_index(self, filename: str):
        os.rename(
            os.path.join(EMBEDING_STORAGE, filename + ".pkl.deactivated"),
            os.path.join(EMBEDING_STORAGE, filename + ".pkl"),
        )
        os.rename(
            os.path.join(EMBEDING_STORAGE, filename + ".faiss.deactivated"),
            os.path.join(EMBEDING_STORAGE, filename + ".faiss"),
        )
