from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment, Watchlist

def post_bid(user, listing, bid_amount):
    if get_highest_bid(listing) == "No bids made so far.":
        if listing.current_bid <= bid_amount:
            return bid_success(user, listing, bid_amount)
    else:
        if listing.current_bid < bid_amount:
            return bid_success(user, listing, bid_amount)
        else:
            message = "Bid should be larger then current listing price."
            allert_type = "danger"
            return message, allert_type
    
def bid_success(user, listing, bid_amount):
    new_bid = Bid(
        user=user,
        listing=listing,
        bid_amount=bid_amount,
    )
    new_bid.save()
    listing.current_bid = bid_amount
    listing.save()
    message = "Bid submmitted. Thank you."
    allert_type = "primary"
    return message, allert_type

def is_creator(user, listing):
    return user == listing.created_by
            
def get_highest_bid(listing):
    try:
        # Get the highest bid for the given listing
        highest_bid = Bid.objects.filter(listing=listing).order_by('-bid_amount').first()
        if highest_bid:
            return highest_bid.user
        else:
            return f"No bids made so far."
    except Bid.DoesNotExist:
        return f"No bids made so far."
