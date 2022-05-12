from sqlite3 import Timestamp
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like


def index(request):

    # Update the like count for each post
    posts = Post.objects.all().order_by('-timestamp')
    update_likes(posts)
    likes = get_likes(request)

    # Pagination
    page = pagination(request,posts)

    # Render the page
    return render(request, "network/index.html", {
        "posts": page,
        "likes": likes
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
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# When user sends a post
@login_required
def new_post(request):

    # Make sure method is post
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requested failed.'}, status=400)

    # Make sure post content has been sent
    post = request.POST["new_post"]
    if post is None:
        return JsonResponse({"error": "Must write a post before sending."}, status=400)

    # Save the new post
    new_post = Post(
        user=request.user,
        content=post
    )
    new_post.save()

    # Return to index
    return HttpResponseRedirect(reverse("index"))


def profile(request, user_id):

    # If get then generate page
    if request.method == 'GET':

        # Get the profile and see if the user is following them
        user = User.objects.get(pk=user_id)
        following = Follow.objects.filter(following=user, follower=request.user)

        # Get and update followers count
        follower_list = Follow.objects.filter(following=user)
        followers = len(follower_list)

        # Get the profiles post and the users likes
        posts = Post.objects.filter(user=user).order_by('-timestamp')
        update_likes(posts)
        likes = get_likes(request)

        # Pagination
        page = pagination(request,posts)

        # Render the page
        return render(request, "network/profile.html", {
            "profile": user,
            "posts": page,
            "following": following,
            "followers": followers,
            "likes": likes
        })

    # Otherwise the user wishes to follow them
    else:
        new_follow = Follow(
            follower=request.user,
            following=user
        )
        new_follow.save()
        return HttpResponseRedirect(reverse("profile", kwargs={'user': user}))


def follow(request, user_id):

    # Create the new follow
    user= User.objects.get(pk=user_id)
    follower = User.objects.get(pk=request.user.id)
    new_follow = Follow(
        follower=follower,
        following=user
    )
    new_follow.save()

    return HttpResponseRedirect(reverse("profile", kwargs={'user_id': user_id}))


def unfollow(request, user_id):

    # Delete the follow
    user= User.objects.get(pk=user_id)
    follower = User.objects.get(pk=request.user.id)
    follow = Follow.objects.get(follower=follower, following=user)
    follow.delete()

    return HttpResponseRedirect(reverse("profile", kwargs={'user_id': user_id}))


def following(request):

    # Find all profiles the user is following
    following_list = Follow.objects.filter(follower=request.user.id).values_list('following')
    print(following_list)

    posts = Post.objects.filter(user__in=following_list).order_by('-timestamp')
    update_likes(posts)
    likes = get_likes(request)

    # Pagination
    page = pagination(request,posts)

    # Render the page
    return render(request, "network/index.html", {
        "posts": page,
        "likes": likes,
        "following": 'true'
    })


@csrf_exempt
def edit_post(request):

    # Check request is post
    if request.method != "POST":
        return JsonResponse({"error": "Request method must be post."}, status=400)

    # Get the new content
    data = json.loads(request.body)
    content = data.get("content", "")
    print(content)

    # Find the post
    id = data.get("id", "")
    post = Post.objects.get(pk=id)

    # Update content
    post.content = content
    post.save()

    # Return response
    return JsonResponse({"message": "Post updated."}, status=201)


@csrf_exempt
def add_like(request):

    # Check request is post
    if request.method != "POST":
        return JsonResponse({"error": "Request method must be post."}, status=400)

    # Get the post data
    data = json.loads(request.body)
    post_id = data.get("post_id", "")
    post = Post.objects.get(pk=post_id)
    user = request.user

    # Create the like
    new_like = Like(
        user = user,
        post = post
    )
    new_like.save()

    # Return response
    return JsonResponse({"message": "Like added."}, status=201)



@csrf_exempt
def remove_like(request):

    # Check request is post
    if request.method != "POST":
        return JsonResponse({"error": "Request method must be post."}, status=400)

    # Get the post data
    data = json.loads(request.body)
    post_id = data.get("post_id", "")
    post = Post.objects.get(pk=post_id)
    user = request.user

    # Find the like
    like = Like.objects.get(post=post, user=user)
    like.delete()

    # Return response
    return JsonResponse({"message": "Like removed."}, status=201)


# A function that updates the likes count whent he user request the page
def update_likes(posts):
    for post in posts:
        likes = Like.objects.filter(post=post.id)
        count = len(likes)
        post.like_count = count
        post.save


#A function that gets a list of all posts the user likes
def get_likes(request):
    likes = Like.objects.filter(user=request.user.id)
    posts =[]
    for like in likes:
        posts.append(like.post.id)
    return posts


# A function that automate the pagination
def pagination(request, posts):
    pages = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = pages.get_page(page_num)
    return page