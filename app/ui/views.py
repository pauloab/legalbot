import json

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from ui import validators


class Index(LoginView):
    """
    Carga y procesa el formulario de login
    """

    template_name = "login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = "/chat"


class Logout(LoginRequiredMixin, View):
    """
    Desloguea al usuario
    """

    def get(self, request):
        logout(request)
        return redirect("/")


class Chat(LoginRequiredMixin, View):
    """
    Retorna el template renderizado de la vista de probar chat
    """

    template_name = "chat.html"

    def get(self, request):
        return render(request, self.template_name)


class ChatAPI(View):
    """
    Endpoint público de consulta de respuesta del chatbot
    """

    template_name = "test_chat.html"

    json_template = {
        "Parameters": [{"question:string": "Pregunta ingresada por el usuario"}],
        "Content-Type": "application/json",
    }

    def get(self, request):
        return JsonResponse(self.json_template, safe=False)

    def post(self, request):
        question = None
        http_response = {}

        try:
            question = json.loads(request.body.decode())
            if not validators.is_chatbot_question_valid(question):
                question = None
                raise ValueError()

        except ValueError:
            http_response["response"] = "Objeto JSON no válido"
            http_response["status"] = 400

        if question:
            """chatbot_instance = ChatBotUtils()
            http_response["response"] = chatbot_instance.chatbot_response(
                question["question"].lower()
            )
            http_response["status"] = 200"""

        return JsonResponse(http_response, safe=False, status=http_response["status"])
