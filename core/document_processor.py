from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.llms.openai import OpenAI

from document import Document, RAWDocument, DocumentChunk

import re


class DocumentProcessor:
    SUMARIZER_PROMPT = """
    A continuación se mostrará las dos últimas páginas de un documento de una normativa legal.
    Responde únicamente con el nombre del documento, en caso de no determinarlo, responde con "Documento no identificado".
    Documento:
    {input_page}
    """

    REGEX_FILTER = r'[a-zA-ZñÑáéíóúÁÉÍÓÚ,;:". ()0-9-\n]'

    def __init__(
        self,
        raw_documents: list[RAWDocument],
        sumarizer_model="gpt-3.5-turbo-instruct",
        sumarizer_prompt=SUMARIZER_PROMPT,
    ):
        self.__sumerizer_llm = OpenAI(model=sumarizer_model)
        self.__sumarizer_prompt = sumarizer_prompt
        self.raw_documents = raw_documents

    def clean_characters(self, text):
        return re.search(self.REGEX_FILTER, text, re.MULTILINE).string

    def __get_documents(self) -> list[Document]:
        docs = []
        for raw_doc in self.raw_documents:
            first_page = self.clean_characters(
                raw_doc.pages[-1]
            ) + self.clean_characters(raw_doc.pages[-2])
            title = self.__sumerizer_llm(
                self.__sumarizer_prompt.format(input_page=first_page)
            )
            clean_text = self.clean_characters(raw_doc.text)
            docs.append(
                Document(title=title, raw_document=raw_doc, clean_text=clean_text)
            )
        return docs

    def __chunk_documents(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=32,
            length_function=len,
        )

        for doc in self.documents:
            metadata = {"title": doc.title}

            doc.chunks = [
                DocumentChunk(chunk, metadata)
                for chunk in text_splitter.split_text(doc.clean_text)
            ]

    def process(self):
        self.documents = self.__get_documents()
        self.__chunk_documents()
        return self.documents

    def get_documents(self):
        return self.documents
