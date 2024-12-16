import json
import httpx
import os
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import ChatMessage, ChatSession, AiAgents # Add models for storing chat and context data
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async  # Import this for async DB operations
import uuid
from openai import OpenAI
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
User = get_user_model()

class AIChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract query string parameters (token and session_id)
        token = self.scope['query_string'].decode().split('&')
        session_id = None
        user_token = None
        agent = None

        for param in token:
            key, value = param.split('=')
            if key == "session_id":
                session_id = value
            if key == "token":
                user_token = value
            if key == "agent":
                agent = value
                
        if self.is_valid_session_id(session_id):
            self.session_id = session_id
        else:
            raise ValueError("Invalid session ID")
                
        # Validate and authenticate user
        try:
            access_token = AccessToken(user_token)
            user = await self.get_user(access_token['user_id'])
            self.scope['user'] = user
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.scope['user'] = AnonymousUser()
        
        # Check if the user is authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
        else:
            try:
                if session_id is None:
                    self.session_id = str(uuid.uuid4())

            # Check for existing session or create a new one
                await self.create_chat_session(self.scope['user'], self.session_id, agent)
            except ValueError as e:
                await self.close()  # Close the connection if there's a session conflict
                return

            await self.accept()  # Accept the connection if authenticated and session created successfully
     
    async def disconnect(self, close_code):
        try:
            logger.info(f"WebSocket disconnected with code: {close_code}")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")

    async def receive(self, text_data):
        try:
            if self.scope['user'].is_anonymous:
                await self.send(json.dumps({'error': 'Authentication required'}))
                return

            data = json.loads(text_data)
            user_message = data.get('message', '')
            
            if not self.session_id or not await self.is_valid_session_id(self.session_id):
                await self.send(json.dumps({'error': 'Invalid session ID'}))
                await self.close()
                return

            if not user_message:
                await self.send(text_data=json.dumps({
                    'error': 'Message is required'
                }))
                return
        
            user_message_embedding,embedding_cost = await self.generate_embedding(user_message)
            relevant_context = await self.get_relevant_messages(self.session_id, user_message_embedding)
            ai_response,input_tokens,output_tokens,response_cost = await self.get_ai_response(user_message, relevant_context)
            # Change the title of the chat if the context is changing
            current_title = await database_sync_to_async(ChatSession.objects.filter(session_id=self.session_id).values_list('title', flat=True).first)()
            suggested_title = await self.suggest_chat_title(user_message, relevant_context)
            if current_title != suggested_title and len(suggested_title) > len(current_title):
                await database_sync_to_async(ChatSession.objects.filter(session_id=self.session_id).update)(title=suggested_title)
                logger.info(f"Updated chat session title: {suggested_title}")
            total_cost = embedding_cost + response_cost
            logger.info(f"Tokens used - Input: {input_tokens}, Output: {output_tokens}, Total Cost: ${total_cost:.4f}")

            # Save the chat message
            await self.save_chat_message(self.session_id, user_message, ai_response, user_message_embedding)

            await self.send(text_data=json.dumps({
                'user_message': user_message,
                'ai_response': ai_response,
                'cost': total_cost
            }))
        
        except Exception as e:
            logger.error(f"Error during message processing: {e}")
            await self.send(json.dumps({'error': 'Internal server error'}))

    async def get_ai_response(self, user_message, context):
        try:
            agent= self.get_agent(self.session_id)
            agent = await agent
                        
            agent_context = agent.context

            messages = [
                        {"role": "system", "content": agent_context},
                        {"role": "system", "content": "Here is the previous context:"},
                    ]
            messages.extend(context)  # Add the previous context
            messages.append({"role": "user", "content": user_message})

            completion = client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=messages
            )
            
            if len(user_message)>=1000:
                title = ChatSession.objects.filter(session_id=self.session_id).get().title
                if title:
                    ChatSession.objects.filter(session_id=self.session_id).update(title=title + " - " + user_message[:100])
                else:
                    ChatSession.objects.filter(session_id=self.session_id).update(title=user_message[:100])

            ai_response = completion.choices[0].message
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            response_cost = (input_tokens * 0.00000015) + (output_tokens * 0.00000060)

            logger.info(f"AI response: {ai_response.content}")
            return ai_response.content, input_tokens, output_tokens, response_cost

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Error generating response", 0, 0, 0

    async def generate_embedding(self, text):
        try:
            # Call OpenAI's embeddings API to get the embedding for the text
            response = client.embeddings.create(input=text, model="text-embedding-3-small")

            cost_per_token = 0.00000002  # Replace with actual cost per token for embeddings
            tokens_used = response.usage.total_tokens
            cost = tokens_used * cost_per_token

            # Log the cost
            logger.info(f"Tokens used for embedding: {tokens_used}, Cost: ${cost:.4f}")

            # Extract the embedding based on the actual structure of the response
            if response.data and hasattr(response.data[0], 'embedding'):
                return response.data[0].embedding, cost
            else:
                raise ValueError("Invalid embedding response structure.")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None, 0

    @database_sync_to_async
    def get_relevant_messages(self, session_id, embedding):
        try:
            session = ChatSession.objects.get(session_id=session_id)
            
            session_id = str(session.session_id)

            messages = ChatMessage.objects.filter(session__session_id=session_id)

            # Calculate similarity scores between the new message embedding and the stored embeddings
            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            # Convert JSONField embedding to a list of floats
            messages_with_similarity = [
                (msg, cosine_similarity(embedding, json.loads(msg.embedding)))
                for msg in messages
            ]

            # Sort messages by similarity score
            relevant_messages = sorted(messages_with_similarity, key=lambda x: x[1], reverse=True)[:10]

            # Build context
            context = []
            for msg, _ in relevant_messages:
                context.append({"role": "user", "content": msg.user_message})
                context.append({"role": "assistant", "content": msg.ai_response})

            return context
        except Exception as e:
            logger.error(f"Error retrieving relevant messages: {e}")
            return []
       
    @database_sync_to_async 
    def get_agent(self, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id)
            return session.agent
        except Exception as e:
            logger.error(f"Error retrieving agent: {e}")
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        
    @database_sync_to_async
    def create_chat_session(self, user, session_id, agent_id):
        try:
            session_uuid = uuid.UUID(session_id)
            session, created = ChatSession.objects.get_or_create(
                session_id=session_uuid,
                defaults={'user': user}
            )
            if agent_id is None:
                agent = session.agent
            else:
                try:
                    agent = AiAgents.objects.get(id=agent_id)
                except AiAgents.DoesNotExist:
                    raise ValueError("Agent does not exist")
                
                # if agent != session.agent:
                #     print("Agent Mismatch")
                #     raise ValueError("Agent Mismatch")

            session.agent = agent
            session.save()

            if not created and session.user != user:
                raise ValueError("Session ID is already in use by a different user.")
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise

    @database_sync_to_async
    def save_chat_message(self, session_id, user_message, ai_response, embedding):
        try:
            session_uuid = uuid.UUID(session_id)
            session = ChatSession.objects.get(session_id=session_uuid)
            ChatMessage.objects.create(
                session=session, 
                user_message=user_message, 
                ai_response=ai_response,
                embedding=json.dumps(embedding),  # Store embedding as JSON
                user = self.scope['user']
            )
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            
    @database_sync_to_async
    def is_valid_session_id(self, session_id):
        try:
            session_uuid = uuid.UUID(session_id)
            ChatSession.objects.get(session_id=session_uuid)
            return True
        except ChatSession.DoesNotExist:
            return False
        
    @database_sync_to_async    
    def suggest_chat_title(self,user_message, context):
        try:
             # Aggregate recent messages for context building
            all_context = context + [{"role": "user", "content": user_message}]
            
            # Prepare messages for OpenAI API
            messages = [
                {"role": "system", "content": "You are an AI assistant tasked with suggesting concise, contextually relevant chat titles. Prioritize clarity and relevance to the conversation."},
                {"role": "assistant", "content": "Examples of good titles: 'Project Plan for AI Deployment', 'Bug Fixing Discussion', 'Team Onboarding'."},
                *all_context
            ]
            
            # Call OpenAI API to generate a suggestion
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=20,  # Restrict to concise title output
                temperature=0.7  # Adjust for balanced creativity
            )

            # Extract the suggested title from the response
            suggested_title = response.choices[0].message.content.strip()
            
            current_title = ChatSession.objects.filter(session_id=self.session_id).values_list('title', flat=True).first()
            
            # Check for semantic improvement
            if current_title and len(suggested_title) > len(current_title):
                return suggested_title
            elif not current_title:  # No existing title
                return suggested_title
            else:  # Current title is better
                return current_title
            
        except Exception as e:
            logger.error(f"Error suggesting chat title: {e}")
            return "Untitled Chat"
