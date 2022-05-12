
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.new_post, name="new_post"),
    path("profile<str:user_id>", views.profile, name="profile"),
    path("follow<str:user_id>", views.follow, name="follow"),
    path("unfollow<str:user_id>", views.unfollow, name="unfollow"),
    path("users_following", views.following, name="following"),

    # API routes
    path("edit", views.edit_post, name="edit"),
    path("like", views.add_like, name="like"),
    path("unlike", views.remove_like, name="unlike")
]
