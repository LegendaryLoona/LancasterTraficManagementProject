from .models import Person, License, Car, Junktion, Camera, Fine, Violation
from django.http import JsonResponse
from datetime import datetime
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import (UserRegisterForm,PersonForm,LicenseForm,CarForm)
from django.http import HttpResponseForbidden

@login_required
def make_fine(request):
    if not request.user.is_superuser:
        return JsonResponse("You do not have permission to do this.", safe=False)
    car_id = request.GET.get('c_id')
    camera_id = request.GET.get('id')
    violation_id = request.GET.get('v_id')
    try:
        car = Car.objects.get(id=car_id) 
        camera = Camera.objects.get(id=camera_id) 
        violation = Violation.objects.get(id=violation_id)
    except Exception as e:
        return JsonResponse(f"Got Error: {e}", safe=False)
    try:
        fine = camera.generate_fine(car, violation)
        # person = car.owner
        return JsonResponse(f"Fine generated {fine.id}, {fine.person.name}, {fine.description}, {fine.fine_amount}, {fine.fine_date}, {fine.fine_location}", safe=False)
    except Exception as e:
        return JsonResponse(f"another Error: {e}", safe=False)

def view_person_info(request):
    id = request.GET.get('id')
    person = Person.objects.filter(id=id)[0]
    if not person: 
        return JsonResponse("Failed to find person", safe=False)
    try: license_number = person.license.number
    except: license_number = "None"
    data = f"Name = {person.name}, birth date = {person.birth_date}, license = {license_number}, cars = {person.owned_cars()}"
    return JsonResponse(data, safe=False)

def view_cars(request):
    junction_id = request.GET.get('id')
    if not junction_id:
        return JsonResponse( "Junction ID is required", safe=False)
    try:
        junction = Junktion.objects.get(id=junction_id) 
    except Junktion.DoesNotExist:
        return JsonResponse({"error": f"Junction ID {junction_id} not found."}, safe=False)
    cars = Car.objects.filter(junction=junction).values("number", "manufacturer", "model", "color")
    return JsonResponse({
        "junction": {
            "id": junction.id,
            "address": junction.address,
            "max_traffic": junction.max_traffic,
            "traffic_status": junction.how_busy()
        },
        "cars": list(cars)  
    }, safe=False)

# http://127.0.0.1:8000/cars/create_person/?name=ja&birth_date=1990-01-01&address=beijing
def create_person(request):
        name = request.GET.get('name')
        birth_date_str = request.GET.get('birth_date')
        address = request.GET.get('address')
        if not name:
            return JsonResponse({ "message": "Name is required."}, safe=False)
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({ "message": f"Invalid date format: {birth_date_str}"}, safe=False)
        try:
            with transaction.atomic():
                person = Person.objects.create(
                    name=name,
                    birth_date=birth_date,
                    address=address
                )
            return JsonResponse({
                 
                "message": "Person added successfully",
                "data": {
                    "id": person.id,
                    "name": person.name,
                    "birth_date": str(person.birth_date) if person.birth_date else None,
                    "address": person.address
                }
            }, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"fail: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/update_person/?name=ja&birth_date=1990-01-01&address=Nanjing&person_id=1
def update_person(request):
        person_id_str = request.GET.get('person_id')
        name = request.GET.get('name')
        birth_date_str = request.GET.get('birth_date')
        address = request.GET.get('address')
        if not person_id_str:
            return JsonResponse({ "message": "person_id is required."}, safe=False)
        try:
            person_id = int(person_id_str)
        except ValueError:
            return JsonResponse({ "message": "person_id must be an integer."}, safe=False)
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({ "message": f"Invalid date format: {birth_date_str}"}, safe=False)
        try:
            with transaction.atomic():
                person = Person.objects.get(pk=person_id)
                if name:
                    person.name = name
                if birth_date:
                    person.birth_date = birth_date
                if address:
                    person.address = address
                person.save()
            return JsonResponse({
                 
                "message": "Person updated successfully",
                "data": {
                    "id": person.id,
                    "name": person.name,
                    "birth_date": str(person.birth_date) if person.birth_date else None,
                    "address": person.address
                }
            }, safe=False)
        except Person.DoesNotExist:
            return JsonResponse({ "message": f"Person ID={person_id} does not exist."}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"fail: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/delete_person/?person_id=1
def delete_person(request):
        person_id_str = request.GET.get('person_id')
        if not person_id_str:
            return JsonResponse({ "message": "person_id is required."}, safe=False)
        try:
            person_id = int(person_id_str)
        except ValueError:
            return JsonResponse({ "message": "person_id must be an integer."}, safe=False)
        try:
            with transaction.atomic():
                person = Person.objects.get(pk=person_id)
                person.delete()

            return JsonResponse({  "message": "Person deleted successfully"}, safe=False)
        except Person.DoesNotExist:
            return JsonResponse({ "message": f"Person ID={person_id} does not exist."}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"fail: {e}"}, safe=False)
    
# http://127.0.0.1:8000/cars/create_car/?number=ABC123&manufacturer=Toyota&model=Corolla&color=Red&owner_id=1
def create_car(request):
        number = request.GET.get('number')
        manufacturer = request.GET.get('manufacturer')
        model = request.GET.get('model')
        color = request.GET.get('color')
        owner_id_str = request.GET.get('owner_id')
        if not number or not manufacturer or not model or not color:
            return JsonResponse({ "message": "Missing required fields."}, safe=False)
        owner = None
        if owner_id_str:
            try:
                owner_id = int(owner_id_str)
                owner = Person.objects.get(pk=owner_id)
            except ValueError:
                return JsonResponse({ "message": "owner_id must be an integer."}, safe=False)
            except Person.DoesNotExist:
                return JsonResponse({ "message": f"Owner ID={owner_id_str} does not exist."}, safe=False)
        try:
            with transaction.atomic():
                car = Car.objects.create(
                    number=number,
                    manufacturer=manufacturer,
                    model=model,
                    color=color,
                    owner=owner,
                )

            return JsonResponse({
                 
                "message": "Car added successfully",
                "data": {
                    "id": car.id,
                    "number": car.number,
                    "manufacturer": car.manufacturer,
                    "model": car.model,
                    "color": car.color,
                    "owner_id": car.owner.id if car.owner else None,
                    "junction_id": car.junction.id if car.junction else None
                }
            }, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"fail: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/update_car/?number=ABC123&manufacturer=Toyota&model=Corolla&color=Red&owner_id=1&car_id=1
def update_car(request):
        car_id_str = request.GET.get('car_id')
        number = request.GET.get('number')
        manufacturer = request.GET.get('manufacturer')
        model = request.GET.get('model')
        color = request.GET.get('color')
        owner_id_str = request.GET.get('owner_id')
        if not car_id_str:
            return JsonResponse({ "message": "car_id is required."}, safe=False)
        try:
            car_id = int(car_id_str)
        except ValueError:
            return JsonResponse({ "message": "car_id must be an integer."}, safe=False)
        owner = None
        if owner_id_str:
            try:
                owner_id = int(owner_id_str)
                owner = Person.objects.get(pk=owner_id)
            except ValueError:
                return JsonResponse({ "message": "owner_id must be an integer."}, safe=False)
            except Person.DoesNotExist:
                return JsonResponse({ "message": f"Owner ID={owner_id_str} does not exist."}, safe=False)
        try:
            with transaction.atomic():
                car = Car.objects.get(pk=car_id)

                if number:
                    car.number = number
                if manufacturer:
                    car.manufacturer = manufacturer
                if model:
                    car.model = model
                if color:
                    car.color = color
                if owner is not None:
                    car.owner = owner
                car.save()
            return JsonResponse({
                 
                "message": "Car updated successfully",
                "data": {
                    "id": car.id,
                    "number": car.number,
                    "manufacturer": car.manufacturer,
                    "model": car.model,
                    "color": car.color,
                    "owner_id": car.owner.id if car.owner else None,
                    "junction_id": car.junction.id if car.junction else None
                }
            }, safe=False)
        except Car.DoesNotExist:
            return JsonResponse({ "message": f"Car ID={car_id} does not exist."}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"fail: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/delete_car/?car_id=1
def delete_car(request):
        car_id_str = request.GET.get('car_id')
        if not car_id_str:
            return JsonResponse({ "message": "car_id is required."}, safe=False)
        try:
            car_id = int(car_id_str)
        except ValueError:
            return JsonResponse({ "message": "car_id must be an integer."}, safe=False)
        try:
            with transaction.atomic():
                car = Car.objects.get(pk=car_id)
                car.delete()
            return JsonResponse({  "message": "Car deleted successfully"}, safe=False)
        except Car.DoesNotExist:
            return JsonResponse({ "message": f"Car ID={car_id} does not exist."}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"fail: {e}"}, safe=False)
    
# http://127.0.0.1:8000/cars/create_license/?number=ABC1234&issue_date=1999-11-11&expiry_date=2000-11-11&person_id=1
def create_license(request):
        number = request.GET.get('number')
        issue_date_str = request.GET.get('issue_date')
        expiry_date_str = request.GET.get('expiry_date')
        person_id_str = request.GET.get('person_id')
        if not number or not issue_date_str or not expiry_date_str or not person_id_str:
            return JsonResponse({ "message": "Missing required fields"}, safe=False)

        try:
            issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({ "message": "Invalid date format, should be YYYY-MM-DD"}, safe=False)

        try:
            person_id = int(person_id_str)
            person = Person.objects.get(pk=person_id)
        except (ValueError, Person.DoesNotExist):
            return JsonResponse({ "message": f"Person ID={person_id_str} does not exist"}, safe=False)

        try:
            with transaction.atomic():
                license_obj = License.objects.create(
                    number=number,
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    person=person
                )

            return JsonResponse({
                 
                "message": "License created successfully",
                "data": {
                    "number": license_obj.number,
                    "issue_date": str(license_obj.issue_date),
                    "expiry_date": str(license_obj.expiry_date),
                    "person_id": license_obj.person.id
                }
            }, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"Failed to create: {e}"}, safe=False)


# http://127.0.0.1:8000/cars/update_license/?number=ABC1234&issue_date=1999-11-11&expiry_date=2000-11-11&person_id=1
def update_license(request):
        number = request.GET.get('number')
        issue_date_str = request.GET.get('issue_date')
        expiry_date_str = request.GET.get('expiry_date')
        person_id_str = request.GET.get('person_id')

        if not number:
            return JsonResponse({ "message": "License number is required"}, safe=False)
        issue_date = None
        expiry_date = None
        if issue_date_str:
            try:
                issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({ "message": "Invalid issue_date format, should be YYYY-MM-DD"}, safe=False)
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({ "message": "Invalid expiry_date format, should be YYYY-MM-DD"}, safe=False)

        person = None
        if person_id_str:
            try:
                person_id = int(person_id_str)
                person = Person.objects.get(pk=person_id)
            except (ValueError, Person.DoesNotExist):
                return JsonResponse({ "message": f"Person ID={person_id_str} does not exist"}, safe=False)

        try:
            with transaction.atomic():
                license_obj = License.objects.get(number=number)

                if issue_date:
                    license_obj.issue_date = issue_date
                if expiry_date:
                    license_obj.expiry_date = expiry_date
                if person:
                    license_obj.person = person
                license_obj.save()

            return JsonResponse({
                 
                "message": "License updated successfully",
                "data": {
                    "number": license_obj.number,
                    "issue_date": str(license_obj.issue_date),
                    "expiry_date": str(license_obj.expiry_date),
                    "person_id": license_obj.person.id
                }
            }, safe=False)
        except License.DoesNotExist:
            return JsonResponse({ "message": f"License number={number} does not exist"}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"Failed to update: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/delete_license/?number=
def delete_license(request):
        number = request.GET.get('number')
        if not number:
            return JsonResponse({ "message": "License number is required"}, safe=False)
        try:
            with transaction.atomic():
                license_obj = License.objects.get(number=number)
                license_obj.delete()
            return JsonResponse({  "message": "License deleted successfully"}, safe=False)
        except License.DoesNotExist:
            return JsonResponse({ "message": f"License number={number} does not exist"}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"Failed to delete: {e}"}, safe=False)
        

# http://127.0.0.1:8000/cars/create_junktion/?junktion_Id=1&address=aaa&max_traffic=111

def create_junktion(request):
        address = request.GET.get('address')
        max_traffic_str = request.GET.get('max_traffic')

        if not address:
            return JsonResponse({ "message": "Missing address"}, safe=False)
        max_traffic = None
        if max_traffic_str:
            try:
                max_traffic = int(max_traffic_str)
            except ValueError:
                return JsonResponse({ "message": "max_traffic must be an integer"}, safe=False)
        try:
            with transaction.atomic():
                junktion = Junktion.objects.create(
                    address=address,
                    max_traffic=max_traffic
                )
            return JsonResponse({
                 
                "message": "Junction created successfully",
                "data": {
                    "id": junktion.id,
                    "address": junktion.address,
                    "max_traffic": junktion.max_traffic
                }
            }, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"Creation failed: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/update_junktion/?junktion_Id=1&address=ccc&max_traffic=222&junktion_id=1
def update_junktion(request):
        junktion_id_str = request.GET.get('junktion_id')
        address = request.GET.get('address')
        max_traffic_str = request.GET.get('max_traffic')

        if not junktion_id_str:
            return JsonResponse({ "message": "Missing junktion_id"}, safe=False)

        try:
            junktion_id = int(junktion_id_str)
        except ValueError:
            return JsonResponse({ "message": "junktion_id must be an integer"}, safe=False)

        max_traffic = None
        if max_traffic_str:
            try:
                max_traffic = int(max_traffic_str)
            except ValueError:
                return JsonResponse({ "message": "max_traffic must be an integer"}, safe=False)

        try:
            with transaction.atomic():
                junktion = Junktion.objects.get(pk=junktion_id)

                if address:
                    junktion.address = address
                if max_traffic is not None:
                    junktion.max_traffic = max_traffic

                junktion.save()

            return JsonResponse({
                 
                "message": "Junction updated successfully",
                "data": {
                    "id": junktion.id,
                    "address": junktion.address,
                    "max_traffic": junktion.max_traffic
                }
            }, safe=False)
        except Junktion.DoesNotExist:
            return JsonResponse({ "message": f"Junktion ID={junktion_id} does not exist"}, safe=False)
        except Exception as e:
            return JsonResponse({ "message": f"Update failed: {e}"}, safe=False)

# http://127.0.0.1:8000/cars/delete_junktion/?junction_id=
def delete_junktion(request):
        junktion_id_str = request.GET.get('junktion_id')

        if not junktion_id_str:
            return JsonResponse({ "message": "junktion_id is required"}, safe=False)

        try:
            junktion_id = int(junktion_id_str)
        except ValueError:
            return JsonResponse({ "message": "junktion_id must be an integer"}, safe=False)
        try:
            with transaction.atomic():
                junktion = Junktion.objects.get(pk=junktion_id)
                junktion.delete()

            return JsonResponse({  "message": "Junction deleted successfully"}, safe=False)
        except Junktion.DoesNotExist:
            return JsonResponse({ "message": f"Junktion ID={junktion_id} does not exist"}, safe=False)
        except Exception as e:
            return JsonResponse({"message": f"Deletion failed: {e}"}, safe=False)
        
def register_view(request):

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            Person.objects.create(user=user, name=user.username)
            login(request, user)
            return redirect("profile") 
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return render(request, 'index.html')  
            else:
                return redirect("profile")  
        else:
            return render(request, "login.html", {"error": "Username or password is incorrect"})

    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile_view(request):
    person, created = Person.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.username, 
        },
    )
    if request.method == "POST":
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = PersonForm(instance=person)
    return render(request, "profile.html", {"form": form})

@login_required
def license_view(request):

    person = get_object_or_404(Person, user=request.user)
    try:
        user_license = person.license
    except License.DoesNotExist:
        user_license = None

    if request.method == "POST":
        form = LicenseForm(request.POST, instance=user_license)
        if form.is_valid():
            license_obj = form.save(commit=False)
            license_obj.person = person 
            license_obj.save()
            return redirect("profile")
    else:
        form = LicenseForm(instance=user_license)

    return render(request, "license_form.html", {"form": form})

@login_required
def car_add_view(request):
    person = get_object_or_404(Person, user=request.user)
    if request.method == "POST":
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = person
            car.save()
            return redirect("car_list")
    else:
        form = CarForm()
    return render(request, "car_form.html", {"form": form})

@login_required
def car_edit_view(request, car_id):
    person = get_object_or_404(Person, user=request.user)
    car = get_object_or_404(Car, id=car_id)

    if car.owner != person:
        return HttpResponseForbidden("You are not allowed to do this")
    if request.method == "POST":
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return redirect("car_list")
    else:
        form = CarForm(instance=car)

    return render(request, "car_form.html", {"form": form, "edit_mode": True})


@login_required
def car_delete_view(request, car_id):
    person = get_object_or_404(Person, user=request.user)
    car = get_object_or_404(Car, id=car_id)

    if car.owner != person:
        return HttpResponseForbidden("You are not allowed to do this")
    if request.method == "POST":
        car.delete()
        return redirect("car_list")
    return render(request, "car_confirm_delete.html", {"car": car})

@login_required
def car_list_view(request):
    person = get_object_or_404(Person, user=request.user)
    cars = person.cars.all()
    return render(request, "car_list.html", {"cars": cars})

@login_required
def index(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")

    return render(request, 'index.html')


def all_persons(request):
    persons = Person.objects.all()
    data = []
    for person in persons:
        data.append({
            "id": person.id,
            "name": person.name,
            "birth_date": str(person.birth_date) if person.birth_date else None,
            "address": person.address,
            "owned_cars": person.owned_cars() 
        })
    
    return JsonResponse(data, safe=False)


def all_licenses(request):
    licenses = License.objects.all()
    data = []

    for license in licenses:
        data.append({
            "number": license.number,
            "issue_date": str(license.issue_date),
            "expiry_date": str(license.expiry_date),
            "person_id": license.person.id,
            "person_name": license.person.name
        })
    
    return JsonResponse(data, safe=False)

def all_cars(request):
    cars = Car.objects.all()
    data = []
    for car in cars:
        data.append({
            "id": car.id,
            "number": car.number,
            "manufacturer": car.manufacturer,
            "model": car.model,
            "color": car.color,
            "owner_id": car.owner.id if car.owner else None,
            "owner_name": car.owner.name if car.owner else None,
            "junction_id": car.junction.id if car.junction else None,
            "junction_address": car.junction.address if car.junction else None
        })
    
    return JsonResponse(data, safe=False)
