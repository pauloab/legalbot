from django.urls import path
from ui.views import Index, Logout, Chat, ChatAPI

urlpatterns = [
    path(r"", Index.as_view()),
    path(r"logout/", Logout.as_view(), name="logout"),
    path(r"chat/", Chat.as_view(), name="chat"),
    path(r"api/chat/", ChatAPI.as_view(), name="chat_api"),
]
