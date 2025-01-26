from django.db import models
from django.db.models import JSONField
class Person(models.Model):
    name = models.CharField(max_length=50, default=None)
    birth_date = models.DateField()
    age = models.IntegerField(blank=True, null=True, default=None)
    address = models.CharField(max_length=50, default=None)
    def owned_cars(self):
        return [car.number for car in self.cars.all()]

class License(models.Model):
    number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    person = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True,)

class Car(models.Model):
    number = models.CharField(max_length=50, default=None)
    manufacturer = models.CharField(max_length=50, default=None)
    model = models.CharField(max_length=50, default=None)
    color = models.CharField(max_length=50, default=None)
    owner = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='cars')

class Junktion(models.Model):
    address = models.CharField(max_length=50, unique=True)
    cars = JSONField(default=dict)