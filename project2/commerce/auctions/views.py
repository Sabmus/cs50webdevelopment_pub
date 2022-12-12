# https://cs50.harvard.edu/web/2020/projects/2/commerce/#specification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


from . import models
from . import forms


def index(request):
    # list all available by last_until items to auction
    items = models.Item.objects.filter(last_until__gte=timezone.now()).all()
    return render(request, template_name="auctions/index.html", context={
        "items": items
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
            user = models.User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        form = forms.CreateListingForm(request.POST)
        if form.is_valid():
            item = models.Item(**form.cleaned_data)
            item.owner = request.user
            item.save()
            # after save. update field "last_until" so be the addition of bid_duration to created_at
            item.last_until = item.created_at + timedelta(days=item.bid_duration)
            item.save(update_fields=["last_until"])
            return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.CreateListingForm()

    return render(request, "auctions/create_listing.html", context={
        "form": form
    })


def item_listed(request, slug):
    bid_form = forms.CreateBidForm()
    comment_form = forms.CommentForm()
    # check is item exists
    item = models.Item.objects.filter(slug__iexact=slug)
    if item.exists():
        item_found = item.first()
        last_bid = item_found.last_bid()
        comments = item_found.comments.all()

        in_watchlist = None
        if request.user.is_authenticated:
            try:
                in_watchlist = item_found.watched_by.get(username=request.user)
            except request.user.DoesNotExist:
                pass
            
        return render(request, template_name="auctions/item.html", context={
            "item": item_found,
            "bid_form": bid_form,
            "last_bid": last_bid,
            "in_watchlist": in_watchlist,
            "comment_form": comment_form,
            "comments": comments
        })
    
    return render(request, template_name="auctions/item.html", context={
        "message": "Item not found."
    })


@login_required(login_url='login')
def bid_item(request, slug):
    error_message = ""
    if request.method == "POST":
        form = forms.CreateBidForm(request.POST)
        if form.is_valid():
            item = models.Item.objects.filter(slug__iexact=slug)
            if item.exists():
                item_found = item.first()
                last_bid = item_found.last_bid()
                bidded_currency = models.Currency.objects.get(name=form.cleaned_data["currency"])
                amount_bidded = int(form.cleaned_data["amount"] * bidded_currency.conversion_rate)

                # convert the amount bidded to the base currency to compare
                if last_bid is not None:
                    amount = int(last_bid.amount * last_bid.currency.conversion_rate)
                else:
                    amount = int(item_found.starting_bid * item_found.currency.conversion_rate)

                if amount_bidded > amount:
                    bid = models.Bid(**form.cleaned_data)
                    bid.bidder = request.user
                    bid.item = item_found
                    bid.save()
                    return HttpResponseRedirect(reverse("item_listed", args=(slug,)))
                else:
                    error_message = "The amount bidded must be greater than the current amount."
            else:
                error_message = "The item was not found."
        else:
            error_message = "Please submit correct data."

        return render(request, template_name="auctions/item.html", context={
            "item": item_found,
            "bid_form": form,
            "last_bid": last_bid,
            "error_message": error_message
        })
    
    return HttpResponseRedirect(reverse("item_listed", args=(slug,)))


@login_required(login_url='login')
def close_bid(request, slug):
    item = models.Item.objects.filter(slug__iexact=slug)
    if item.exists():
        item_found = item.first()
        if request.user == item_found.owner:
            item_found.active = False
            item_found.save(update_fields=["active"])
    
    return HttpResponseRedirect(reverse("item_listed", args=(slug,)))


@login_required(login_url='login')
def add_to_watchlist(request, slug):
    item = models.Item.objects.filter(slug__iexact=slug)
    if item.exists():
        item_found = item.first()
        request.user.watchlist.add(item_found)

    return HttpResponseRedirect(reverse("item_listed", args=(slug,)))


@login_required(login_url='login')
def remove_from_watchlist(request, slug):
    item = models.Item.objects.filter(slug__iexact=slug)
    if item.exists():
        item_found = item.first()
        request.user.watchlist.remove(item_found)

    return HttpResponseRedirect(reverse("item_listed", args=(slug,)))


@login_required(login_url='login')
def add_comment(request, slug):
    error_message = ""
    if request.method == "POST":
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            item = models.Item.objects.filter(slug__iexact=slug)
            if item.exists():
                item_found = item.first()
                comment = models.Comment(**form.cleaned_data)
                comment.user = request.user
                comment.item = item_found
                comment.save()
                return HttpResponseRedirect(reverse("item_listed", args=(slug,)))
            else:
                error_message = "The item was not found."
        else:
            error_message = "Please submit correct data."
    
    return render(request, template_name="auctions/item.html", context={
        "item": item_found,
        "bid_form": form,
        "last_bid": item_found.last_bid(),
        "error_message": error_message
    })


@login_required(login_url='login')
def watchlist(request):
    watchlisted = models.User.objects.get(username=request.user).watchlist.all()
    return render(request, template_name="auctions/watchlist.html", context={
        "watchlisted": watchlisted
    })


def categories(request):
    categs = models.Category.objects.all()
    return render(request, template_name="auctions/categories.html", context={
        "categs": categs
    })


def category(request, name):
    item_by_category = models.Category.objects.get(name=name).item_set.all()
    if item_by_category.exists():
        return render(request, template_name="auctions/index.html", context={
            "items": item_by_category,
            "category_title": f"All Listing in {name}"
        })

    return render(request, template_name="auctions/index.html", context={
        "items": None,
    })