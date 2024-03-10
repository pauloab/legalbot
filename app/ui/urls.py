from django.urls import path
from ui.views import Index, Logout, Chat, ChatAPI, reset_chat

urlpatterns = [
    path(r"", Index.as_view()),
    path(r"logout/", Logout.as_view(), name="logout"),
    path(r"chat/", Chat.as_view(), name="chat"),
    path(r"chat/reset/", reset_chat, name="chat_reset"),
    path(r"api/chat/", ChatAPI.as_view(), name="chat_api"),
]
