from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from ..models import ProjectTask
from project.models import Membership
from django.db.models import Q
from ..serializers.serializers_v2 import ProjectTaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from storyvord.exception_handlers import custom_exception_handler
import logging

logger = logging.getLogger(__name__)

class ProjectTaskViewSet(viewsets.ModelViewSet):
    queryset = ProjectTask.objects.all()
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]  # Adjust permissions as needed
        
    # Override the initial method to add token validation
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if 'HTTP_AUTHORIZATION' not in request.META:
            logger.error("Authorization token missing")
            raise AuthenticationFailed("Authorization token is missing. Please provide a valid token.")
        
    # Create Task
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            task_instance = serializer.save()
            assigned_users = list(task_instance.assigned_to.all())
            data = {
                'status': status.HTTP_201_CREATED,
                'message': 'Task Created successfully',
                'data': {
                    'task_id': task_instance.id,
                    'title': task_instance.title,
                    'description': task_instance.description,
                    'assigned_to': [
                        {
                            'id': membership.user.id,
                            'email': membership.user.email,
                        } for membership in assigned_users
                    ],
                    'due_date': task_instance.due_date,
                    'status': task_instance.status,
                    'is_completed': task_instance.is_completed
                }
            }
            return Response(data)
        except Exception as exc:
            logger.error(f"Error creating task: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    # Update Task
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            print("Instance:", instance)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {
                'status': status.HTTP_201_CREATED,
                'message': 'Task Updated successfully',
                'data': {
                    'task_id': instance.id,
                    'title': instance.title,
                    'description': instance.description,
                    'assigned_to': [
                        {
                            'id': membership.user.id,
                            'email': membership.user.email,
                        } for membership in instance.assigned_to.all()
                    ],
                    'due_date': instance.due_date,
                    'status': instance.status,
                    'is_completed': instance.is_completed
                }
            }
            return Response(data)
        except Exception as exc:
            logger.error(f"Error updating task: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
    # List Tasks
    #TODO Project name in response
    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            tasks = self.queryset.filter(Q(assigned_to__user=user))
            data = {
                'status': status.HTTP_201_CREATED,
                'message': 'Task Fetched successfully',
                'data': {
                    'tasks': [
                        {
                            'id': task.id,
                            'project_id': task.project_id,
                            'title': task.title,
                            'description': task.description,
                            'assigned_to': [
                                {
                                    'membership_id': membership.id,
                                    'email': membership.user.email,
                                } for membership in task.assigned_to.all()
                            ],
                            'due_date': task.due_date,
                            'status': task.status,
                            'is_completed': task.is_completed
                        } for task in tasks
                    ]
                }
            }
            return Response(data)
        except Exception as exc:
            logger.error(f"Error getting tasks: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response  
        
    # Retrieve a single task
    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            tasks = self.queryset.filter(project=kwargs['pk'])
            if not tasks.exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
            data = {
                'status': status.HTTP_200_OK,
                'message': 'Tasks Fetched successfully',
                'data': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'assigned_to': [
                            {
                                'membership_id': membership.id,
                                'user_id': membership.user.id,
                                'role': membership.role.name,
                                'email': membership.user.email,
                            } for membership in task.assigned_to.all()
                        ],
                        'due_date': task.due_date,
                        'status': task.status,
                        'is_completed': task.is_completed
                    } for task in tasks
                ]
            }
            return Response(data)
            
        except Exception as exc:
            logger.error(f"Error retierving task: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        
    # Update a task
    # def put(self, request, *args, **kwargs):
    #     try:
    #         user = request.user
    #         print("User:", user)
    #         tasks = self.queryset.filter(assigned_to__user=user)
    #         if tasks.count() == 0:
    #             return Response(status=status.HTTP_404_NOT_FOUND)
            
    #         task_id = request.query_params.get('task_id')
    #         if not task_id:
    #             return Response({"error": "Task ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            
    #         task = tasks.get(pk=task_id)
    #         print("Task:", task)
    #         serializer = self.get_serializer(task, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             print("Serializer:", serializer.data)
    #         if serializer.is_valid():
    #             task_instance = serializer.save()
    #             print("Task Instance:", task_instance)
    #             assigned_users = list(task_instance.assigned_to.all())
    #             data = {
    #                 'status': status.HTTP_201_CREATED,
    #                 'message': 'Task Updated successfully',
    #                 'data': {
    #                     'task_id': task_instance.id,
    #                     'title': task_instance.title,
    #                     'description': task_instance.description,
    #                     'assigned_to': [
    #                         {
    #                             'id': membership.user.id,
    #                             'email': membership.user.email,
    #                         } for membership in assigned_users
    #                     ],
    #                     'due_date': task_instance.due_date,
    #                     'status': task_instance.status,
    #                     'is_completed': task_instance.is_completed
    #                 }
    #             }
    #             return Response(data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    #     except Exception as exc:
    #         logger.error(f"Error updating task: {exc}")
    #         response = custom_exception_handler(exc, self.get_renderer_context())
    #         return response
    
    # Delete a task
    def destroy(self, request, *args, **kwargs):
        print("Destroying task")
        print("pk:", kwargs['pk'])
        try:
            user = request.user
            print("User:", user)
            tasks = self.queryset.filter(assigned_to__user=user)
            print("Tasks:", tasks)
            if tasks.count() == 0:
                print("No tasks found")
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            task = tasks.get(pk=kwargs['pk'])
            print("Task:", task)
            print("Assigned by:", task.assigned_by)
            print("User:", user)
            if task.assigned_by.user != user:
                print("Not authorized to delete this task.")
                raise Exception("You are not authorized to delete this task.")
            task.delete()
            print("Task deleted")
            data = {
                'status': status.HTTP_200_OK,
                'message': 'Tasks Deleted successfully'
            }
            print("Returning response", data)
            return Response(data)
        except Exception as exc:
            print("Error:", exc)
            logger.error(f"Error getting all tasks: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
