
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path('all_posts', views.all_posts, name='all_posts'),
    path('following', views.following, name='following'),
    path("profile/<str:username>", views.profile, name="profile"),
    path("create_post", views.create_post, name="create_post"),
    
    # api routes
    path("posts/<str:option>", views.posts, name="posts"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("liked_post/<int:post_id>", views.liked_post, name="liked_post"),
    path("follow/<str:username>", views.follow, name="follow")

]
