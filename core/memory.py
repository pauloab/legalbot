class Memmory:

    __memory_prompt = """Sistema: {context}
Tu nombre es: {chatbot_prefix}
Tu rol es: {chatbot_prefix}
El rol del humano es: {human_prefix}
Conversación actual:
{history}"""

    def __init__(
        self, context: str, k=8, human_prefix="Humano", chatbot_prefix="LegalBot"
    ):
        self.__l = k
        self.__context = context
        self.__message_history = []
        self.human_prefix = human_prefix
        self.chatbot_prefix = chatbot_prefix

    def __update_history(self, message):
        self.__message_history.append(message)
        if len(self.__message_history) > self.__l:
            self.__message_history = self.__message_history[-self.__l :]

    def add_human_message(self, message):
        self.__update_history(self.human_prefix + ": " + message)

    def add_chatbot_message(self, message):
        self.__update_history(self.chatbot_prefix + ": " + message)

    def add_interacition(self, human_message, chatbot_message):
        self.add_human_message(human_message)
        self.add_chatbot_message(chatbot_message)

    def get_context(self):
        return self.__context

    def get_history(self):
        return self.__message_history

    def get_history_prompt(self):
        messages = "\n".join(self.__message_history)
        prompt = self.__memory_prompt.format(
            context=self.__context,
            history=messages,
            human_prefix=self.human_prefix,
            chatbot_prefix=self.chatbot_prefix,
        )
        return prompt
