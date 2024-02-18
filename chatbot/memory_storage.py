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
            }
        )
        return inserted.inserted_id

    def getAll(self):
        return self.collection.find()

    def filter_by_userId(self, userId) -> list[Memory]:
        out = []
        for memory in self.collection.find({"userId": userId}):
            out.append(Memory(**memory))

    def get_by_uuid(self, uuid):
        return self.collection.find_one({"_id": uuid})

    def update_history(self, uuid, message_history: list[str]):
        self.collection.update_one(
            {"_id": uuid},
            {
                "$set": {
                    "message_history": message_history,
                }
            },
        )
