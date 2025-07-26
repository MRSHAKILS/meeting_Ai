from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
<<<<<<< HEAD
=======
    path('pricing/', views.pricing_page, name='pricing_page'),

>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
]