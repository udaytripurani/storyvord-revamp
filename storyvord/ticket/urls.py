# from django.urls import path
# from .views import TicketListCreateView, TicketDetailView, CommentCreateView

# urlpatterns = [
#     path('ticket/', TicketListCreateView.as_view(), name='ticket-list-create'),
#     path('ticket/<str:ticket_id>/', TicketDetailView.as_view(), name='ticket-detail'),  # Updated to use str for ticket_id
#     path('comments/', CommentCreateView.as_view(), name='comment-create'),
# ]

from django.urls import path
from .views import TicketListCreateView, TicketDetailView, CommentCreateView, AgentLoginView, AgentCreateView,AgentTicketListView,UpdateTicketStatusView,UpdateTicketView,login_page,admin_dashboard
from .views import AdminAnalyticsView,AgentListView,agent_dashboard

urlpatterns = [
    path('agent/login/', AgentLoginView.as_view(), name='agent-login'),
    path('agent/create/', AgentCreateView.as_view(), name='agent-create'),  # Only superuser can create agents
    path('ticket/', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('ticket/<str:ticket_id>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
     path('agent/tickets/', AgentTicketListView.as_view(), name='agent-ticket-update'),
     path('tickets/<str:ticket_id>/update-status/', UpdateTicketStatusView.as_view(), name='update-ticket-status'),
     path('tickets/update/', UpdateTicketView.as_view(), name='update-ticket'),
     
     
     path('tickets/admin/analytics/', AdminAnalyticsView.as_view(), name='admin_analytics'),

     #frontend rendering
     path('tickets/login/', login_page, name='login_page'),
     path('tickets/admin/', admin_dashboard, name='admin_dashboard'),
     path('agents/', AgentListView.as_view(), name='agent-list'),
     path('agent/dashboard/', agent_dashboard, name='agent_dashboard'),
     ]



