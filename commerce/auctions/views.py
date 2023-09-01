from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment, Watchlist


def index(request):
    
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def listing_details(request, listing_id, listing_title):
    listing = Listing.objects.get(id=listing_id)
    try:
        watchlist_entry_exists = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    except:
        watchlist_entry_exists = False
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist_entry_exists": watchlist_entry_exists,
    })


def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        starting_bid = request.POST.get("starting_bid")
        url = request.POST.get("url")
        category_id = request.POST.get("category")
        created_by = request.user
    
        # Create a new Listing instance and save it to the database
        new_listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            url=url,
            category_id=category_id,
            created_by=created_by
        )
        new_listing.save()
    
        return render(request, "auctions/create_listing.html", {
            "message": "Listing created.",
            "categories": Category.objects.all()
        })
    else:
        return render(request, "auctions/create_listing.html", {
            "categories": Category.objects.all()
        })
    
def watchlist(request):
    watchlist_entries = Watchlist.objects.filter(user=request.user)
    listings_in_watchlist = Listing.objects.filter(listing_watchlist__in=watchlist_entries)
    return render(request, "auctions/watchlist.html", {
        "listings_in_watchlist": listings_in_watchlist,
    })
    
    
def watchlist_action(request, listing_id, listing_title):
    listing = Listing.objects.get(id=listing_id)
    
    watchlist_entry_exists = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    if watchlist_entry_exists:
        # Watchlist entry exists, remove it
        Watchlist.objects.filter(user=request.user, listing=listing).delete()
    else:
        # Watchlist entry doesn't exist, add it
        Watchlist.objects.create(user=request.user, listing=listing)

    return redirect("listing_details", listing_id=listing_id, listing_title=listing_title)
        