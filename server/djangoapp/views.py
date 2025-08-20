# Uncomment the required imports before adding the code



from django.contrib.auth.models import User

from django.contrib.auth import logout

from django.http import JsonResponse
from .models import CarMake, CarModel
 # you'll create this next


from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request


def logout_user(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...
def register(request):
    if request.method != "POST":
        return JsonResponse({"status":
        False, "error": "Invalid method"}, status=400)

    data = json.loads(request.body.decode("utf-8"))
    username = data.get("userName", "").strip()
    password = data.get("password", "")
    first = data.get("firstName", "").strip()
    last = data.get("lastName", "").strip()
    email = data.get("email", "").strip()

    if User.objects.filter(username=username).exists():
        return JsonResponse({"status": False, "error": "Already Registered"})

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first,
        last_name=last,
        email=email,
    )
    # authenticate & login
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({"status": True, "userName": username})
    return JsonResponse({"status": False, "error": "Auth failed"}, status=400)


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...
# Update the `get_dealerships` render list of dealerships all by default,
# particular state if state is passed


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...


def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail["review"])
            print(response)
            review_detail["sentiment"] = response["sentiment"]
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `add_review` view to submit a review
# def add_review(request):
# ...


def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            # Insert the review
            post_review(data)

            # After adding, fetch dealer details again
            dealer_id = data.get("dealer_id")
            dealer = get_request(f"/fetchDealer/{dealer_id}")

            return JsonResponse({"status": 200, "dealer": dealer})
        except Exception as e:
            print(e)
            return JsonResponse({"status": 401,
                "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})


def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, 
                     "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})
