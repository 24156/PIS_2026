from django.urls import path

from . import views

app_name = 'communication'

urlpatterns = [
    path('annonces/', views.annonce_list, name='annonce_list'),
    path('annonces/create/', views.annonce_create, name='annonce_create'),
    path('annonces/<int:pk>/edit/', views.annonce_edit, name='annonce_edit'),
    path('annonces/<int:pk>/delete/', views.annonce_delete, name='annonce_delete'),
    path('notifications/send/', views.notification_send, name='notification_send'),
]
