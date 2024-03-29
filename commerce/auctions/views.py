from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment, Watchlist
from . import util


def index(request):
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.filter(closed = False)
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
    comments = Comment.objects.filter(listing=listing).order_by('-timestamp')
    try:
        watchlist_entry_exists = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    except:
        watchlist_entry_exists = False
    
    lattest_bid_user = util.get_highest_bid(listing)
    print("lattest_bid_user:", lattest_bid_user)  # Add this line for debugging

    if lattest_bid_user == "No bids made so far.":
        listing_winner = "No bids made so far."
    elif lattest_bid_user == request.user:
        listing_winner = "Congrats. You're the winner on this listing."
    else:
        listing_winner = f"Bidding is closed. The winner is: {lattest_bid_user}"
    
    print("request.user:", request.user)  # Add this line for debugging

    if request.method == "POST":
        bid_submitted = round(float(request.POST.get("Bid")), 2)
        message, allert_type = util.post_bid(request.user, listing, bid_submitted)
        lattest_bid_user = util.get_highest_bid(listing)
        return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist_entry_exists": watchlist_entry_exists,
        "message": message,
        "allert_type": allert_type,
        "listing_winner": listing_winner,
        "bid_status": lattest_bid_user,
        "creator": request.user == listing.created_by,
        "listing_status": listing.closed,
        "comments": comments,
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "watchlist_entry_exists": watchlist_entry_exists,
            "bid_status": lattest_bid_user,
            "listing_winner": listing_winner,
            "creator": request.user == listing.created_by,
            "listing_status": listing.closed,
            "comments": comments,
        })



def create_listing(request):
    sorted_categories = Category.objects.all().order_by('category')
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
            current_bid=starting_bid,
            url=url,
            category_id=category_id,
            created_by=created_by
        )
        new_listing.save()
    
        return render(request, "auctions/create_listing.html", {
            "message": "Listing created.",
            "categories": sorted_categories
        })
    else:
        return render(request, "auctions/create_listing.html", {
            "categories": sorted_categories
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
  
        
def bid_close(request, listing_id, listing_title):
    listing = Listing.objects.get(id=listing_id)
    if listing.closed:
        listing.closed = False
    else:
        listing.closed = True
    listing.save()

    return redirect("listing_details", listing_id=listing_id, listing_title=listing_title)
        
        
def comment_post(request, listing_id, listing_title):
    comment = request.POST.get("comment")
    listing = Listing.objects.get(id=listing_id)
    new_comment = Comment(
        listing=listing,
        user=request.user,
        comment=comment,
    )
    new_comment.save()
    return redirect("listing_details", listing_id=listing_id, listing_title=listing_title)


def categories(request):
    return render(request, "auctions/categories.html", {
            "categories": Category.objects.all().order_by('category')
        })


def filtered(request, category):
    category_id = Category.objects.get(category=category)
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.filter(category=category_id)
    })