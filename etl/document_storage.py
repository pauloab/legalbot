from pymongo import MongoClient
from etl.document import Document


class DocumentStorage:
    def __init__(self, mongo_connection_string: str, db_name: str):
        self.client = MongoClient(mongo_connection_string)
        self.database = self.client[db_name]
        self.collection = self.database["documents"]

    def add(self, document_obj: Document):
        """
        Crea un nuevo documento
        """
        inserted = self.collection.insert_one(
            {
                "title": document_obj.title,
                "filename": document_obj.filename,
                "filesize": document_obj.filesize,
                "pages": document_obj.pages,
                "chunks": document_obj.chunks,
                "content": document_obj.content,
                "deactivated": False,
            }
        )
        return inserted.inserted_id

    def getAll(self):
        return self.collection.find()

    def get_by_filename(self, filename):
        return self.collection.find_one({"filename": filename})

    def get_by_uuid(self, uuid):
        return self.collection.find_one({"_id": uuid})

    def activate_document(self, filename):
        self.collection.update_one(
            {"filename": filename}, {"$set": {"deactivated": False}}
        )

    def deactivate_document(self, filename):
        self.collection.update_one(
            {"filename": filename}, {"$set": {"deactivated": True}}
        )

    def delete_document(self, filename):
        self.collection.delete_one({"filename": filename})
