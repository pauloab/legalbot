from celery import shared_task
from chatbot.memory_storage import MemoryStorage
from chatbot.memory import Memory
from chatbot.chatbot import Chatbot

import os

CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")


@shared_task
def send_chat_message(query:str,user_id:int,context:str,model:str, temperature:float):
    mem_storage = MemoryStorage(CONNECTION_STR,DBNAME)
    memory = mem_storage.get_by_userId(user_id)
    if not memory:
        memory = Memory(context, user_id)
        memory._id = mem_storage.add(memory)
    
    memory.waiting = True
    mem_storage.set_waiting_status(memory._id, memory.waiting)
    chatbot = Chatbot(memory,model, temperature,context)
    answer = chatbot.chat(query)
    mem_storage.update_history(memory._id, memory.message_history)
    memory.waiting = False
    mem_storage.set_waiting_status(memory._id, memory.waiting)
    
    return answer
