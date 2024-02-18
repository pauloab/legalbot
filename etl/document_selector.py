from dotenv import load_dotenv
from etl.document_storage import DocumentStorage
from etl.pdf_utils import get_text_by_page, load_pdf
from etl.document import Document

load_dotenv()
import os

DATA_DIR = os.environ.get("DATA_DIR")
CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")


class DocumentSelector:
    def __init__(self):
        pass

    def __read(self):
        filenames = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".pdf"):
                filenames.append(filename)
        return filenames

    def __get_unvectorized(self):
        filenames = self.__read()
        unvectorized_documents = []
        storage = DocumentStorage(CONNECTION_STR, DBNAME)
        for filename in filenames:
            document = storage.get_by_filename(filename)
            if not document:
                unvectorized_documents.append(filename)
            else:
                if document["filesize"] != os.path.getsize(
                    os.path.join(DATA_DIR, filename)
                ):
                    storage.delete_document(filename)
                    unvectorized_documents.append(filename)
                elif document["deactivated"] == True:
                    storage.activate_document(filename)
        return unvectorized_documents

    def get_selected_documents(self):
        out_docs = []
        filenames = self.__get_unvectorized()
        for filename in filenames:
            abs_path = os.path.join(DATA_DIR, filename)
            pdf = load_pdf(abs_path)
            size = os.path.getsize(abs_path)
            pages = get_text_by_page(pdf)
            content = "".join(pages)
            out_docs.append(
                Document(
                    filename=filename,
                    filesize=size,
                    content=content,
                )
            )
        return out_docs
