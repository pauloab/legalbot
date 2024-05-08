import json

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from ui import validators, models, tasks, forms
from chat_agent.memory_storage import MemoryStorage
from chat_agent.memory import Memory
from processing.document_storage import DocumentStorage
from processing.embeding_processor import EmbeddingProcessor
from celery.result import AsyncResult

import os

CONNECTION_STR = os.environ.get("MONGO_CONNECTION_STRING")
DBNAME = os.environ.get("MONGO_DBNAME")
DOCUMENT_PATH = os.environ.get("DATA_DIR")
EMBEDING_STORAGE= os.environ.get("EMBEDING_STORAGE")

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


class DocumentsList(LoginRequiredMixin, View):
    """
    Retorna la lista de documentos subidos al sistema
    """

    template_name = "documents_list.html"

    def get(self, request):
        storage = DocumentStorage(CONNECTION_STR, DBNAME)
        documents = storage.getAll()
        return render(request, self.template_name, {"documents": documents})


class DocumentAdd(LoginRequiredMixin, View):
    """
    Retorna el formulario de nuevo doccumento
    """

    def get(self, request):
        form = forms.DocumentForm()
        return render(request, "document_add.html", {"form": form})

    def post(self, request):
        form = forms.DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Extraer el archivo del form
            file = request.FILES["file"]
            # Guardar el archivo en el servidor
            filename = file.name
            tasks.add_file.delay(file.read(), filename)
            messages.add_message(
                request,
                messages.INFO,
                "Se está procesando el documento '"
                + filename
                + "', una vez procesado aparecerá en la lista. Este proceso puede tardar varios minutos",
            )
            return redirect("documents")
        return render(request, "document_add.html", {"form": form})


class DocumentDeactivate(LoginRequiredMixin, View):

    def get(self, request, id):
        storage = DocumentStorage(CONNECTION_STR, DBNAME)
        document = storage.get_by_uuid(id)
        ep = EmbeddingProcessor()
        if not document:
            return redirect("documents")
        if document.deactivated:
            ep.reactivate_index(document.filename)
            storage.activate_document_by_id(id)
            messages.add_message(
                request,
                messages.INFO,
                "Se reactivó el documento '{}'".format(document.title),
            )
        else:
            ep.deactivate_index(document.filename)
            messages.add_message(
                request,
                messages.INFO,
                "Se desactivó el documento '{}'".format(document.title),
            )
            storage.deactivate_document_by_id(id)
        return redirect("documents")


class DocumentDelete(LoginRequiredMixin, View):

    def get(self, request, id):
        storage = DocumentStorage(CONNECTION_STR, DBNAME)
        document = storage.get_by_uuid(id)
        if not document:
            messages.add_message(
                request, messages.INFO, "No se encontro el documento solicitado"
            )
            return redirect("documents")
        ep = EmbeddingProcessor(embedding_storage=EMBEDING_STORAGE)
        ep.delete_index(document.filename)
        os.remove(os.path.join(DOCUMENT_PATH, document.filename))
        storage.delete_document(document.filename)
        messages.add_message(
            request,
            messages.INFO,
            "Se elimino el documento '{}'".format(document.title),
        )
        return redirect("documents")


class ChatAPI(View):
    """
    Endpoint público de consulta de respuesta del chatbot
    """

    MAX_INTERACTIONS = 5
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSerhF9ABz6V-i7VpudENvIWSipjgMHB7YW6SzFl2Vnidha0Og/viewform?usp=sf_link"
    FINAL_MESSAGE = """
            Gracias por colaborar en nuestro proyecto!. Haz alcanzado el límite de interacciones con
            el bot. Para finalizar, por favor completa la siguiente encuesta de satisfacción. <br>
            <a href="{url}">Ir a la encuesta</a>                                                                                         
            """.format(
                    url=FORM_URL
            )

    def get(self, request):
        waiting = False
        response = ""
        status = 200

        if request.session.get("limit_reached", False):
            response = self.FINAL_MESSAGE
        else:
            storage = MemoryStorage(CONNECTION_STR, DBNAME)
            memory = storage.get_by_userId(request.user.id)

            if not memory:
                contexto = models.Configuracion.objects.get(clave="contexto").valor
                memory = Memory(contexto, request.user.id)
                memory._id = storage.add(memory)

            task_id = memory.task_id

            if task_id:

                answer = AsyncResult(task_id)

                if not answer.ready():
                    waiting = True
                    response = ""
                elif answer.successful():
                    waiting = False
                    response = answer.get()
                    memory.task_id = None
                    storage.set_task_id(memory._id, memory.task_id)
                    if not request.user.is_staff and memory.message_history.__len__() >= self.MAX_INTERACTIONS*2:
                        request.session["limit_reached"] = True
                        response += "<br><br>" + self.FINAL_MESSAGE
                elif answer.failed():
                    waiting = False
                    response = answer.result.message
                    status = 500
                    memory.task_id = None
                    storage.set_task_id(memory._id, memory.task_id)

        payload = {
            "waiting": waiting,
            "response": response,
            "status": status,
        }
        return JsonResponse(payload, status=status, safe=False)

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
            
            if request.session.get("limit_reached", False):
                http_response["response"] = self.FINAL_MESSAGE
            else :                                                                                      
                user_id = request.user.id
                contexto = models.Configuracion.objects.get(clave="contexto").valor
                modelo = models.Configuracion.objects.get(clave="modelo").valor
                temperature = models.Configuracion.objects.get(clave="temperatura").valor

                mem_storage = MemoryStorage(CONNECTION_STR, DBNAME)
                memory = mem_storage.get_by_userId(user_id)

                if not memory:
                    memory = Memory(context=contexto, userId=user_id)
                    memory._id = mem_storage.add(memory)

                task = tasks.send_chat_message.delay(
                    user_id, json_req["question"], modelo, temperature
                )

                memory.task_id = task.task_id
                mem_storage.set_task_id(memory._id, memory.task_id)

                http_response["response"] = {"response": "Preguntando..."}
                http_response["status"] = 200
        return JsonResponse(http_response, safe=False, status=http_response["status"])


class Chat(LoginRequiredMixin, View):
    """
    Retorna el template renderizado de la vista de probar chat
    """

    template_name = "chat.html"

    def get(self, request):
        storage = MemoryStorage(CONNECTION_STR, DBNAME)
        memory = storage.get_by_userId(request.user.id)
        if not memory:
            contexto = models.Configuracion.objects.get(clave="contexto").valor
            memory = Memory(
                contexto, request.user.id, human_name=request.user.first_name
            )
            memory._id = storage.add(memory)
        history = memory.get_clean_message_history()
        return render(request, self.template_name, {"history": history})


def reset_memory(request):
    storage = MemoryStorage(CONNECTION_STR, DBNAME)
    memory = storage.get_by_userId(request.user.id)
    memory.message_history = []
    storage.update_history(memory._id, memory.message_history)
    return redirect("/chat")

def download_document(request, id):
    storage = DocumentStorage(CONNECTION_STR, DBNAME)
    document = storage.get_by_uuid(id)
    if not document:
        messages.add_message(
            request, messages.INFO, "No se encontro el documento solicitado"
        )
        return redirect("documents")
    
    with open(os.path.join(DOCUMENT_PATH, document.filename), 'rb') as f:
           file_data = f.read()
        
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename={filename}'.format(filename=document.filename)
    return response
