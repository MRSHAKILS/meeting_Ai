from django.urls import path
<<<<<<< HEAD
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('join/', views.join_meeting, name='join_meeting'),
    path('meeting/<int:meeting_id>/', views.meeting_page, name='meeting_page'),
    path('delete_meeting/<int:meeting_id>/', views.delete_meeting, name='delete_meeting'),
]
=======
from .views import dashboard, create_meeting, join_meeting, meeting_page, delete_meeting, transcribe_meeting_view,summarize_transcript

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('create/', create_meeting, name='create_meeting'),
    path('join/', join_meeting, name='join_meeting'),
    path('meeting/<int:meeting_id>/', meeting_page, name='meeting_page'),
    path('delete_meeting/<int:meeting_id>/', delete_meeting, name='delete_meeting'),
    path('meeting/<int:meeting_id>/transcribe/', transcribe_meeting_view, name='transcribe_meeting'),
    path('summarize/<int:transcript_id>/', summarize_transcript, name='summarize_transcript'),

]
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
