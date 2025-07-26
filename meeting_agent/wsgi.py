"""
WSGI config for meeting_agent project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
<<<<<<< HEAD
=======
import dotenv
dotenv.load_dotenv()
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_agent.settings')

application = get_wsgi_application()
