from dotenv import load_dotenv

from langchain_community.llms.openai import OpenAI

from memory import Memmory
from document import Document
from document_retriever import DocumentRetriever

load_dotenv()


class LegalChatbotModel:

    __legal_docs = None
    __model_name = None
    memory = None

    def __init__(
        self,
        legal_docs: list[Document],
        memory: Memmory,
        model_name="gpt-3.5-turbo-instruct",
    ):
        self.__model_name = model_name
        self.__model = OpenAI(model=self.__model_name)
        self.__document_retriever = DocumentRetriever(legal_docs)
        self.legal_docs = legal_docs
        self.memory = memory

    def get_next_prompt(self, query: str):
        docs_prompt = self.__document_retriever.get_document_query_prompt(query)
        memory_prompt = self.memory.get_memory_prompt()
        prompt = memory_prompt + "\n" + docs_prompt
        return prompt

    def chat(self, query: str):
        docs_prompt = self.__document_retriever.get_document_query_prompt(query)
        self.memory.add_human_message(query)
        memory_prompt = self.memory.get_history_prompt()
        prompt = memory_prompt + "\n" + docs_prompt
        answer = self.__model(prompt)
        self.memory.add_chatbot_message(answer)
        return answer
