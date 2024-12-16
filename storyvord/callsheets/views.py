from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import *
from .serializers import *
import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from storyvord.exception_handlers import custom_exception_handler
from project.models import Membership, ProjectDetails   
from rest_framework import serializers

class CallSheetListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CallSheetSerializer
    
    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not (membership.role.permission.filter(name=permission_name).exists()):
            return False
        return True


    def get(self, request, project_id):
        try:
            callsheets = CallSheet.objects.filter(project=project_id)
            serializer = CallSheetSerializer(callsheets, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, project_id):
        try:
            project = get_object_or_404(ProjectDetails, pk=project_id)

            # if not self.check_rbac(request.user, project, 'create_callsheet'):
                # raise PermissionError('You do not have permission to create callsheet for this project')
            
            data = request.data.copy()
            data['project'] = project.project_id

            serializer = CallSheetSerializer(data=data)


            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class CallSheetDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CallSheetSerializer


    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not (membership.role.permission.filter(name=permission_name).exists()):
            return False
        return True


    def get(self, request, pk):
        try:
            call_sheet = get_object_or_404(CallSheet, pk=pk)
            
            if not Membership.objects.filter(user=request.user, project=call_sheet.project).exists():
                raise PermissionError('You do not have permission to view callsheet for this project')
            
            serializer = CallSheetSerializer(call_sheet)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk):
        try:
            call_sheet = get_object_or_404(CallSheet, pk=pk)

            
            if not self.check_rbac(request.user, call_sheet.project, 'edit_callsheet'):
                raise PermissionError('You do not have permission to edit callsheet for this project')
            
            
            serializer = CallSheetSerializer(call_sheet, data=request.data, partial=True)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        

    def delete(self, request, pk):
        try:
            call_sheet = get_object_or_404(CallSheet, pk=pk)

            if not self.check_rbac(request.user, call_sheet.project, 'delete_callsheet'):
                raise PermissionError('You do not have permission to delete callsheet for this project')
            
            call_sheet.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response


        
# https://www.geoapify.com/tutorial/geocoding-python/
class GeoapifyGeocodeView(APIView):

    def get(self, request):
        try:
            api_key = getattr(settings, 'GEOAPIFY_API_KEY')
            address = request.GET.get('text')

            url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
            headers = {"Accept": "application/json"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = {
                'message': 'Success',
                'data': response.json()
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response 

class GeoapifyNearestPlaceView(APIView):

    def get(self, request):
        try:
            api_key = getattr(settings, 'GEOAPIFY_API_KEY')
            latitude = request.GET.get('lat')
            longitude = request.GET.get('lon')

            url = f"https://api.geoapify.com/v1/places?categories=city&filter=circle:{longitude},{latitude},1000&limit=1&apiKey={api_key}"
            headers = {"Accept": "application/json"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = {
                'message': 'Success',
                'data': response.json()
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

            
# https://www.weatherapi.com/docs/
class WeatherCurrentInfoView(APIView):

    def get(self, request):
        try:
            latitude = request.GET.get('lat')
            longitude = request.GET.get('lon')
        
            if not latitude or not longitude:
                return Response({'error': 'Latitude and Longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
            api_key = getattr(settings, 'WEATHERAPI_API_KEY')
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={latitude},{longitude}"
            headers = {"Accept": "application/json"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = {
                'message': 'Success',
                'data': response.json()
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class WeatherFutureInfoView(APIView):

    def get(self, request):
        try:
            latitude = request.GET.get('lat')
            longitude = request.GET.get('lon')
            dt = request.GET.get('dt')
        
            if not latitude or not longitude:
                return Response({'status': False,
                                 'error': 'Latitude and Longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
            api_key = getattr(settings, 'WEATHERAPI_API_KEY')
            url = f"http://api.weatherapi.com/v1/future.json?key={api_key}&q={latitude},{longitude}&dt={dt}"
            headers = {"Accept": "application/json"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = {
                'message': 'Success',
                'data': response.json()
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response