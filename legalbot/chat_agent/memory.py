class Memory:

    def __init__(
        self,
        context: str,
        userId: str,
        _id: str = None,
        k=4,
        human_name="Humano",
        chatbot_name="LegalBot",
        message_history=[],
        task_id=None,
    ):
        self.l = k
        self.context = context
        self.message_history = message_history
        self.human_name = human_name
        self.chatbot_name = chatbot_name
        self._id = _id
        self.userId = userId
        self.history_window = self.message_history[-k:]
        self.task_id = task_id

    def __update_history(self, rol, name, message):
        if not name:
            self.message_history.append({"role": rol, "content": message})
            self.history_window.append({"role": rol, "content": message})
        else:
            self.message_history.append({"role": rol, "name": name, "content": message})
            self.history_window.append({"role": rol, "name": name, "content": message})
        if len(self.history_window) > self.l:
            self.history_window = self.history_window[-self.l :]

    def add_human_message(self, message: str):
        self.__update_history("user", self.human_name, message)

    def add_chatbot_message(self, message: str):
        self.__update_history("assistant", self.chatbot_name, message)

    def add_system_message(self, message: str):
        self.__update_history("system", None, message)

    def add_interacition(self, human_message, chatbot_message):
        self.add_human_message(human_message)
        self.add_chatbot_message(chatbot_message)

    def get_clean_message_history(self):
        clean_history = []
        for message in self.message_history:
            if message["role"] != "system":
                clean_history.append(message["content"])
        return clean_history

    def get_history(self):
        contextualized_history = [x for x in self.history_window]
        contextualized_history.insert(0, {"role": "system", "content": self.context})
        return contextualized_history
