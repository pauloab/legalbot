from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.llms.openai import OpenAI

from processing.document import Document, DocumentChunk
from processing.document_storage import DocumentStorage
import re

import os

CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")


class DocumentProcessor:
    SUMARIZER_PROMPT = """
    A continuación se mostrará la primera pagina de un documento de una normativa legal.
    Responde únicamente con el nombre del documento en mayúsculas, en caso de no determinarlo, responde con "Documento no identificado".
    Fragmento:
    {input_page}
    """

    REGEX_FILTER = r'[a-zA-ZñÑáéíóúÁÉÍÓÚ,;:". ()0-9-\n]'

    def __init__(
        self,
        documents: list[Document],
        sumarizer_model="gpt-3.5-turbo-instruct",
        sumarizer_prompt=SUMARIZER_PROMPT,
    ):
        self.__sumerizer_llm = OpenAI(model=sumarizer_model)
        self.__sumarizer_prompt = sumarizer_prompt
        self.__document_storage = DocumentStorage(CONNECTION_STR, DBNAME)
        self.documents = documents

    def clean_characters(self, text):
        return re.search(self.REGEX_FILTER, text, re.MULTILINE).string

    def __clean_documents(self):
        for doc in self.documents:
            doc.content = self.clean_characters(doc.content)

    def __add_title(self) -> list[Document]:
        docs = []
        for doc in self.documents:
            last_pages = doc.pages[0]
            title = self.__sumerizer_llm(
                self.__sumarizer_prompt.format(input_page=last_pages)
            )
            doc.title = title

    def __chunk_documents(self):
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["Art."],
            length_function=len,
        )

        for doc in self.documents:
            splitted = text_splitter.split_text("Art." + doc.content)
            metadata = doc.get_metadata()
            doc.chunks = [DocumentChunk(chunk, metadata) for chunk in splitted]

    def process(self):
        self.__clean_documents()
        self.__add_title()
        self.__chunk_documents()

    def process_and_save(self):
        self.process()
        for doc in self.documents:
            doc.id = self.__document_storage.add(doc)
