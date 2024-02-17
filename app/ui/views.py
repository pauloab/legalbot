

class TestChat(View):
    """
        Retorna el template renderizado de la vista de probar chat
    """
    template_name = "test_chat.html"

    def get(self, request):
        return render(request, self.template_name)
    

class ChatbotAPI(View):
    """
        Endpoint público de consulta de respuesta del chatbot
    """
    template_name = "test_chat.html"

    json_template = {"Parameters": 
                    [   
                        {"question:string":"Pregunta ingresada por el usuario"}
                    ],
                    "Content-Type":"application/json"}

    def get(self, request):
        return JsonResponse(self.json_template, safe=False)

    def post(self, request):
        question = None
        http_response = {}

        try:
            question = json.loads(request.body.decode())
            if not is_chatbot_question_valid(question):
                question = None
                raise ValueError()
            
        except ValueError:
            http_response["response"]="Objeto JSON no válido"
            http_response["status"] = 400

        if question:
            chatbot_instance = ChatBotUtils()
            http_response["response"] = chatbot_instance.chatbot_response(question["question"].lower())
            http_response["status"] = 200

        return JsonResponse(http_response, safe=False, status=http_response["status"])