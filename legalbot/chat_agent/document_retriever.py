from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.llms.openai import OpenAI
from processing.document import Document, DocumentChunk
from langchain_core.documents.base import Document as LangchainDocument

import os

EMBEDING_STORAGE = os.environ.get("EMBEDING_STORAGE")


class DocumentRetriever:

    DEFAULR_RETRIEVER_PROMPT = """Para tu respuesta, considera los siguientes extractos de normativa interna.
    Argumenta al final, citando siempre el o los articulos que cosnideres relevantes, indicando el reglamento y articulo
    Documentos Relacionados: 
    {input_docs}
    Resumen:
    """

    DEFAULT_SUMARIZATION_PROMPT = """Arma un breve resumen del siguiente articulo de normativa sin descartar 
    el numero de articulo ni la informacion vital: {input_doc}"""

    def __init__(
        self,
        retriever_prompt_template=DEFAULR_RETRIEVER_PROMPT,
        score_threshold=0.5,
        k=3,
    ):
        self.template = retriever_prompt_template
        self.score_threshold = score_threshold
        self.embeddings = OpenAIEmbeddings()
        self.__k = k
        self.__indexes = self.__load_indexes()
        self.__sumarizer_model_name = "gpt-3.5-turbo-instruct"
        self.__sumarizer_model = OpenAI(
            model=self.__sumarizer_model_name, temperature=0.2
        )

    def __load_indexes(self):
        indexes = []
        # iterate over the embeding storage directory
        # and load the indexes
        if not os.path.exists(EMBEDING_STORAGE):
            raise Exception("No embeding storage found")
        for filename in os.listdir(EMBEDING_STORAGE):
            if filename.endswith(".faiss"):
                indexes.append(
                    FAISS.load_local(
                        EMBEDING_STORAGE,
                        self.embeddings,
                        filename.replace(".faiss", ""),
                    )
                )
        faiss_index = indexes[0]
        for index in indexes[1:]:
            faiss_index.merge_from(index)
        return faiss_index

    def search_documents(self, query):
        return self.__indexes.similarity_search_with_score(
            query,
            k=self.__k,
        )

    def __parse_chunk(self, faiss_docs: LangchainDocument) -> list[DocumentChunk]:
        chunks = []

        for faiss_doc in faiss_docs:
            metadata = faiss_doc.metadata
            content = faiss_doc.page_content
            chunks.append(DocumentChunk(content, metadata))

        return chunks

    def __filter_documents_by_score(
        self, documents_with_scores: list[tuple[Document, float]]
    ) -> list[LangchainDocument]:
        documents = []
        for document, score in documents_with_scores:
            if score <= self.score_threshold:
                documents.append(document)
        return documents

    def __sumarize_chunk(self, chunk: DocumentChunk) -> str:
        prompt = self.DEFAULT_SUMARIZATION_PROMPT.format(input_doc=chunk.content)
        chunk.content = self.__sumarizer_model(prompt)
        return chunk

    def get_document_query(self, query: str):
        documents_with_scores = self.search_documents(query)
        documents = self.__filter_documents_by_score(documents_with_scores)
        chunks = self.__parse_chunk(documents)
        # chunks = [ self.__sumarize_chunk(chunk) for chunk in chunks  ]
        return chunks

    def get_document_query_prompt(self, query: str):
        chunks = self.get_document_query(query)
        input_docs = "Documentos relevantes para la consulta: \n"

        if not chunks:
            input_docs += "No se encontraron resultados"

        for chunk in chunks:
            input_docs += chunk.content + "\n"

        return self.template.format(input_docs=input_docs)
