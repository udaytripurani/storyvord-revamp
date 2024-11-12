# equipment/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import EquipmentCategory, EquipmentModel, EquipmentInstance, EquipmentLog
from .serializers import EquipmentCategorySerializer, EquipmentModelSerializer, EquipmentInstanceSerializer, EquipmentLogSerializer
from django.shortcuts import get_object_or_404
from storyvord.exception_handlers import custom_exception_handler

class EquipmentCategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            categories = EquipmentCategory.objects.all()
            serializer = EquipmentCategorySerializer(categories, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request):
        try:
             # Check if the data is a list
            if isinstance(request.data, list):
                serializer = EquipmentCategorySerializer(data=request.data, many=True)  # <-- Add this line
            else:
                serializer = EquipmentCategorySerializer(data=request.data)
            serializer.is_valid(exception=True)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EquipmentModelListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            models = EquipmentModel.objects.all()
            serializer = EquipmentModelSerializer(models, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request):
        try:
              # Check if the data is a list
            if isinstance(request.data, list):
                serializer = EquipmentModelSerializer(data=request.data, many=True)  # <-- Add this line
            else:
                serializer = EquipmentModelSerializer(data=request.data)
            serializer.is_valid(exception=True)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EquipmentInstanceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            instances = EquipmentInstance.objects.all()
            serializer = EquipmentInstanceSerializer(instances, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request):
        try:
             # Check if the data is a list
            if isinstance(request.data, list):
                serializer = EquipmentInstanceSerializer(data=request.data, many=True)  # <-- Add this line
            else:
                serializer = EquipmentInstanceSerializer(data=request.data)
            serializer.is_valid(exception=True)
            serializer.save()
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EquipmentInstanceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(EquipmentInstance, pk=pk)

    def get(self, request, pk):
        try:
            instance = self.get_object(pk)
            serializer = EquipmentInstanceSerializer(instance)
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
            instance = self.get_object(pk)
            serializer = EquipmentInstanceSerializer(instance, data=request.data)
            serializer.is_valid(exception=True)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def patch(self, request, pk):
        try:
            instance = self.get_object(pk)
            serializer = EquipmentInstanceSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(exception=True)
            serializer.save()
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk):
        try:
            instance = self.get_object(pk)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EquipmentLogListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logs = EquipmentLog.objects.all()
            serializer = EquipmentLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request):
        try:
             # Check if the data is a list
            if isinstance(request.data, list):
                serializer = EquipmentLogSerializer(data=request.data, many=True)  # <-- Add this line
            else:
                serializer = EquipmentLogSerializer(data=request.data)
            serializer.is_valid(exception=True)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EquipmentLogDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(EquipmentLog, pk=pk)

    def get(self, request, pk):
        try:
            log = self.get_object(pk)
            serializer = EquipmentLogSerializer(log)
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
            log = self.get_object(pk)
            serializer = EquipmentLogSerializer(log, data=request.data)
            serializer.is_valid(exception=True)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def patch(self, request, pk):
        try:
            log = self.get_object(pk)
            serializer = EquipmentLogSerializer(log, data=request.data, partial=True)
            serializer.is_valid(exception=True)
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
            log = self.get_object(pk)
            log.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            return Response(data ,status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
