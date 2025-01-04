from django.apps import AppConfig


class StoryvordCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'storyvord_calendar'

    def ready(self):
        import storyvord_calendar.signals