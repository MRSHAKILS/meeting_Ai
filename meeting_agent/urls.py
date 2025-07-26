"""
URL configuration for meeting_agent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
<<<<<<< HEAD
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from landing_page.views import landing_page  # Import your view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('create_meeting_app.urls')),
    path('', landing_page, name='landing_page'),
]
=======
"""
from django.contrib import admin
from django.urls import path, include
from landing_page.views import landing_page  # Your landing page view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Allauth’s built-in routes
    path('accounts/', include('allauth.urls')),
    # Your custom login/signup app under /login/
    path('login/', include('login_signup_app.urls')),
    # Meetings dashboard (requires login)
    path('dashboard/', include('create_meeting_app.urls')),
    # Public landing page at root
    path('', include('landing_page.urls')), 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
