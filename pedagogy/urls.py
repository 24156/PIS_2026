from django.urls import path

from . import views

app_name = 'pedagogy'

urlpatterns = [
    path('cours/', views.cours_list, name='cours_list'),
    path('cours/create/', views.cours_create, name='cours_create'),
    path('cours/<int:pk>/edit/', views.cours_edit, name='cours_edit'),
    path('cours/<int:pk>/delete/', views.cours_delete, name='cours_delete'),
    path('cours/<int:pk>/download/', views.cours_download, name='cours_download'),
    path('td/', views.td_list, name='td_list'),
    path('td/create/', views.td_create, name='td_create'),
    path('td/<int:pk>/delete/', views.td_delete, name='td_delete'),
    path('td/<int:pk>/rendus/', views.rendu_list_td, name='rendu_list_td'),
    path('td/<int:pk>/rendre/', views.rendu_deposer_td, name='rendu_deposer_td'),
    path('tp/', views.tp_list, name='tp_list'),
    path('tp/create/', views.tp_create, name='tp_create'),
    path('tp/<int:pk>/delete/', views.tp_delete, name='tp_delete'),
    path('tp/<int:pk>/rendus/', views.rendu_list_tp, name='rendu_list_tp'),
    path('tp/<int:pk>/rendre/', views.rendu_deposer_tp, name='rendu_deposer_tp'),
    path('tp-td/', views.tp_td_list, name='tp_td_list'),
    path('rendus/<int:pk>/download/', views.rendu_download, name='rendu_download'),
    path('rendus/<int:pk>/corriger/', views.rendu_corriger, name='rendu_corriger'),
]
