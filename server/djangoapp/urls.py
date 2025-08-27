from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = "djangoapp"

urlpatterns = [
    # path for registration & authentication
    path("logout", views.logout_user, name="logout"),
    path("register", views.register, name="register"),
    path("login", views.login_user, name="login"),

    # dealership-related paths
    path("get_cars", views.get_cars, name="getcars"),
    path("get_dealers", views.get_dealerships, name="get_dealers"),
    path(
        "get_dealers/<str:state>",
        views.get_dealerships,
        name="get_dealers_by_state",
    ),
    path(
        "dealer/<int:dealer_id>",
        views.get_dealer_details,
        name="dealer_details",
    ),
    path(
        "reviews/dealer/<int:dealer_id>",
        views.get_dealer_reviews,
        name="dealer_reviews",   # changed to avoid duplicate
    ),
    path(
        "add_review",
        views.add_review,
        name="add_review",
    ),
    path(
        "dealers/",
        views.get_dealerships,
        name="dealers_alias",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
