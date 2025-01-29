from django.db import models
class Person(models.Model):
    name = models.CharField(max_length=50, default=None)
    birth_date = models.DateField(null=True, blank=True)
    # age = models.IntegerField(blank=True, null=True, default=None)
    address = models.CharField(max_length=50, null=True, blank=True)

    def owned_cars(self):
        return [car.number for car in self.cars.all()]

class License(models.Model):
    number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    person = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True)

class Junktion(models.Model):
    address = models.CharField(max_length=50, unique=True)
    max_traffic = models.IntegerField(blank=True, null=True, default=None)
    def get_cars(self):
        return [car.number for car in self.cars.all()]
    def how_busy(self):
        if len(self.get_cars()) <= self.max_traffic * 0.4:
            return "Low traffic"
        elif len(self.get_cars()) <= self.max_traffic * 0.7:
            return "Moderate traffic"
        else:
            return "High traffic"

class Car(models.Model):
    number = models.CharField(max_length=50, null=True, default=None)
    manufacturer = models.CharField(max_length=50, null=True, default=None)
    model = models.CharField(max_length=50, null=True, default=None)
    color = models.CharField(max_length=50, null=True, default=None)
    owner = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='cars')
    junction = models.ForeignKey(Junktion, on_delete=models.SET_NULL, null=True, related_name='cars')
