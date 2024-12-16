# chat/urls.py
from django.urls import path
from .views.template_view import chat_page , wss_page  # Import template view
from .views.api_view import *    # Import API view
from .views.requirement import CrewOnly, Requirement

urlpatterns = [
    path('', chat_page, name='chat_page'),             # URL for rendering chat UI
    
    path('ai_chat/', wss_page, name='wss_page'),
    
    path('v2/requirement/', Requirement.as_view(), name='requirement'),
    path('v2/crew-requirement/',CrewOnly.as_view(), name='crew-requirement'),
    
    # URL for retrieving chat sessions for the authenticated user
    path('ai_chat/sessions/', UserChatSessionsAPIView.as_view(), name='user_chat_sessions'),
    
    # URL for retrieving chat history for a specific session ID
    path('ai_chat/history/<str:id>/', ChatHistoryAPIView.as_view(), name='chat_history'),
]