from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import requests
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Script, Scene, Shot, Sequence, Storyboard
from .serializers import (
    ScriptSerializer, SceneSerializer, ShotSerializer,
    SequenceSerializer, StoryboardSerializer
)
from .ai_utils import AIService  # Custom module for AI integration
from .utils import handle_file_upload

import logging

logger = logging.getLogger(__name__)

#Get all scripts
#TODO Add Role permissions
class ScriptListView(APIView):
    def get(self, request):
        project_id = request.query_params.get("project_id")
        scripts = Script.objects.filter(project=project_id)
        serializer = ScriptSerializer(scripts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Get a specific script
class ScriptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        script = get_object_or_404(Script, id=id)

        # Check if the user is authorized to access the script
        if script.user != request.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ScriptSerializer(script)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Upload a new script
class ScriptUploadView(APIView):
    def post(self, request):
        content = request.data.get('content')
        file = request.FILES.get('file')

        if not content and not file:
            logger.info("No content or file provided")
            return Response({"error": "Either content or file must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        script_data = {
            'user': request.user.id,
            'project': request.data.get('project'),
            'title': request.data.get('title'),
            'content': content
        }

        serializer = ScriptSerializer(data=script_data)
        if serializer.is_valid():
            script = serializer.save()

            if file:
                try:
                    script.file = file
                    script.save()
                except Exception as e:
                    logger.error(f"File upload failed: {e}")
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(f"Script created: {script}")
            return Response(ScriptSerializer(script).data, status=status.HTTP_201_CREATED)

        logger.warning(f"Invalid data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update a script
class ScriptUpdateView(APIView):
    def put(self, request, id):
        script = get_object_or_404(Script, id=id)
        serializer = ScriptSerializer(script, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
# Delete a script  
class ScriptDeleteView(APIView):
    def delete(self, request, id):
        logger.info(f"User {request.user.id} is deleting script {id}")
        script = get_object_or_404(Script, id=id)
        if script.user != request.user or script.project.owner != request.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)
        
        script.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

#TODO Need to complete this
class ScriptSuggestionView(APIView):
    def post(self, request, id):
        print("Received POST request for script suggestions")
        print(f"Request data: {request.data}")
        script = get_object_or_404(Script, id=id)
        print(f"Script: {script}")
        content = script.content
        if content is None:
            print("No content found in database, reading from file")
            content = script.file.read().decode('utf-8')
        print(f"Content: {content}")
        try:
            ai_service = AIService()
            suggestions = ai_service.get_script_suggestions(content)
            print(f"Suggestions: {suggestions}")
            return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)
        except TypeError as e:
            logger.error(f"Failed to fetch script suggestions: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to fetch script suggestions: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScriptSuggestionActionView(APIView):
    def put(self, request, id, suggestion_id, action):
        script = get_object_or_404(Script, id=id)
        # Use `action` to either accept or reject the suggestion
        if action == "accept":
            result = AIService.accept_suggestion(script, suggestion_id)
        elif action == "reject":
            result = AIService.reject_suggestion(script, suggestion_id)
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
    
class CreateSceneView(APIView):
    def post(self, request, id):
        try:
            print("Received POST request for creating scene")
            data = request.data
            script = get_object_or_404(Script, id=id)
            print(f"Script: {script}")
            serializer = SceneSerializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save(script=script)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to create scenes: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateScenesView(APIView):
    def post(self, request, id):
        script = get_object_or_404(Script, id=id)
        scenes = AIService.generate_scenes(script.content)
        serializer = SceneSerializer(data=scenes, many=True)
        if serializer.is_valid():
            serializer.save(script=script)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditSceneView(APIView):
    def put(self, request, scene_id):
        scene = get_object_or_404(Scene, id=scene_id)
        serializer = SceneSerializer(scene, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteSceneView(APIView):
    def delete(self, request, scene_id):
        scene = get_object_or_404(Scene, id=scene_id)
        scene.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RegenerateSceneView(APIView):
    def post(self, request, scene_id):
        scene = get_object_or_404(Scene, id=scene_id)
        regenerated_scene = AIService.regenerate_scene(scene)
        return Response({"scene": regenerated_scene}, status=status.HTTP_200_OK)

class GenerateShotsView(APIView):
    def post(self, request, scene_id):
        scene = get_object_or_404(Scene, id=scene_id)
        shots = AIService.generate_shots(scene.description)
        serializer = ShotSerializer(data=shots, many=True)
        if serializer.is_valid():
            serializer.save(scene=scene)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkShotDoneView(APIView):
    def put(self, request, shot_id):
        shot = get_object_or_404(Shot, id=shot_id)
        shot.done = True
        shot.save()
        return Response({"message": "Shot marked as done"}, status=status.HTTP_200_OK)

class UpdateTimelineView(APIView):
    def put(self, request, scene_id):
        scene = get_object_or_404(Scene, id=scene_id)
        timeline = request.data.get("timeline", {})
        scene.timeline = timeline
        scene.save()
        return Response({"message": "Timeline updated"}, status=status.HTTP_200_OK)

class CreateSequenceView(APIView):
    def post(self, request):
        serializer = SequenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GenerateStoryboardView(APIView):
    def post(self, request):
        scenes = request.data.get("scenes", [])
        storyboards = AIService.generate_storyboards(scenes)
        serializer = StoryboardSerializer(data=storyboards, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditStoryboardView(APIView):
    def put(self, request, id):
        storyboard = get_object_or_404(Storyboard, id=id)
        serializer = StoryboardSerializer(storyboard, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

