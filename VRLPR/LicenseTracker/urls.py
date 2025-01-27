from django.urls import path
from . import views

urlpatterns = [
    path('person/', views.view_person_info, name='sample_json_view'),
    path('car/', views.view_cars, name='sample_json_view'),
    ]