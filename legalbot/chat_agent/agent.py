from openai import OpenAI
from langchain.llms.openai import OpenAI as langchainOpenAI
from chat_agent.memory import Memory
from chat_agent.exceptions import ChatbotException
from processing.document import Document
from chat_agent.document_retriever import DocumentRetriever
from chat_agent.stat import Stat
from chat_agent.stats_storage import StatsStorage
import tiktoken


class ChatAgent:

    DEFAULT_CONTEXT = """Eres un bot de la Universidad Técnica de Machala que contesta solamente dudas sobre normas legales internas de la universidad. 
    Tienes prohibido contestar cualquier consulta fuera de este dominio"""

    CLASSIFICATION_PROMPT = """Sistema: Responde con 'SI' o 'NO' de acuerdo a la siguiente interrogante. Basado en el texto de la consulta a continuación: 
    '{query}'
    ¿Se requiere recurrir a reglamentos de la universidad para responderla?
    Respuesta: """

    FORMAT_PROMPT = "Tu respuesta debe estar en formato HTML, usando solamente etiquetas: p, b, i, ul, li, br, span"

    TOKEN_LIMITS = {
        "gpt-4o": 128000,
        "gpt-4o-mini":128000,
        "gpt-4-0125-preview": 128000,
        "gpt-4-turbo-preview": 128000,
        "gpt-4-1106-preview": 128000,
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-2024-04-09": 128000,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0613": 32768,
        "gpt-3.5-turbo-0125": 16385,
        "gpt-3.5-turbo": 16385,
        "gpt-3.5-turbo-1106": 16385,
        "gpt-3.5-turbo-instruct": 4096,
        "gpt-3.5-turbo-16k": 16385,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-16k-0613": 16385,
    }

    __legal_docs = None
    __model_name = None
    memory = None

    def __init__(
        self,
        memory: Memory,
        stats_storage: StatsStorage,
        model_name="gpt-3.5-turbo",
        temperature=0.5,
        chatbot_context=DEFAULT_CONTEXT,
        sumarizer_model="gpt-3.5-turbo-instruct",
    ):
        self.__client = OpenAI()
        self.__document_retriever = DocumentRetriever()
        self.__chatbot_context = chatbot_context
        self.__temperature = temperature
        self.__model_name = model_name
        self.__sumarizer_model = sumarizer_model
        self.__sumarizer = langchainOpenAI(model_name=sumarizer_model, temperature=0)
        self.memory = memory
        self.stats_storage = stats_storage

    def is_consulta(self, query: str):
        prompt = self.CLASSIFICATION_PROMPT.format(query=query)
        answer = self.__sumarizer(prompt)
        return answer == "SI"

    def get_chat_history(self, query: str):

        memory_history = self.memory.get_history()
        # if self.is_consulta(query):
        docs_prompt = self.__document_retriever.get_document_query_prompt(query)
        memory_history.append({"role": "system", "content": docs_prompt})
        memory_history.append({"role": "system", "content": self.FORMAT_PROMPT})
        return memory_history

    def __tokens_count(self, messages, model):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4o-mini"
            "gpt-4o",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4
            tokens_per_name = -1
        elif "gpt-3.5-turbo" in model:
            return self.__tokens_count(messages, model="gpt-3.5-turbo-0125")
        elif "gpt-4" in model:
            return self.__tokens_count(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3
        return num_tokens

    def chat(self, query: str):
        self.memory.add_human_message(query)
        history = self.get_chat_history(query)
        token_count = self.__tokens_count(history, self.__model_name)
        if (
            token_count
            > self.TOKEN_LIMITS[self.__model_name]
            # or token_count > self.TOKEN_LIMITS[self.__sumarizer_model]
        ):
            raise ChatbotException(
                "Parece que tu consulta es demasiado extensa. Por favor, reescribe tu consulta o reinicia la conversación."
            )
        print("Chat Started")
        answer = self.__client.chat.completions.create(
            model=self.__model_name,
            temperature=float(self.__temperature),
            messages=history,
        )
        print("Chat Ended")
        answer = answer.choices[0].message.content
        self.memory.add_chatbot_message(answer)
        """
        stats = Stat(
            userId=self.memory.userId,
            context=self.memory.context,
            documents_prompt=self.__document_retriever.get_document_query_prompt(query),
            user_prompt=query,
            user_prompt_tokens=token_count,
            chat_response=answer,
            chat_response_tokens=self.__tokens_count([{"": answer}], self.__model_name),
            model=self.__model_name,
        )
        self.stats_storage.add(stats)
        """
        return answer
