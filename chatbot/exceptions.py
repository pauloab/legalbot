class ChatbotException(Exception):
    message = "Error inesperado al procesar la consulta"

    def __init__(self, message=None):
        self.message = message or self.message

    def __str__(self):
        return self.message

    def __dict__(self):
        return {"message": self.message}
