"""
ASGI config for meeting_agent project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
<<<<<<< HEAD
=======
import dotenv
dotenv.load_dotenv()
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_agent.settings')

application = get_asgi_application()
