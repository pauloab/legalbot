import json

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from ui import validators, models, tasks
from chatbot.memory_storage import MemoryStorage

import os

CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")


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
        storage = MemoryStorage(CONNECTION_STR, DBNAME)
        memory = storage.get_by_userId(request.user.id)
        history = memory.get_clean_message_history()
        return render(request, self.template_name, {"messages": history})


class ChatAPI(View):
    """
    Endpoint público de consulta de respuesta del chatbot
    """

    template_name = "test_chat.html"

    def get(self, request):
        storage = MemoryStorage(CONNECTION_STR, DBNAME)
        memory = storage.get_by_userId(request.user.id)
        history = memory.get_clean_message_history()
        http_response = {
            "waiting": memory.waiting,
            "response": history[-1] if history else "",
            "status": 200,
        }
        return JsonResponse(http_response, safe=False)

    def post(self, request):
        json_req = None
        http_response = {}

        try:
            json_req = json.loads(request.body.decode())
            if not validators.is_chatbot_question_valid(json_req):
                json_req = None
                raise ValueError()

        except ValueError:
            http_response["response"] = "Objeto JSON no válido"
            http_response["status"] = 400

        if json_req:
            user_id = request.user.id
            contexto = models.Configuracion.objects.get(clave="contexto").valor
            modelo = models.Configuracion.objects.get(clave="modelo").valor
            temperature = models.Configuracion.objects.get(clave="temperatura").valor
            tasks.send_chat_message.delay(json_req["question"], user_id, contexto, modelo, temperature)
            http_response["response"] = {"response": "Preguntando..."}
            http_response["status"] = 200
        return JsonResponse(http_response, safe=False, status=http_response["status"])

def reset_chat(request):
    storage = MemoryStorage(CONNECTION_STR, DBNAME)
    memory = storage.get_by_userId(request.user.id)
    memory.message_history = []
    storage.update_history(memory._id, memory.message_history)
    return redirect("/chat")
