from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    # path("categories", views.categories, name="categories"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>/<str:listing_title>", views.listing_details, name="listing_details"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>/<str:listing_title>/watchlist_action", views.watchlist_action, name="watchlist_action"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:listing_id>/<str:listing_title>/bid_close", views.bid_close, name="bid_close"),
]
