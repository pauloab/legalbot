from pymongo import MongoClient
from chatbot.memory import Memory


class MemoryStorage:

    def __init__(self, mongo_connection_string: str, db_name: str):
        self.client = MongoClient(mongo_connection_string)
        self.database = self.client[db_name]
        self.collection = self.database["chats"]

    def add(self, memory_obj: Memory):
        inserted = self.collection.insert_one(
            {
                "human_prefix": memory_obj.human_prefix,
                "chatbot_prefix": memory_obj.chatbot_prefix,
                "context": memory_obj.context,
                "message_history": memory_obj.message_history,
                "userId": memory_obj.userId,
                "waiting": memory_obj.waiting,
                "k": memory_obj.l,
            }
        )
        return inserted

    def set_waiting_status(self, _id, waiting):
        self.collection.update_one(
            {"_id": _id},
            {
                "$set": {
                    "waiting": waiting,
                }
            },
        )

    def get_by_userId(self, userId) -> Memory:
        memory = self.collection.find_one({"userId": userId})
        if not memory:
            return None
        return Memory(**memory)

    def get_by_uuid(self, uuid):
        memory = self.collection.find_one({"_id": uuid})
        if not memory:
            return None
        return Memory(**memory)

    def update_history(self, uuid, message_history: list[str]):
        self.collection.update_one(
            {"_id": uuid},
            {
                "$set": {
                    "message_history": message_history,
                }
            },
        )
