from django.urls import path
from ui.views import (
    Index,
    Logout,
    Chat,
    ChatAPI,
    chat_no_callback,
    reset_memory,
    DocumentsList,
    DocumentAdd,
    DocumentDeactivate,
    DocumentDelete,
    download_document,
)

urlpatterns = [
    path(r"", Index.as_view()),
    path(r"logout/", Logout.as_view(), name="logout"),
    path(r"chat/", Chat.as_view(), name="chat"),
    path(r"documents/", DocumentsList.as_view(), name="documents"),
    path(r"document/add/", DocumentAdd.as_view(), name="document_add"),
    path(
        r"document/deactivate/<str:id>/",
        DocumentDeactivate.as_view(),
        name="document_deactivate",
    ),
    path(
        r"document/delete/<str:id>/",
        DocumentDelete.as_view(),
        name="document_delete",
    ),
    path(r"document/download/<str:id>/", download_document, name="document_download"),
    path(r"chat/reset/", reset_memory, name="chat_reset"),
    path(r"api/chat/", ChatAPI.as_view(), name="chat_api"),
    path(r"api/chat/nocallback/", chat_no_callback),
]
