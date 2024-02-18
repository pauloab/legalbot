from chatbot.memory_storage import MemoryStorage
from dotenv import load_dotenv


class Memmory:

    __memory_prompt = """Sistema: {context}
Tu nombre es: {chatbot_prefix}
Tu rol es: {chatbot_prefix}
El rol del humano es: {human_prefix}
Conversación actual:
{history}"""

    def __init__(
        self,
        context: str,
        userId: str,
        uuid: str = None,
        k=8,
        human_prefix="Humano",
        chatbot_prefix="LegalBot",
    ):
        self.l = k
        self.context = context
        self.message_history = []
        self.human_prefix = human_prefix
        self.chatbot_prefix = chatbot_prefix
        self.uuid = uuid
        self.userId = userId

    def __update_history(self, message):
        self.message_history.append(message)
        if len(self.message_history) > self.l:
            self.message_history = self.message_history[-self.l :]

    def add_human_message(self, message):
        self.__update_history(self.human_prefix + ": " + message)

    def add_chatbot_message(self, message):
        self.__update_history(self.chatbot_prefix + ": " + message)

    def add_interacition(self, human_message, chatbot_message):
        self.add_human_message(human_message)
        self.add_chatbot_message(chatbot_message)

    def get_history_prompt(self):
        messages = "\n".join(self.message_history)
        prompt = self.__memory_prompt.format(
            context=self.context,
            history=messages,
            human_prefix=self.human_prefix,
            chatbot_prefix=self.chatbot_prefix,
        )
        return prompt
