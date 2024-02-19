class DocumentChunk:

    def __init__(self, content: str, metadata: dict):
        self.content = content
        self.metadata = metadata


class Document:

    def __init__(
        self,
        filename: str,
        filesize: int,
        content: str,
        title: str = None,
        chunks: list[DocumentChunk] = [],
        pages: list = [],
        _id: str = None,
        deactivated: bool = False,
    ):
        self.filename = filename
        self.filesize = filesize
        self.content = content
        self.title = title
        self.chunks = chunks
        self.pages = pages
        self._id = _id
        self.deactivated = deactivated

    def __str__(self):
        return self.title

    def get_metadata(self):

        return {
            "title": self.title,
            "uuid": self._id,
            "deactivated": self.deactivated,
        }
