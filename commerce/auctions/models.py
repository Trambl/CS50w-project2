from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(unique=True, max_length=64)
    
    def __str__(self):
        return self.category

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=19, decimal_places=2)
    current_bid = models.DecimalField(max_digits=19, decimal_places=2, default=0)  # Add a field to track the current highest bid
    url = models.URLField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_listings")
    closed = models.BooleanField(default=False)  # Add a field to track if the listing is closed
    
    def __str__(self):
        return self.title

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    bid_amount = models.DecimalField(max_digits=19, decimal_places=2)
    
    def __str__(self):
        return f"{self.user} - {self.listing}: ${self.bid_amount}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.listing}: {self.comment}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_watchlist")

    def __str__(self):
        return f"{self.user} - {self.listing}"
