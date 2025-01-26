from django.urls import path
from . import views

urlpatterns = [
    path('person/', views.view_person_info, name='sample_json_view'),

    ]