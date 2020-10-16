from django.urls import path
from .views import PostListView,PostDetailView,PostCreateView,PostUpdateView,PostDeleteView,UserPostListView
from . import views

urlpatterns = [
    path('',PostListView.as_view(),name='blog-home'),
    path('user/<str:username>/',UserPostListView.as_view(),name='blog-user'),
    path('post/<int:pk>/',PostDetailView.as_view(),name='blog-detail'),
    path('post/<int:pk>/update/',PostUpdateView.as_view(),name='blog-update'),
    path('post/<int:pk>/delete/',PostDeleteView.as_view(),name='blog-delete'),
    path('post/new/',PostCreateView.as_view(),name='blog-create'),
    path('about/',views.about,name='blog-about'),
]