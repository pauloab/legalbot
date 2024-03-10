from langchain_community.llms.openai import OpenAI

from chatbot.memory import Memory
from etl.document import Document
from chatbot.document_retriever import DocumentRetriever


class Chatbot:

    DEFAULT_CONTEXT = """Eres un bot de la Universidad Técnica de Machala que contesta dudas sobre normas legales internas de la universidad."""

    __legal_docs = None
    __model_name = None
    memory = None

    def __init__(
        self,
        memory: Memory,
        model_name="gpt-3.5-turbo-instruct",
        temperature=0.7,
        chatbot_context=DEFAULT_CONTEXT,
    ):
        self.__model = OpenAI(model=model_name, temperature=temperature)
        self.__document_retriever = DocumentRetriever()
        self.__chatbot_context = chatbot_context
        self.memory = memory

    def get_next_prompt(self, query: str):
        docs_prompt = self.__document_retriever.get_document_query_prompt(query)
        memory_prompt = self.memory.get_history_prompt()
        prompt = self.__chatbot_context + memory_prompt + "\n" + docs_prompt
        prompt += self.memory.chatbot_prefix + ": "
        return prompt

    def chat(self, query: str):
        self.memory.add_human_message(query)
        prompt = self.get_next_prompt(query)
        answer = self.__model(prompt)
        self.memory.add_chatbot_message(answer)
        return answer
