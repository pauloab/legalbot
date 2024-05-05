from pymongo import MongoClient
from chat_agent.stat import Stat


class StatsStorage:

    def __init__(self, mongo_connection_string: str, db_name: str):
        self.client = MongoClient(mongo_connection_string)
        self.database = self.client[db_name]
        self.collection = self.database["stats"]

    def add(self, obj: Stat):
        inserted = self.collection.insert_one(
            {
                "userId": obj.userId,
                "context": obj.context,
                "documents_prompt": obj.documents_prompt,
                "user_prompt": obj.user_prompt,
                "user_prompt_tokens": obj.user_prompt_tokens,
                "chat_response": obj.chat_response,
                "chat_response_tokens": obj.chat_response_tokens,
                "model": obj.model,
            }
        )
        return inserted
