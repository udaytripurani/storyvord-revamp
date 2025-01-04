from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ai_assistant.models import ChatMessage
from ai_assistant.models import ChatSession
from ai_assistant.serializers import ChatMessageSerializer
from ai_assistant.serializers import ChatSessionSerializer
from rest_framework.pagination import PageNumberPagination

class UserChatSessionsAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        chat_sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionSerializer(chat_sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChatHistoryPagination(PageNumberPagination):
    page_size = 10  # Default number of messages per page

class ChatHistoryAPIView(APIView):
    pagination_class = ChatHistoryPagination

    def get(self, request, id, *args, **kwargs):
        try:
            chat_messages = ChatMessage.objects.filter(session_id=id).select_related('session', 'user').order_by('timestamp')
            if not chat_messages.exists():
                return Response({"detail": "Chat session not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_messages = paginator.paginate_queryset(chat_messages, request)
            serializer = ChatMessageSerializer(paginated_messages, many=True)
            
            return paginator.get_paginated_response(serializer.data)
        
        except ChatMessage.DoesNotExist:
            return Response({"detail": "Chat session not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)