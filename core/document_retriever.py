from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from document import Document, DocumentChunk


class DocumentRetriever:

    DEFAULT_DOCUMENT_PROMPT = """Sistema: Para tu respuesta, considera los siguientes extractos de normativa interna:
    {input_docs}
    Bot:"""

    def __init__(
        self,
        documents: list[Document],
        retriever_prompt_template=DEFAULT_DOCUMENT_PROMPT,
        score_threshold=0.5,
        k=5,
    ):
        self.documents = documents
        self.template = retriever_prompt_template
        self.score_threshold = score_threshold
        self.__k = k
        chunks = []
        metadatas = []
        for doc in documents:
            for chunk in doc.chunks:
                chunks.append(chunk.content)
                metadatas.append(chunk.metadata)

        embeddings = OpenAIEmbeddings()
        self.__indexes = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)

    def search_documents(self, query):
        return self.__indexes.similarity_search_with_score(
            query,
            k=self.__k,
        )

    def __parse_documents(self, documents) -> list[DocumentChunk]:
        chunks = []

        for document in documents:
            metadata = document.metadata
            content = document.page_content
            chunks.append(DocumentChunk(content, metadata))
        return chunks

    def __filter_documents_by_score(
        self, documents_with_scores: list[tuple[Document, float]]
    ):
        documents = []
        for document, score in documents_with_scores:
            if score > self.score_threshold:
                documents.append(document)
        return documents

    def get_document_query_prompt(self, query: str):
        documents_with_scores = self.search_documents(query)
        documents = self.__filter_documents_by_score(documents_with_scores)

        if not documents:
            return ""

        chunks = self.__parse_documents(documents)

        input_docs = ""
        for chunk in chunks:
            input_docs += "Normativa:" + chunk.metadata["title"]
            input_docs += "\nContenido:\n" + chunk.content + "\n"

        return self.template.format(input_docs=input_docs)
