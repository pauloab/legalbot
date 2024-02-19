from etl.document_storage import DocumentStorage
from etl.pdf_utils import get_text_by_page, load_pdf
from etl.document import Document
from dotenv import find_dotenv, load_dotenv, dotenv_values

from pathlib import Path

# allow importing from other modules
PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    find_dotenv(str(PROJECT_DIR) + "/.env", raise_error_if_not_found=True),
    override=True,
)
import os

DATA_DIR = os.environ.get("DATA_DIR")
CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")


class DocumentSelector:
    def __init__(self):
        self.__filenames = self.__read()
        self.__storage = DocumentStorage(CONNECTION_STR, DBNAME)

    def __read(self):
        filenames = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".pdf"):
                filenames.append(filename)
        return filenames

    def get_new(self):
        unvectorized_documents = []
        for filename in self.__filenames:
            document = self.__storage.get_by_filename(filename)
            if not document:
                unvectorized_documents.append(filename)
        return unvectorized_documents

    def get_reprocess(self):
        updated_filenames = []
        for filename in self.__filenames:
            document = self.__storage.get_by_filename(filename)
            if document:
                if document["filesize"] != os.path.getsize(
                    os.path.join(DATA_DIR, filename)
                ):
                    updated_filenames.append(filename)
        return updated_filenames

    def get_reactivated(self):
        reactivated = []
        for filename in self.__filenames:
            document = self.__storage.get_by_filename(filename)
            if document:
                if (
                    document["filesize"]
                    == os.path.getsize(os.path.join(DATA_DIR, filename))
                    and document["deactivated"]
                ):
                    reactivated.append(filename)
        return reactivated

    def get_removed(self):
        registred_documents = self.__storage.getAll()
        removed_documents = []
        for document in registred_documents:
            if document.filename not in self.__filenames:
                removed_documents.append(document.filename)
        return removed_documents

    def activate_documents(self):
        for filename in self.get_reactivated():
            self.__storage.activate_document(filename)

    def remove_documents(self):
        for filename in self.get_removed():
            self.__storage.delete_document(filename)

    def deactivate_documents(self):
        removed_documents = self.get_removed()
        for filename in removed_documents:
            self.__storage.deactivate_document(filename)

    def get_selected_documents(self):
        out_docs = []
        filenames = self.get_new() + self.get_reprocess()
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
                    pages=pages,
                )
            )
        return out_docs
