from celery import shared_task
from chat_agent.memory_storage import MemoryStorage
from chat_agent.memory import Memory
from chat_agent.agent import ChatAgent
from chat_agent.exceptions import ChatbotException
from chat_agent.stats_storage import StatsStorage
from processing.pdf_utils import load_pdf, get_text_by_page
import os
import traceback
from io import BytesIO

from processing.document_storage import DocumentStorage, Document
from processing.document_processor import DocumentProcessor
from processing.embeding_processor import EmbeddingProcessor

CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")
DOCUMENT_PATH = os.environ.get("DATA_DIR")
EMBEDING_STORAGE = os.environ.get("EMBEDING_STORAGE")


@shared_task
def send_chat_message(
    user_id: str,
    query: str,
    model: str,
    temperature: float,
):
    mem_storage = MemoryStorage(CONNECTION_STR, DBNAME)
    memory = mem_storage.get_by_userId(user_id)
    stats_storage = StatsStorage(CONNECTION_STR, DBNAME)
    try:
        if not memory:
            raise Exception("Memoria inexistente")
        chatbot = ChatAgent(memory, stats_storage, model, temperature, memory.context)
        answer = chatbot.chat(query)
        mem_storage.update_history(memory._id, memory.message_history)
    except ChatbotException as ex:
        raise ex
    except Exception as ex:
        print(traceback.format_exc())
        raise ChatbotException("Hubo un error inesperado al procesar la consulta")
    return answer


@shared_task
def add_file(fileBytes, filename):

    print("Saving new document")
    abs_path = os.path.join(DOCUMENT_PATH, filename)

    with open(abs_path, "wb") as file:
        file.write(fileBytes)

    pdf = load_pdf(abs_path)
    pages = get_text_by_page(pdf)
    content = "".join(pages)
    doc = Document(
        filename=filename,
        filesize=os.path.getsize(abs_path),
        content=content,
        pages=pages,
    )
    print("Starting processing!")
    processor = DocumentProcessor([doc])
    processor.process()  # Procesa el documento y lo almacena en mongoDB
    to_vectorize = processor.documents
    print("Vectorizing!")
    embedding_processor = EmbeddingProcessor(embedding_storage=EMBEDING_STORAGE)
    embedding_processor.embed_document(to_vectorize[0])
    print("Saving to MongoDB!")
    doc_storage = DocumentStorage(CONNECTION_STR, DBNAME)
    doc_storage.add(to_vectorize[0])
    print("Finished!")
