from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django import forms
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bid, Comment
from django.shortcuts import redirect

from .models import User

CATEGORY_CHOICES = [
    ('Fashion', 'Fashion'), 
    ('Toys', 'Toys'), 
    ('Electronics', 'Electronics'), 
    ('Home', 'Home'),
    ('No Category Listed', 'No Category Listed')]

class CreateListingForm(forms.Form):
    title = forms.CharField(label = '', widget = forms.TextInput(attrs = {'placeholder':'Title', 'class':'form-control'}))
    description = forms.CharField(label = '', widget = forms.Textarea(attrs = {'placeholder':'Description', 'class':'form-control'}))
    price = forms.DecimalField(label = '', widget = forms.NumberInput(attrs = {'placeholder':'Starting Bid', 'class':'form-control'}))
    image = forms.URLField(required=False, label = '', widget = forms.URLInput(attrs = {'placeholder':'Image URL', 'class':'form-control'}))
    category = forms.ChoiceField(label = 'Category', choices = CATEGORY_CHOICES, widget=forms.Select(attrs = {'class': 'form-control'}))

class BidForm(forms.Form):
    bid = forms.DecimalField(label = '', widget = forms.NumberInput(attrs = {'placeholder':'Bid', 'class':'form-control'}))

class CommentForm(forms.Form):
    comment = forms.CharField(label = '', widget = forms.Textarea(attrs = {'placeholder':'Comment', 'class':'form-control'}))

def index(request):
    active_listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings
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

@login_required
def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = Listing(    
                user = request.user,        
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                price = form.cleaned_data["price"],
                image = form.cleaned_data["image"],
                category = form.cleaned_data["category"],
                active = True,
                created = timezone.now()
                )
            listing.save()
            bid = Bid(
                user = request.user,
                listing = listing,
                bid = form.cleaned_data["price"]
                )
            bid.save()
    return render(request, "auctions/create.html", {
        "form": CreateListingForm()
    })

@login_required
def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bid = Bid.objects.filter(listing=listing)
    comments = Comment.objects.filter(listing=listing)
    watchlist = request.user in listing.watchlist.all()
    if request.method != "POST":
        if listing.user == request.user:
            return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid": bid,
            "comments": comments,
            "watchlist": watchlist,
            "owner": True,
            "active": True,
            "comment_form": CommentForm()
        })
        elif listing.winner == request.user:
            if listing.active == True:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "comments": comments,
                    "watchlist": watchlist,
                    "winner": True,
                    "active": True,
                    "bid_form": BidForm(),
                    "comment_form": CommentForm()
                })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "comments": comments,
                    "watchlist": watchlist,
                    "winner": True,
                    "active": False,
                    "bid_form": BidForm(),
                    "comment_form": CommentForm()
                })
        else:
            if listing.active == True:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "comments": comments,
                    "watchlist": watchlist,
                    "winner": False,
                    "active": True,
                    "bid_form": BidForm(),
                    "comment_form": CommentForm()
                })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "comments": comments,
                    "watchlist": watchlist,
                    "winner": False,
                    "active": False,
                    "bid_form": BidForm(),
                    "comment_form": CommentForm()
                })
    elif request.method == "POST":
        if request.POST.get("action") == "close_auction":
            listing.active = False
            listing.save()
            return redirect("index")
        elif request.POST.get("action") == "add_watchlist":
            listing.watchlist.add(request.user)
            listing.save()
            return redirect(reverse("listing", kwargs={"listing_id":listing_id}))
        elif request.POST.get("action") == "remove_watchlist":
            listing.watchlist.remove(request.user)
            listing.save()
            return redirect(reverse("listing", kwargs={"listing_id":listing_id}))
        elif request.POST.get("action") == "place_bid":
            form = BidForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["bid"] > listing.price:
                    new_bid = Bid(
                        user = request.user,
                        listing = listing,
                        bid = form.cleaned_data["bid"]
                        )
                    new_bid.save()
                    listing.price = form.cleaned_data["bid"]
                    listing.winner = request.user
                    listing.save()
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bid": bid,
                        "comments": comments,
                        "watchlist": watchlist,
                        "winner": True,
                        "active": True,
                        "bid_form": BidForm(),
                        "comment_form": CommentForm()
                    })
                else:
                    if listing.winner == request.user:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "bid": bid,
                            "comments": comments,
                            "watchlist": watchlist,
                            "winner": True,
                            "active": True,
                            "bid_form": BidForm(),
                            "comment_form": CommentForm(),
                            "error": True
                        })
                    else:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "bid": bid,
                            "comments": comments,
                            "watchlist": watchlist,
                            "winner": False,
                            "active": True,
                            "bid_form": BidForm(),
                            "comment_form": CommentForm(),
                            "error": True
                        })
        elif request.POST.get("action") == "comment":
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = Comment(
                    user = request.user,
                    listing = listing,
                    comment = form.cleaned_data["comment"]
                )
                new_comment.save()
                return redirect("listing", listing_id=listing.id)
            
@login_required
def watchlist(request):
    listings = Listing.objects.filter(watchlist=request.user)
    return render(request, "auctions/watchlist.html", {
        "listings": listings 
    })
            
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories":Listing.objects.values_list("category", flat=True).distinct()
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "category":Listing.objects.filter(category=category, active=True),
        "category_name": category
    })

    