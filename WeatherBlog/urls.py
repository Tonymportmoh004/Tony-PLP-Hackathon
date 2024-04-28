from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('weather/', views.WeatherView.as_view(), name='weather'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('blog/', views.blogPostListView.as_view(), name='blog-home'),
    path('blog/<int:pk>/', views.blogPostDetailView.as_view(), name='blog-detail'),
    path('blog/new/', views.blogPostCreateView.as_view(), name='blog-create'),
    path('blog/<int:pk>/update/', views.blogPostUpdateView.as_view(), name='blog-update'),
    path('blog/<int:pk>/delete/', views.blogPostDeleteView.as_view(), name='blog-delete'),
    # Assuming you have Comment views
    # path('comment/new/', views.comment.as_view(), name='comment-create'),
    # path('comment/<int:pk>/update/', views.blogPostUpdateView.as_view(), name='comment-update'),
    # path('comment/<int:pk>/delete/', views.blog.as_view(), name='comment-delete'),
]
