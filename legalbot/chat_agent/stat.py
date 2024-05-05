class Stat:

    def __init__(
        self,
        userId: str,
        context: str,
        documents_prompt: str,
        user_prompt: str,
        user_prompt_tokens: int,
        chat_response: str,
        chat_response_tokens: int,
        model: str,
        _id: str = None,
    ):
        self.context = context
        self._id = _id
        self.userId = userId
        self.documents_prompt = documents_prompt
        self.user_prompt = user_prompt
        self.user_prompt_tokens = user_prompt_tokens
        self.chat_response = chat_response
        self.chat_response_tokens = chat_response_tokens
        self.model = model
