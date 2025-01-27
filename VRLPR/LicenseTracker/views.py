from django.shortcuts import render
from .models import Person, License, Car, Junktion
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Prefetch, Avg, Count

def view_person_info(request):
    id = request.GET.get('id')
    person = Person.objects.filter(id=id)[0]
    if not person: 
        return JsonResponse("Failed to find person", safe=False)
    data = f"Name = {person.name}, birth date = {person.birth_date}, license = {person.license.number}, cars = {person.owned_cars()}"

    return JsonResponse(data, safe=False)
def view_cars(request):
    id = request.GET.get('id')
    junction = Junktion.objects.filter(id=id)[0]
    data = f'Status: {junction.how_busy()}; Cars: {junction.get_cars()}'
    return JsonResponse(data, safe=False)