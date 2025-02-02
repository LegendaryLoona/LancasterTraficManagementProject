from django.contrib import admin
from .models import Person, License, Car, Junktion, Violation, Fine, Camera
admin.site.register(Person)
admin.site.register(Car)
admin.site.register(License)
admin.site.register(Junktion)
admin.site.register(Violation)
admin.site.register(Fine)
admin.site.register(Camera)