from django.apps import AppConfig

<<<<<<< HEAD

class CreateMeetingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'create_meeting_app'
=======
class CreateMeetingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'create_meeting_app'

    def ready(self):
        # DO NOT start the scheduler here. Let the DB finish migrating first.
        pass
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
