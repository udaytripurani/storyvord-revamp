# views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import now
from .models import Connection, ActiveConnection
from .serializers import UserSerializer, ConnectionSerializer, ActiveConnectionSerializer
from rest_framework.views import APIView
User = get_user_model()

# Check if an email exists
class CheckEmailExistsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')

        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response({'exists': True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'exists': False}, status=status.HTTP_200_OK)

class CheckConnectionRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        status_filter = request.query_params.get('status')  # Optional filter for status
        user = request.user

        # Get connection requests where the user is either the requester or the receiver
        connection_requests = Connection.objects.filter(
            Q(requester=user) | Q(receiver=user)
        )

        if status_filter:
            connection_requests = connection_requests.filter(status=status_filter)

        return Response(ConnectionSerializer(connection_requests, many=True).data, status=status.HTTP_200_OK)

# Send a connection request
class SendConnectionRequestView(generics.CreateAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        receiver_email = request.data.get('receiver_email')

        if not receiver_email:
            return Response({'error': 'Receiver email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the connection request already exists
        if Connection.objects.filter(requester=request.user, receiver=receiver).exists():
            return Response({'error': 'Connection request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        connection = Connection.objects.create(requester=request.user, receiver=receiver)
        return Response(ConnectionSerializer(connection).data, status=status.HTTP_201_CREATED)

# Manage a connection request (accept/decline)
class ManageConnectionRequestView(generics.UpdateAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        requester_id = request.data.get('requester_id')
        status_update = request.data.get('status')

        if not requester_id:
            return Response({'error': 'Requester ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if status_update not in ['accepted', 'declined']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            connection = Connection.objects.get(requester_id=requester_id, receiver=request.user)
        except Connection.DoesNotExist:
            return Response({'error': 'Connection request not found'}, status=status.HTTP_404_NOT_FOUND)

        connection.status = status_update
        connection.save()

        if status_update == 'accepted':
            # Ensure an active connection is created only once
            active_connection, created = ActiveConnection.objects.get_or_create(
                user_id_1=min(connection.requester, connection.receiver, key=lambda x: x.id),
                user_id_2=max(connection.requester, connection.receiver, key=lambda x: x.id),
            )

            return Response({
                'message': 'Connection accepted and active connection created',
                'connection': ConnectionSerializer(connection).data,
                'active_connection': ActiveConnectionSerializer(active_connection).data
            }, status=status.HTTP_200_OK)

        return Response(ConnectionSerializer(connection).data, status=status.HTTP_200_OK)

# View active connections
# View active connections directed to the logged-in user
class ViewConnectionsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Filter to get active connections where the user is the receiver
        active_connections = ActiveConnection.objects.filter(user_id_2=user)

        # Return the list of users who requested connections
        connected_users = [conn.user_id_1 for conn in active_connections]

        return User.objects.filter(id__in=[u.id for u in connected_users])
