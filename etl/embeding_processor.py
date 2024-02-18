from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from etl.document import Document, DocumentChunk
from etl.document_storage import DocumentStorage

from dotenv import load_dotenv

load_dotenv()
import os

EMBEDING_STORAGE = os.environ.get("EMBEDING_STORAGE")


class EmbeddingProcessor:

    def __init__(
        self,
        documents: list[Document],
        embeddings=OpenAIEmbeddings(),
    ):
        self.documents = documents
        self.embeddings = embeddings
        self.filename = "embeddings.pkl"

    def __embed_documents(self) -> FAISS:
        chunks = []
        metadatas = []
        for doc in self.documents:
            for chunk in doc.chunks:
                chunks.append(chunk.content)
                metadatas.append(chunk.metadata)

        embeddings = OpenAIEmbeddings()
        self.__indexes = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
        return self.__indexes

    def process(self):
        return self.__embed_documents()

    def process_and_save(self):
        self.documents = self.process()
        self.__indexes.save_local(EMBEDING_STORAGE + self.filename)
