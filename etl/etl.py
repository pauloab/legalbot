from etl.document_selector import DocumentSelector
from etl.document_processor import DocumentProcessor
from etl.embeding_processor import EmbeddingProcessor


def start_etl_process():
    print("ETL process started")
    print("Srtarting smart document selector")
    selector = DocumentSelector()
    embedding_processor = EmbeddingProcessor()

    new = selector.get_new()
    deactivated = selector.get_removed()
    reactivated = selector.get_reactivated()
    processed = selector.get_selected_documents()
    reprocessed = selector.get_reprocess()
    if reactivated:
        print("Documents to be reactivated:")
        print("\n- ".join(reactivated))
        print("Reactivating documents from vector store")
        for doc in reactivated:
            embedding_processor.reactivate_index(doc)
        selector.activate_documents()
        print("Documents reactivated")
    if deactivated:
        print("Documents to be removed:")
        print("\n- ".join(deactivated))
        print("Deactivating documents from vector store")
        selector.remove_documents()
        for doc in deactivated:
            embedding_processor.deactivate_index(doc)
        selector.deactivate_documents()
        print("Documents removed")
    if not processed:
        print("Not new documents found")
        print("ETL process finished")
        return
    if new:
        print("New documents found:")
        print("\n- ".join(new))
    if reprocessed:
        print("Documents to be reprocessed:")
        print("\n- ".join(reprocessed))

    print("Smart document selector finished")
    print("Starting document processing")
    print("Documents to be processed:")
    print("\n- ".join([doc.filename for doc in processed]))
    processor = DocumentProcessor(processed)
    print("Document processing started...")
    processor.process_and_save()
    print("Document processing finished")

    to_vectorize = processor.documents
    print("Srtarting vectorization (new and reprocessed)")
    for doc in to_vectorize:
        embedding_processor.embed_document(doc)
    print("Vectorization finished")
    print("ETL process finished")
