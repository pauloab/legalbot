import json
import jsonschema
from jsonschema.validators import validate
from jsonschema.exceptions import ValidationError

chatbotApiSchema = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
    },
    "required": ["question"],
    "additionalProperties": False,
}


def is_chatbot_question_valid(jsonObject) -> bool:
    try:
        validate(jsonObject, schema=chatbotApiSchema)
        return True
    except ValidationError:
        return False
