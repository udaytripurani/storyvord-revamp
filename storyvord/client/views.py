# client/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from storyvord.exception_handlers import custom_exception_handler


from crew.models import CrewProfile
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated  # Ensure this import is present
from rest_framework.parsers import MultiPartParser

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]  # Apply IsAuthenticated permission globally

#     def get(self, request):
#         # Fetch the profile of the logged-in user
#         profile = get_object_or_404(Profile, user=request.user)  # Modified to fetch profile by user
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data)

#     def post(self, request):
#         # Ensure the logged-in user doesn't already have a profile
#         if Profile.objects.filter(user=request.user).exists():
#             return Response({"detail": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

#         # Create a new profile for the logged-in user
#         serializer = ProfileSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated  # Ensure this import is present
from accounts.models import User  # Adjust the import path as per your User model location

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]  # Apply IsAuthenticated permission globally

#     def put(self, request):
#         # Ensure the logged-in user has an associated account
#         try:
#             user = User.objects.get(id=request.user.id)  # Change: Ensure user exists
#         except User.DoesNotExist:
#             return Response({"detail": "User account does not exist."}, status=status.HTTP_404_NOT_FOUND)  # Comment: Handle if user not found

#         # Ensure the logged-in user doesn't already have a profile
#         if ClientProfile.objects.filter(user=request.user).exists():  # Change: Check if profile exists for user
#             return Response({"detail": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)  # Comment: Handle if profile already exists

#         # Create a new profile for the logged-in user
#         serializer = ProfileSerializer(data=request.data)
#         if serializer.is_valid():
#             # serializer.save(user=request.user)
#             serializer.save(user=request.user, user_type=request.user.user_type)  # Change: Ensure user_type is saved

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Comment: Handle serializer errors


class OnboardAPIView(APIView):
    permissions_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        profile = get_object_or_404(ClientProfile, user=self.request.user)
        return profile

    def put(self, request):
        try:
            user = request.user

            if str(user.user_type) != 'client':
                raise PermissionError('Only clients can onboard')
        
            if user.steps:
                raise PermissionError('User has already onboarded')

            profile = self.get_object()
            serializer = ProfileSerializer(profile, data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
                
            serializer.save()

            user.steps = True
            user.user_stage = 2
            user.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class ProfileDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        profile = get_object_or_404(ClientProfile, user=self.request.user)
        return profile

    def get(self, request):
        try:
            profile = self.get_object()
            serializer = ProfileSerializer(profile)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request):
        try:
            profile = self.get_object()
            serializer = ProfileSerializer(profile, data=request.data)
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

class ClientCompanyProfileAPIView(APIView):
    permissions_classes = [IsAuthenticated]
    serializer_class = ClientCompanyProfileSerializer

    def get(self, request):
        try:
            pk = request.query_params.get('pk', None)
            if pk:
                profile = get_object_or_404(ClientCompanyProfile, pk=pk)
            else:
                profile = get_object_or_404(ClientCompanyProfile, user=request.user)

            if not profile.has_permission(request.user, 'edit'):
                raise PermissionError('You do not have permission to view this profile')
        
            
            serializer = ClientCompanyProfileSerializer(profile)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk=None):
        try:
            if pk:
                profile = get_object_or_404(ClientCompanyProfile, pk=pk)
            else:
                profile = ClientCompanyProfile.objects.get(user=request.user)

            serializer = ClientCompanyProfileSerializer(profile, data=request.data)
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

# List all employees in a company
class EmployeeListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MembershipSerializer

    def get(self, request, pk):
        try:
            # pk = request.query_params.get('pk', None)
            # if not pk:
                # raise serializers.ValidationError('Company ID is required as a query parameter "pk"')

            company = get_object_or_404(ClientCompanyProfile, pk=pk)
            memberships = Membership.objects.filter(company=company)
            serializer = MembershipSerializer(memberships, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response



class SwitchProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            data = request.data
            switch_to_client = data.get('switch_to_client', False)
            switch_to_crew = data.get('switch_to_crew', False)

            if not (switch_to_client or switch_to_crew):
                return Response({'status': False,
                                 'code': status.HTTP_400_BAD_REQUEST,
                                 'message': 'Specify a role to switch to.'}, status=status.HTTP_400_BAD_REQUEST)

            if switch_to_client:
                # Activate Client profile and deactivate Crew profile
                client_profile, created = ClientProfile.objects.get_or_create(user=user)
                client_profile.active = True
                client_profile.save()

                CrewProfile.objects.filter(user=user).update(active=False)

                user.is_client = True
                user.is_crew = False
                user.save()

            if switch_to_crew:
                # Activate Crew profile and deactivate Client profile
                crew_profile, created = CrewProfile.objects.get_or_create(user=user)
                crew_profile.active = True
                crew_profile.save()

                ClientProfile.objects.filter(user=user).update(active=False)

                user.is_client = False
                user.is_crew = True
                user.save()

            return Response({'message': 'Success',
                             'detail': 'Profile updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response



class ClientCompanyFolderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientCompanyFolderSerializer

    def get(self, request, company_id):
        try:
            user = request.user
            company = get_object_or_404(ClientCompanyProfile, pk=company_id)

            if company.has_permission(user, 'view_folder'):
                folders = ClientCompanyFolder.objects.filter(company=company)
            else:
                folders = ClientCompanyFolder.objects.filter(company=company, allowed_users=user)
            
            serializer = ClientCompanyFolderSerializer(folders, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, company_id):
        try:
            company = get_object_or_404(ClientCompanyProfile, pk=company_id)
            if not company.has_permission(request.user, 'create_folder'):
                raise PermissionError('You do not have permission to create folders for this company')

            data = request.data.copy()
            data['company'] = company_id

            for user in data.get('allowed_users', []):
                print(user)
                if not company.memberships.filter(user=user).exists(): 
                    raise PermissionError(f'User {user} does not have permission to view folders for this company')
            
            serializer = ClientCompanyFolderSerializer(data=data, context={'request': request})

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            serializer.save(created_by=request.user)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    # Delete folders?

class ClientCompanyFileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientCompanyFileSerializer

    def get(self, request, folder_id, format=None):
        try:
            folder = get_object_or_404(ClientCompanyFolder, pk=folder_id)

            if not folder.company.has_permission(request.user, 'view_folder') or not folder.allowed_users.filter(pk=request.user.pk).exists():
                raise PermissionError('You do not have permission to view this folder')
            
            files = folder.files.all()
            serializer = ClientCompanyFileSerializer(files, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, folder_id, format=None):
        try:
            folder = get_object_or_404(ClientCompanyFolder, pk=folder_id)

            if not folder.company.has_permission(request.user, 'create_folder'):
                raise PermissionError('You do not have permission to create files to this folder')
            
            req_data = request.data.copy()
            req_data['folder'] = folder.id
            serializer = ClientCompanyFileSerializer(data=req_data)

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
    # Delete files?

class ClientCompanyFileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientCompanyFileUpdateSerializer

    def get_object(self, pk):
        try:
            return ClientCompanyFile.objects.get(pk=pk)
        except ClientCompanyFile.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        try:
            file = self.get_object(pk)

            if not file:
                raise serializers.ValidationError('File not found.')

            if not file.folder.company.has_permission(request.user, 'view_folder') or not file.folder.allowed_users.filter(pk=request.user.pk).exists():
                raise PermissionError('You do not have permission to view this folder')

            serializer = ClientCompanyFileUpdateSerializer(file, context={'request': request})
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk, format=None):
        try:
            file = self.get_object(pk)

            if file is None:
                raise serializers.ValidationError('File not found.')


            if not file.folder.company.has_permission(request.user, 'edit_folder'):
                raise PermissionError('You do not have permission to edit files to this folder')

            serializer = ClientCompanyFileUpdateSerializer(file, data=request.data, context={'request': request})

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
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
            file = self.get_object(pk)
            if file is None:
                raise serializers.ValidationError('File not found.')

            if not file.folder.company.has_permission(request.user, 'delete_folder'):
                raise PermissionError('You do not have permission to delete files to this folder')


            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    
class ClientCompanyFolderUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return ClientCompanyFolder.objects.get(pk=pk)
        except ClientCompanyFolder.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        try:
            print("Get folder")
            folder = self.get_object(pk)

            if folder is None:
                raise serializers.ValidationError('Folder not found.')

            if not folder.company.has_permission(request.user, 'view_folder') or not folder.allowed_users.filter(pk=request.user.pk).exists():
                raise PermissionError('You do not have permission to view this folder')

            serializer = ClientCompanyFolderUpdateSerializer(folder)

            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk, format=None):
        try:
            folder = self.get_object(pk)

            if folder is None:
                raise serializers.ValidationError('Folder not found.')
            
            if not folder.company.has_permission(request.user, 'edit_folder'):
                raise PermissionError('You do not have permission to edit this folder')

            serializer = ClientCompanyFolderUpdateSerializer(folder, data=request.data, context={'request': request})

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            self.check_object_permissions(request, folder)
            serializer.save()

            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def patch(self, request, pk, format=None):
        try:
            folder = self.get_object(pk)

            if folder is None:
                raise serializers.ValidationError('Folder not found.')

            if not folder.company.has_permission(request.user, 'edit_folder'):
                raise PermissionError('You do not have permission to edit this folder')

            serializer = ClientCompanyFolderUpdateSerializer(folder, data=request.data, partial=True, context={'request': request})

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

    def delete(self, request, pk, format=None):
        try:
            folder = self.get_object(pk)

            if folder is None:
                raise serializers.ValidationError('Folder not found.')

            if not folder.company.has_permission(request.user, 'delete_folder'):
                raise PermissionError('You do not have permission to delete this folder')

            folder.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

# Calendar


class ClientCompanyEventAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientCompanyEventSerializer

    def get(self, request, event_id=None):
        try:
            if (event_id):
                event = ClientCompanyEvent.objects.get(id=event_id, calendar__company__user=request.user)
                serializer = ClientCompanyEventSerializer(event)

                data = {
                    'message': 'Success',
                    'data': serializer.data
                }
                return Response(data)
        
            company_profile = ClientCompanyProfile.objects.get(user=request.user)
            print("Company prodile", company_profile)
            events = ClientCompanyEvent.objects.filter(calendar__company=company_profile)
            serializer = ClientCompanyEventSerializer(events, many=True)

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
            serializer = ClientCompanyEventSerializer(data=request.data, context={'request': request})
            serializer.is_valid(exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, event_id):
        try:
            event = ClientCompanyEvent.objects.get(id=event_id, calendar__company__user=request.user)

            serializer = ClientCompanyEventSerializer(event, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(exception=True)
            serializer.save()

            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, event_id):
        try:
            event = ClientCompanyEvent.objects.get(id=event_id, calendar__company__user=request.user)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

            

class CompanyListView(APIView):

    def get(self, request, format=None):
        try:
            # Get the ClientProfile associated with the current user
            client_profile = ClientProfile.objects.filter(employee_profile=request.user)

            # Get all the companies where the user is listed in the employee profile
            companies = ClientCompanyProfile.objects.filter(user__in=client_profile.values_list('user', flat=True))

            serializer = ClientCompanyProfileSerializer(companies, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response