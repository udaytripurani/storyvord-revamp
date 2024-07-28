

# # Create your views here.
# # callsheets/views.py
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from.models import CallSheet
# from.serializers import CallSheetSerializer
# from django.shortcuts import render
# from datetime import datetime  

# class CallSheetListView(APIView):
#     def get(self, request):
#         callsheets = CallSheet.objects.all()
#         serializer = CallSheetSerializer(callsheets, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#      serializer = CallSheetSerializer(data=request.data)
#      if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CallSheetDetailView(APIView):
#     def get_object(self, pk):
#         try:
#             return CallSheet.objects.get(pk=pk)
#         except CallSheet.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#     def get(self, request, pk):
#         callsheet = self.get_object(pk)
#         serializer = CallSheetSerializer(callsheet)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         callsheet = self.get_object(pk)
#         serializer = CallSheetSerializer(callsheet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         callsheet = self.get_object(pk)
#         callsheet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CallSheet
from .serializers import CallSheetSerializer
from project.models import Project
from storyvord_calendar.models import Calendar

class CallSheetCreateView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  # Copy the request data to modify it
        
        # Retrieve the project_id from request data
        project_id = data.get('project')
        
        # Fetch the Project instance using project_id
        project = get_object_or_404(Project, project_id=project_id)
        
        # Get calendar instance (if exists)
        try:
            calendar = Calendar.objects.get(project=project)
        except Calendar.DoesNotExist:
            calendar = None
        
        # Retrieve and fill additional information from project and calendar models
        data['project_name'] = project.name
        data['location'] = project.location_details.first().location if project.location_details.exists() else ''

        # Validate and save the CallSheet
        serializer = CallSheetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
