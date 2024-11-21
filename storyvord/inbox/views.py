from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from .models import DialogsModel, MessageModel, RoomModel
from .serializers import DialogSerializer, MessageSerializer, RoomSerializer, RoomMessageSerializer
from accounts.models import User
from rest_framework.pagination import LimitOffsetPagination

class DialogListView(APIView, LimitOffsetPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dialogs = DialogsModel.objects.filter(Q(user1=request.user) | Q(user2=request.user)) \
            .select_related('user1', 'user2')

        paginated_dialogs = self.paginate_queryset(dialogs, request, view=self)
        serializer = DialogSerializer(paginated_dialogs, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class DialogMessagesView(APIView, LimitOffsetPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)

        # Ensure dialog exists
        dialog = DialogsModel.dialog_exists(request.user, other_user)
        if not dialog:
            return Response({"detail": "Dialog not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch and paginate messages
        messages = MessageModel.objects.filter(
            Q(sender=request.user, recipient=other_user) |
            Q(sender=other_user, recipient=request.user)
        ).select_related('sender', 'recipient').order_by('created')

        paginated_messages = self.paginate_queryset(messages, request, view=self)
        serializer = MessageSerializer(paginated_messages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        recipient = get_object_or_404(User, id=user_id)

        if recipient == request.user:
            return Response({"detail": "Cannot send message to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        text = request.data.get('text', '').strip()
        if not text:
            return Response({"detail": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        message = MessageModel.objects.create(sender=request.user, recipient=recipient, text=text)
        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        message = get_object_or_404(MessageModel, id=message_id, recipient=request.user)

        if message.read:
            return Response({"detail": "Message already marked as read."}, status=status.HTTP_400_BAD_REQUEST)

        message.read = True
        message.save()
        return Response({"detail": "Message marked as read."}, status=status.HTTP_200_OK)
    
class RoomListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = request.user.rooms.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        name = request.data.get('name')
        member_ids = request.data.get('members', [])
        if not name or not member_ids:
            return Response({"detail": "Room name and members are required."}, status=status.HTTP_400_BAD_REQUEST)

        members = User.objects.filter(id__in=member_ids)
        room = RoomModel.objects.create(name=name)
        room.members.set(members)
        room.members.add(request.user)  # Include the creator as a member
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoomMessagesView(APIView, LimitOffsetPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(RoomModel, id=room_id, members=request.user)
        messages = room.messages.select_related('sender').order_by('created')
        paginated_messages = self.paginate_queryset(messages, request, view=self)
        serializer = RoomMessageSerializer(paginated_messages, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, room_id):
        room = get_object_or_404(RoomModel, id=room_id, members=request.user)
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"detail": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        message = MessageModel.objects.create(sender=request.user, room=room, text=text)
        serializer = RoomMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

