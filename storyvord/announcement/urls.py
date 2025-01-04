# urls.py
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('announcements/', AnnouncementListCreateAPIView.as_view(), name='announcement-list-create'),
    path('announcements/<int:pk>/', AnnouncementRetrieveUpdateDestroyAPIView.as_view(), name='announcement-detail'),
    
    path('recipients/announcements/', RecipientAnnouncementListAPIView.as_view(), name='recipient-announcement-list'),
    path('recipients/announcements/<int:pk>/', RecipientAnnouncementDetailAPIView.as_view(), name='recipient-announcement-detail'),

    path('users/<str:project_id>/', ProjectUserListAPIView.as_view(), name='user-list-create'),
]

router.register(r'project-announcements', ProjectAnnouncementViewSet, basename='project-announcement')

urlpatterns += [
    path('v2/', include(router.urls))
    ]