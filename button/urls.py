from django.urls import path
from . import views

app_name = 'button'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/session/', views.create_session, name='create_session'),
    path('api/click/', views.record_click, name='record_click'),
    path('api/stats/', views.get_stats, name='get_stats'),
]
