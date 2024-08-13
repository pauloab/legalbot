from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from processing.document import Document
import os
from pathlib import Path

EMBEDING_STORAGE = os.environ.get("EMBEDING_STORAGE")


class EmbeddingProcessor:

    def __init__(
        self, embeddings=OpenAIEmbeddings(), embedding_storage=EMBEDING_STORAGE
    ):
        self.embeddings = embeddings
        self.embedding_storage = embedding_storage

    def embed_document(self, doc: Document) -> FAISS:
        chunks = []
        metadatas = []
        for chunk in doc.chunks:
            chunk_text = (
                "Documento: \n"
                + chunk.metadata["title"]
                + "\nFragmento: \n"
                + chunk.content
            )
            chunks.append(chunk_text)
            metadatas.append(chunk.metadata)

        embeddings = OpenAIEmbeddings()
        vectorStore = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
        vectorStore.save_local(os.path.join(self.embedding_storage, doc.filename))

    def deactivate_index(self, filename: str):
        os.rename(
            os.path.join(self.embedding_storage, filename + ".pkl"),
            os.path.join(self.embedding_storage, filename + ".pkl.deactivated"),
        )
        os.rename(
            os.path.join(self.embedding_storage, filename + ".faiss"),
            os.path.join(self.embedding_storage, filename + ".faiss.deactivated"),
        )

    def reactivate_index(self, filename: str):
        os.rename(
            os.path.join(self.embedding_storage, filename + ".pkl.deactivated"),
            os.path.join(self.embedding_storage, filename + ".pkl"),
        )
        os.rename(
            os.path.join(self.embedding_storage, filename + ".faiss.deactivated"),
            os.path.join(self.embedding_storage, filename + ".faiss"),
        )

    def delete_index(self, filename: str):
        path = Path(os.path.join(self.embedding_storage, filename + ".pkl"))

        if path.is_file():
            os.remove(os.path.join(self.embedding_storage, filename + ".pkl"))
            os.remove(os.path.join(self.embedding_storage, filename + ".faiss"))
        else:
            os.remove(
                os.path.join(self.embedding_storage, filename + ".faiss.deactivated")
            )
            os.remove(
                os.path.join(self.embedding_storage, filename + ".pkl.deactivated")
            )
