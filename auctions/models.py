from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=64, decimal_places=2)
    image = models.CharField(max_length=64, blank=True, null=True)
    category = models.CharField(max_length=64)
    active = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="winner")
    watchlist = models.ManyToManyField(User, blank=True, related_name="passengers")
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=64, decimal_places=2)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=64)


