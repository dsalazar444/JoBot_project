from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview, name='interview'),
    path('<int:session_id>/', views.interview, name='interview_session'),
    path('api/send-message/<int:session_id>/', views.send_message, name='send_message'),
    path('api/create-session/', views.create_session, name='create_session'),
    path('api/session-summary/<int:session_id>/', views.session_summary, name='session_summary'),
]
