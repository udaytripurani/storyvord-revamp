# urls.py

from django.urls import path
from .views import (
    CheckEmailExistsView,
    SendConnectionRequestView,
    ManageConnectionRequestView,
    ViewConnectionsView,
    CheckConnectionRequestsView,
     SuggestedProfilesView,
    )

urlpatterns = [
    path('check-email/', CheckEmailExistsView.as_view(), name='check_email_exists'),
    path('connections/send/', SendConnectionRequestView.as_view(), name='send_connection_request'),
    path('connections/manage/', ManageConnectionRequestView.as_view(), name='manage_connection_request'),
    path('connections/', ViewConnectionsView.as_view(), name='view_connections'),
    path('connections/requests/', CheckConnectionRequestsView.as_view(), name='check_connection_requests'),  
    
    path('suggested-profiles/', SuggestedProfilesView.as_view(), name='suggested-profiles'),
    
]
