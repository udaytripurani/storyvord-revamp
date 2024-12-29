from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from .models import Ticket, Comment
from .serializers import TicketSerializer, CommentSerializer
from .utils import send_email_to_user


from .serializers import TicketSerializer, CommentSerializer, AgentSerializer

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import Agent
from datetime import datetime, timedelta
from django.conf import settings
import jwt

  

class AgentLoginView(APIView):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        

        
        if not email or not password:
            
            raise ValidationError("Email and password are required.")
        
        try:
           
            agent = Agent.objects.get(email=email)
            

           
            if check_password(password, agent.password):
                
                refresh_token, access_token = self.create_jwt_token(agent)
                
                return Response({
                    'refresh': refresh_token,
                    'access': access_token,
                })
            else:
                
                raise ValidationError("Invalid credentials")

        except Agent.DoesNotExist:
            
            raise ValidationError("Agent not found")
        except Exception as e:
           
            return Response({
                "status": False,
                "code": 500,
                "message": "An unexpected error occurred. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_jwt_token(self, agent):
        """
        Creates a JWT token for the authenticated agent.
        """
        payload = {
            'id': agent.id,
            'email': agent.email,
            'name': agent.name,
            'is_active': agent.is_active,
            'exp': datetime.utcnow() + timedelta(hours=24),  
            'iat': datetime.utcnow(),  
        }

        
        refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        
        access_token_payload = payload.copy()
        access_token_payload['exp'] = datetime.utcnow() + timedelta(minutes=15)  # Shorter expiration for access token
        access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

        
        return refresh_token, access_token
  






# Agent Creation API (Superuser Only)
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import Agent
from .serializers import AgentSerializer

class AgentCreateView(generics.CreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure the user creating the agent is a superuser
        if not self.request.user.is_superuser:
            raise ValidationError("You must be a superuser to create agents.")
        
        # Get the password from the request data
        password = self.request.data.get('password')

        # Ensure password is provided
        if not password:
            raise ValidationError("Password is required to create an agent.")
        
        # Create the agent instance (without setting the password yet)
        agent = serializer.save()

        # Hash the password and save it to the agent instance
        agent.set_password(password)

        # Save the agent with the hashed password
        agent.save()
 # Save the agent with the hashed password


class TicketListCreateView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            
            new_ticket = serializer.save(created_by=self.request.user)

            
            send_email_to_user(self.request.user.email, new_ticket.ticket_id)
        except Exception as e:
            
            raise ValidationError("There was an error while creating the ticket.")

import logging
from django.utils.timezone import now
from django.conf import settings
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import Ticket, Agent
from .serializers import TicketSerializer
from .utils import send_email_to_agent

logger = logging.getLogger(__name__)

class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Override the default method to get the ticket using the ticket_id (string).
        """
        ticket_id = self.kwargs['ticket_id']
        try:
            return Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError(f"Ticket with ID {ticket_id} does not exist.")

    def perform_update(self, serializer):
        """
        Handle updates, including assigning tickets to agents (only by superuser).
        """
        ticket_id = self.kwargs['ticket_id']
        ticket = self.get_object()

        # Only superusers can assign tickets
        if 'assigned_to' in self.request.data:
            if not self.request.user.is_superuser:
                raise ValidationError("Only superusers can assign tickets to agents.")
            assigned_agent = self.request.data['assigned_to']
            try:
                agent = Agent.objects.get(id=assigned_agent)
                serializer.save(assigned_to=agent)

                # Send email to the assigned agent
                send_email_to_agent(agent.email, ticket_id)

            except Agent.DoesNotExist:
                raise ValidationError("Assigned agent does not exist.")
        else:
            serializer.save()

        # Handle status changes
        if 'status' in self.request.data:
            status = self.request.data['status']
            if status == 'resolved':
                serializer.save(resolved_at=now())
            elif status == 'closed':
                serializer.save(closed_at=now())
            elif status == 'reopened':
                serializer.save(status='reopened')
            else:
                serializer.save()


from .authentication import AgentAuthentication  # Import the custom authentication class

import logging
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Ticket
from .serializers import TicketSerializer
from .authentication import AgentAuthentication  # Custom authentication class

logger = logging.getLogger(__name__)

class AgentTicketListView(generics.ListAPIView):
    """
    View for agents to see the tickets assigned to them.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [AgentAuthentication]  # Use the custom authentication class

    def get_queryset(self):
        """
        Return only tickets assigned to the logged-in agent.
        """
        logger.info(f"Fetching tickets for agent: {self.request.user}")
        return Ticket.objects.filter(assigned_to=self.request.user)


class UpdateTicketStatusView(APIView):
    """
    API endpoint to update the status of a ticket.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [AgentAuthentication]

    def put(self, request, ticket_id):
        try:
            # Use ticket_id field instead of id
            ticket = Ticket.objects.get(ticket_id=ticket_id, assigned_to=request.user)
        except Ticket.DoesNotExist:
            logger.warning(f"Ticket not found or not assigned to user: {request.user}")
            return Response({"error": "Ticket not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error when retrieving ticket: {e}")
            return Response({"status": False, "code": 500, "message": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        status_to_update = request.data.get("status")
        if not status_to_update:
            logger.warning("No status provided in the request.")
            return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket.status = status_to_update
            ticket.save()
        except Exception as e:
            logger.error(f"Unexpected error when updating ticket status: {e}")
            return Response({"status": False, "code": 500, "message": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Ticket {ticket.ticket_id} status updated to {status_to_update} by user {request.user}")
        return Response({"message": "Ticket status updated successfully."}, status=status.HTTP_200_OK)



import logging
from rest_framework.exceptions import ValidationError
from .models import Ticket, Comment
from .serializers import CommentSerializer

# Initialize logger
logger = logging.getLogger(__name__)

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [AgentAuthentication]

    def perform_create(self, serializer):
        """
        Ensure the comment is added to the correct ticket and by the correct user.
        """
        ticket_id = self.request.data.get('ticket')  # Use .get() to avoid KeyError

        if not ticket_id:
            logger.error("Ticket ID is missing in the request data.")
            raise ValidationError("Ticket ID is required.")

        try:
            # Fetch the ticket using the ticket_id
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            logger.error(f"Ticket with ID {ticket_id} not found.")
            raise ValidationError(f"Ticket with ID {ticket_id} does not exist.")
        
        if ticket.assigned_to != self.request.user:
            logger.warning(f"Agent {self.request.user.email} tried to comment on a ticket not assigned to them (Ticket ID: {ticket_id}).")
            raise ValidationError("You can only comment on tickets assigned to you.")

        try:
            # Save the comment and associate the logged-in agent as the user
            comment = serializer.save(user=self.request.user, ticket=ticket)
            logger.info(f"Comment created successfully by agent {self.request.user.email} on ticket {ticket_id}. Comment ID: {comment.id}")
        except Exception as e:
            # Log the exception details for further investigation
            logger.error(f"Error creating comment: {str(e)}")
            raise ValidationError("An unexpected error occurred. Please try again later.")

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Ticket, Comment
from .serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .utils import send_ticket_update_to_user  # Import the function from utils.py

# Initialize logger
logger = logging.getLogger(__name__)

class UpdateTicketView(APIView):
    """
    API endpoint to update ticket status and/or add a comment to a ticket.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [AgentAuthentication]

    def put(self, request):
        # Extract ticket_id from the request body
        ticket_id = request.data.get('ticket_id')

        if not ticket_id:
            logger.error("Ticket ID is missing in the request data.")
            return Response({"error": "Ticket ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the ticket using ticket_id and ensure it is assigned to the current user
            ticket = Ticket.objects.get(ticket_id=ticket_id, assigned_to=request.user)
        except Ticket.DoesNotExist:
            logger.warning(f"Ticket not found or not assigned to user: {request.user}")
            return Response({"error": "Ticket not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error when retrieving ticket: {e}")
            return Response({"status": False, "code": 500, "message": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Use a transaction to ensure both operations (status update and comment creation) are atomic
        try:
            with transaction.atomic():
                # Flags to check if any update occurred
                status_updated = False
                comment_added = False
                comment_text = None
                
                # Update status if provided
                status_to_update = request.data.get("status")
                if status_to_update:
                    ticket.status = status_to_update
                    ticket.save()  # Save ticket status
                    status_updated = True
                    logger.info(f"Ticket {ticket.ticket_id} status updated to {status_to_update} by user {request.user}")

                # Add comment if provided
                comment_text = request.data.get("comment_text")  # This should be 'comment_text' in the request body
                if comment_text:
                    comment_serializer = CommentSerializer(data=request.data)
                    if comment_serializer.is_valid():
                        comment = comment_serializer.save(user=request.user, ticket=ticket)
                        comment_added = True
                        logger.info(f"Comment added to ticket {ticket.ticket_id} by user {request.user}")
                    else:
                        # Log the errors if serializer is not valid
                        logger.error(f"Error creating comment: {comment_serializer.errors}")
                        return Response({"error": "Invalid comment data."}, status=status.HTTP_400_BAD_REQUEST)

                # Send an email only if either the status or a comment was updated
                if status_updated or comment_added:
                    send_ticket_update_to_user(
                        ticket.assigned_to.email,
                        ticket.ticket_id,
                        ticket.status if status_updated else None,
                        comment_text if comment_added else None
                    )

            return Response({"message": "Ticket status updated and/or comment added successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error during transaction: {e}")
            return Response({"error": "An unexpected error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.shortcuts import render

def login_page(request):
    return render(request, 'ticket/login.html') 

from django.shortcuts import render, redirect  # Add redirect here


def admin_dashboard(request):
    # Check if the user is authenticated and is a superuser
    # if not request.user.is_authenticated or not request.user.is_superuser:
    #     return redirect('login')  # Redirect to login if the user is not authenticated or a superuser

    return render(request, 'ticket/admin.html')


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Ticket, Agent, Comment
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Add permission classes

    def get(self, request):
        try:
            # Total number of tickets
            total_tickets = Ticket.objects.count()

            # Resolved tickets count
            resolved_tickets = Ticket.objects.filter(status='resolved').count()

            # Tickets count by priority
            priority_counts = {
                'low': Ticket.objects.filter(priority='low').count(),
                'medium': Ticket.objects.filter(priority='medium').count(),
                'high': Ticket.objects.filter(priority='high').count(),
                'critical': Ticket.objects.filter(priority='critical').count()
            }

            # Tickets count by status
            status_counts = {status: Ticket.objects.filter(status=status).count() for status, _ in Ticket.STATUS_CHOICES}

            # Total agents
            total_agents = Agent.objects.count()

            # Total number of comments across all tickets
            total_comments = Comment.objects.count()

            # Tickets assigned to each agent
            tickets_per_agent = {
                agent.email: Ticket.objects.filter(assigned_to=agent).count()
                for agent in Agent.objects.all()
            }

            # Total number of agents with tickets assigned
            total_agents_with_tickets = len([agent for agent in Agent.objects.all() if agent.assigned_tickets.exists()])

            # Return the response with detailed analytics
            return Response({
                'total_tickets': total_tickets,
                'resolved_tickets': resolved_tickets,
                'priority_counts': priority_counts,
                'status_counts': status_counts,
                'total_agents': total_agents,
                'total_comments': total_comments,
                'tickets_per_agent': tickets_per_agent,
                'total_agents_with_tickets': total_agents_with_tickets
            })

        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error fetching analytics: {e}")
            
            # Raise a validation error with a message
            raise ValidationError("There was an error while fetching the analytics.")



from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Agent
from .serializers import AgentSerializer

class AgentListView(generics.ListAPIView):
    queryset = Agent.objects.all()  # Fetch all agents from the database
    serializer_class = AgentSerializer  # Use the AgentSerializer to format the response
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated to access this view



from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import get_authorization_header
from .authentication import AgentAuthentication  # Custom authentication class
import logging

logger = logging.getLogger(__name__)

def agent_dashboard(request):
    """
    Render the agent dashboard template with authentication using AgentAuthentication.
    """


 

    return render(request, 'ticket/agent.html')
