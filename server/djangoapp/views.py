from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# -------------------------
# Authentication Views
# -------------------------

@csrf_exempt
def login_user(request):
    """Handle user login."""
    if request.method != "POST":
        return JsonResponse({"status": False, "error": "Invalid method"}, status=405)

    data = json.loads(request.body)
    username = data.get("userName", "").strip()
    password = data.get("password", "")

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})

    return JsonResponse({"status": False, "error": "Invalid credentials"}, status=401)


def logout_user(request):
    """Handle user logout."""
    logout(request)
    return JsonResponse({"status": True, "userName": ""})


@csrf_exempt
def register(request):
    """Handle new user registration."""
    if request.method != "POST":
        return JsonResponse({"status": False, "error": "Invalid method"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    username = data.get("userName", "").strip()
    password = data.get("password", "")
    first = data.get("firstName", "").strip()
    last = data.get("lastName", "").strip()
    email = data.get("email", "").strip()

    if User.objects.filter(username=username).exists():
        return JsonResponse({"status": False, "error": "Already Registered"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first,
        last_name=last,
        email=email,
    )
    login(request, user)
    return JsonResponse({"status": True, "userName": username}, status=201)


# -------------------------
# Dealership Views
# -------------------------

def get_dealerships(request, state="All"):
    """Fetch all dealerships, or filter by state."""
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    """Fetch details of a single dealer."""
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = f"/fetchDealer/{dealer_id}"
    dealership = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealership})


def get_dealer_reviews(request, dealer_id):
    """Fetch and analyze reviews of a dealer."""
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    for review_detail in reviews:
        sentiment = analyze_review_sentiments(review_detail["review"])
        review_detail["sentiment"] = sentiment["sentiment"]

    return JsonResponse({"status": 200, "reviews": reviews})


@csrf_exempt
def add_review(request):
    """Submit a new review for a dealer."""
    if request.method != "POST":
        return JsonResponse({"status": False, "error": "Invalid method"}, status=405)

    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

    try:
        data = json.loads(request.body)
        post_review(data)

        dealer_id = data.get("dealer_id")
        dealer = get_request(f"/fetchDealer/{dealer_id}")

        return JsonResponse({"status": 200, "dealer": dealer})
    except Exception as e:
        logger.error(f"Error posting review: {e}")
        return JsonResponse({"status": 500, "message": "Error in posting review"})


# -------------------------
# Car Views
# -------------------------

def get_cars(request):
    """Return available car models with their makes."""
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = [{"CarModel": cm.name, "CarMake": cm.car_make.name} for cm in car_models]

    return JsonResponse({"CarModels": cars})
