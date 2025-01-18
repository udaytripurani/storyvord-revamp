# your_project/ticket/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import Agent

class AgentAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed("No token provided")

        try:
            # Extract token
            token = token.split(' ')[1]  # Extract token from "Bearer <token>"
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Find the agent by ID in the payload
            agent = Agent.objects.get(id=payload['id'])

            return (agent, token)  # Return the agent instance and the token
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Agent.DoesNotExist:
            raise AuthenticationFailed("Agent not found")
