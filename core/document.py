class DocumentChunk:
    def __init__(self, content: str, meta: dict):
        self.content = content
        self.metadata = meta


class RAWDocument:
    def __init__(self, pages_extracted: list):
        self.text = "\n".join(pages_extracted)
        self.pages = pages_extracted


class Document:

    def __init__(self, title, raw_document: RAWDocument, clean_text: str):
        self.title = title
        self.raw_document = raw_document
        self.chunks = []
        self.clean_text = clean_text

    def __str__(self):
        return self.title
