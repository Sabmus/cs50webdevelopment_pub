# https://cs50.harvard.edu/web/2020/projects/4/network/#specification
# https://docs.djangoproject.com/en/4.1/ref/request-response/#jsonresponse-objects
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json

from . import models
from . import forms


@login_required(login_url='login')
def index(request):
    return render(request, template_name='network/index.html', context={})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("all_posts"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = models.User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def all_posts(request):
    return render(request, template_name='network/posts.html', context={})


@login_required(login_url='login')
def following(request):
    return render(request, template_name='network/following.html', context={})


@login_required(login_url='login')
def profile(request, username):
    profile_user = models.User.objects.get(username=username)

    return render(request, template_name='network/profile.html', context={
        'username': profile_user.username,
        'can_follow': request.user != profile_user,  # return False is the logged user is different than the profile user
        'follower': profile_user.follower.count(),
        'following': profile_user.following(),
        'is_follower': request.user.is_follower(username)
    })


##@login_required(login_url='login')
@ensure_csrf_cookie
def posts(request, option):
    logged_in = request.user.is_authenticated

    if option not in ('all', 'following', 'profile'):
        return JsonResponse({'message': 'Error: wrong url option.'}, status=400)
    
    if not logged_in and option in ('following', 'profile'):
        return JsonResponse({'message': 'User must be logged in.'}, status=400)


    if option == 'all':
        posts = models.Post.objects.all().order_by('-created_at')
        
    if option == 'following':
        following = models.User.objects.filter(follower__exact=request.user)
        posts = models.Post.objects.filter(author__in=following).order_by('-created_at')

    if option == 'profile':
        username = request.GET.get('username')
        author = models.User.objects.get(username=username)
        posts = models.Post.objects.filter(author__exact=author).order_by('-created_at')


    page_number = request.GET.get('page', 1)  # default: page 1
    paginator = Paginator(posts, 10)  # show 10 post per page
    page_obj = paginator.get_page(page_number)

    # page_obj.has_other_pages()
    num_pages = paginator.num_pages
    has_next = page_obj.has_next()
    has_previous = page_obj.has_previous()
    next_page = None
    previous_page = None

    if has_next:
        next_page = page_obj.next_page_number()
    if has_previous:
        previous_page = page_obj.previous_page_number()

    posts_list = [post.serialize() for post in page_obj.object_list]

    posts_dict = {
        'user': request.user.username,
        'option': option,
        'current_page': page_obj.number,
        'num_pages': num_pages,
        'has_next': has_next,
        'has_previous': has_previous,
        'next_page': next_page,
        'previous_page': previous_page,
        'posts_list': posts_list
    }

    return JsonResponse(posts_dict, status=200)


@login_required(login_url='login')
def create_post(request):
    post_form = forms.PostForm(request.POST)

    if request.method != "POST":
        return render(request, template_name='network/index.html', context={
            'post_form': post_form,
            'message': 'POST request is required.'
        })
    
    if not post_form.is_valid():
         return render(request, template_name='network/index.html', context={
            'post_form': post_form,
            'message': 'Please check you input.'
        })


    post = models.Post(**post_form.cleaned_data)
    post.author = request.user
    post.save()

    return HttpResponseRedirect(reverse('all_posts'))


@login_required(login_url='login')
@ensure_csrf_cookie
def edit_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'message': 'must be post request.'})

    try:
        post = models.Post.objects.get(id=post_id)
        content = json.loads(request.body)
    except models.Post.DoesNotExist as error:
        return JsonResponse({'message': 'Post not found.'}, status=500)

    if post.author != request.user:
        return JsonResponse({'message': 'You cannot do that!.'}, status=400)

    post.content = content
    post.save(update_fields=["content"])

    return JsonResponse({'content': content}, status=200)
    

@login_required(login_url='login')
def liked_post(request, post_id):
    try:
        post = models.Post.objects.get(pk=post_id)
    except models.Post.DoesNotExist as error:
        return JsonResponse({'message': error}, status=500)

    # if user not liked the post add to liked list, else remove it
    if request.user not in post.liked_by.all():
        post.liked_by.add(request.user)
        return JsonResponse({'message': 'post liked!', 'likes': post.like_count}, status=200)
    else:
        post.liked_by.remove(request.user)
        return JsonResponse({'message': 'post not liked!', 'likes': post.like_count}, status=200)


@login_required(login_url='login')
def follow(request, username):
    try:
        profile_user = models.User.objects.get(username__exact=username)
    except models.User.DoesNotExist as error:
        return JsonResponse({'message': error}, status=500)

    # if user is not following, then follow, elese unfollow
    if request.user not in profile_user.follower.all():
        profile_user.follower.add(request.user)
    else:
        profile_user.follower.remove(request.user)

    follow_data = {
        'follower': profile_user.follower.count(),
        'is_follower': request.user.is_follower(username)
    }
    return JsonResponse(follow_data, status=200)
    