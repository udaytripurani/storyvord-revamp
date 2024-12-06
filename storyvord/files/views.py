from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from project.serializers.serializers_v1 import UserSerializer
from project.serializers.serializers_v2 import MembershipSerializer
from .models import File, Folder
from accounts.models import User
from project.models import Project
from django.shortcuts import get_object_or_404
from django.db.models import Q
from storyvord.exception_handlers import custom_exception_handler

# Create your views here.

class FolderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FolderSerializer
    # parser_classes = (MultiPartParser, FormParser)

    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)

        if not membership.role.permission.filter(name=permission_name).exists():
            return False
        return True

    def get(self, request, pk, format=None):
        try:
            user = request.user

            # Check if the user is a member of the project
            folders = Folder.objects.filter(Q(project=pk) & (Q(allowed_users__user=user) | Q(default=True))).distinct()

            # Check if the user has permission to view folders
            if self.check_rbac(user, pk, 'view_folders'):
                folders = Folder.objects.filter(project=pk)
            
            serializer = FolderSerializer(folders, many=True, context={'exclude_files': True})
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, pk, format=None):
        try:
            data = request.data.copy()
            data['project'] = pk

            # Check if the user has permission to create a folder
            if not self.check_rbac(request.user, pk, 'create_folder'):
                raise PermissionError('You do not have permission to create a folder in this project.')


            serializer = FolderSerializer(data=data, context={'request': request})
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

class FolderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FolderUpdateSerializer

    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not membership.role.permission.filter(name=permission_name).exists():
            return False
        return True
    
    def put(self, request, pk, format=None):
        try:
            folder = get_object_or_404(Folder, pk=pk)
            project = folder.project
            
            # Check if the user has permission to edit a folder
            if not self.check_rbac(request.user, project, 'edit_folder'):
                raise PermissionError('You do not have permission to edit this folder.')
            
            serializer = self.serializer_class(folder, data=request.data, context={'request': request}, partial=True)
        
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk, format=None):
        try:
            folder = get_object_or_404(Folder, pk=pk)

            # Check if the user has permission to delete a folder
            if not self.check_rbac(request.user, folder.project, 'delete_folder'):
                raise PermissionError('You do not have permission to delete this folder.')

            folder.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response


class FileListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileSerializer

    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not membership.role.permission.filter(name=permission_name).exists():
            return False
        return True

    # Get the list of files in a folder
    def get(self, request, pk, format=None):
        try:
            folder = get_object_or_404(Folder, pk=pk)

            # Check if the user is in allowed_users or has permission to view the folder
            if not folder.default:
                if not folder.allowed_users.filter(user=request.user).exists():
                    raise PermissionError('You do not have permission to view the files in this folder.')

            files = folder.files

            serializer = FileSerializer(files, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, pk, format=None):
        try:
            user = request.user

            folder = get_object_or_404(Folder, pk=pk)
        
            # Check if the user has permission to create a file in the folder
            if not self.check_rbac(user, folder.project, 'create_folder'):
                raise PermissionError('You do not have permission to create a file in this folder.')


            # Check if the file with same name exists
            if File.objects.filter(folder=pk, name=request.data.get('name')).exists():
                # return Response({"detail": "File with the same name already exists."}, status=status.HTTP_400_BAD_REQUEST)
                raise Warning('File with the same name already exists.')

            # Make a mutable copy of request.data
            data = request.data.copy()
            data['folder'] = pk

            serializer = FileSerializer(data=data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class FileDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileSerializer

    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not (membership.role.permission.filter(name=permission_name).exists()):
            return False
        return True

    # Get the details of a file
    def get(self, request, pk, format=None):
        try:
            file = get_object_or_404(File, pk=pk)

            # Check if the user has view_folder permission
            if not file.folder.default:
                if not file.folder.allowed_users.filter(user=request.user).exists():
                    raise PermissionError('You do not have permission to view this file.')

            serializer = FileSerializer(file)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
    def delete(self, request, pk, format=None):
        try:
            file = get_object_or_404(File, pk=pk)

            # Check if the user has permission to delete a file
            if not self.check_rbac(request.user, file.folder.project, 'delete_folder'):
                raise PermissionError('You do not have permission to delete this file.')

            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response


    def put(self, request, pk, format=None):
        try:
            file = get_object_or_404(File, pk=pk)

            # Check if the user has permission to edit a file
            if not self.check_rbac(request.user, file.folder.project, 'edit_folder'):
                raise PermissionError('You do not have permission to edit this file.')


            # Ensure the folder id doesnot change
            if 'folder' in request.data:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'status': False,
                                                                        'code': status.HTTP_403_FORBIDDEN,
                                                                        'message': 'You cannot change the folder of a file.'})

            serializer = FileSerializer(file, data=request.data, partial=True)
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

# class FolderCrewListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def check_rbac(self, user, project, permission_name):
#         membership = get_object_or_404(Membership, user=user, project=project)
#         if not (membership.role.permission.filter(name=permission_name).exists()):
#             return False
#         return True

#     def get(self, request, pk):
#         try:
#             folder = get_object_or_404(Folder, pk=pk)

#             # Check if the user has view_folder permission
#             if not self.check_rbac(request.user, folder.project, 'view_folders'):
#                 raise PermissionError('You do not have permission to view this folder')

#             crew = folder.project.members.all()
#             serializer = MembershipSerializer(crew, many=True)
#             data = {
#                 'message': 'Success',
#                 'data': serializer.data
#             }
            
#             return Response(data, status=status.HTTP_200_OK)
#         except Exception as exc:
#             print(exc)
#             response = custom_exception_handler(exc, self.get_renderer_context())
#             return response
