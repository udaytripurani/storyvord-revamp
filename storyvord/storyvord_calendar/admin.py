from django.contrib import admin
from .models import *

# admin.site.register(Calendar)
# admin.site.register(Event)


admin.site.register(ProjectCalendar)
admin.site.register(CalendarEvent)

admin.site.register(UserCalender)
admin.site.register(UserCalendarEvent)