class Memory:

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
        _id: str = None,
        k=8,
        human_prefix="Humano",
        chatbot_prefix="LegalBot",
        waiting=False,
        message_history=[],
    ):
        self.l = k
        self.context = context
        self.message_history = message_history
        self.human_prefix = human_prefix
        self.chatbot_prefix = chatbot_prefix
        self._id = _id
        self.userId = userId
        self.waiting = waiting   
        self.history_window = self.message_history[-k:] 

    def __update_history(self, message):
        self.message_history.append(message)
        self.history_window.append(message)
        if len(self.history_window) > self.l:
            self.history_window = self.history_window[-self.l :]

    def add_human_message(self, message: str):
        self.__update_history(self.human_prefix + ": " + message)

    def add_chatbot_message(self, message: str):
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

    def get_clean_message_history(self):
        clean_history = []
        for message in self.message_history:
            if self.chatbot_prefix in message:
                clean_history.append(message.replace(self.chatbot_prefix + ": ", ""))
            elif self.human_prefix in message:
                clean_history.append(message.replace(self.human_prefix + ": ", ""))
        return clean_history
