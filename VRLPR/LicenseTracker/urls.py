from django.urls import path
from . import views
urlpatterns = [
    path('person/', views.view_person_info, name='sample_json_view'),
    path('car/', views.view_cars, name='sample_json_view'),
    path('create_person/', views.create_person, name='person_create'),
    path('update_person/', views.update_person, name='person_update'),
    path('delete_person/', views.delete_person, name='person_delete'),
    path('create_car/', views.create_car, name='person_create'),
    path('update_car/', views.update_car, name='person_update'),
    path('delete_car/', views.delete_car, name='person_delete'),
    path('create_license/', views.create_license, name='person_create'),
    path('update_license/', views.update_license, name='person_update'),
    path('delete_license/', views.delete_license, name='person_delete'),
    path('create_junktion/', views.create_junktion, name='person_create'),
    path('update_junktion/', views.update_junktion, name='person_update'),
    path('delete_junktion/', views.delete_junktion, name='person_delete'),
    ]
