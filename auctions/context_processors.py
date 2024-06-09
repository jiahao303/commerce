from .models import Listing

def watchlist_count(request):
    if request.user.is_authenticated:
        return {"watchlist_count": Listing.objects.filter(watchlist=request.user).count()}
    else:
        return {"watchlist_count": 0}
