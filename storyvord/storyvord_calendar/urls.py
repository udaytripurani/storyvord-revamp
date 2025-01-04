from django.urls import path
from .views import *

urlpatterns = [
    path('calendars/', CalendarView.as_view(), name='calendar-list'),
    path('calendars/<str:project_id>/', CalendarView.as_view(), name='calendar-detail'),
    path('calendars/<str:project_id>/events/', EventView.as_view(), name='event-list-create'),
    path('calendars/<str:project_id>/events/<int:pk>/', EventView.as_view(), name='event-detail'),

    
    # user calendar
    path('user/calendar/home/', UserHomeCalendarView.as_view(), name='user-home-calendar'),

    # user calendar events
    path('user/calendar/', UserCalendarView.as_view(), name='user-calendar-list'),
    path('user/calendar/events/', UserCalendarEventView.as_view(), name='user-calendar-event-list-create'),
    path('user/calendar/events/<int:pk>/', UserCalendarEventView.as_view(), name='user-calendar-event-detail'),
]
