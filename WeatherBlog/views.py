from django.shortcuts import render

# Create your views here.
import requests
from django.shortcuts import render

def home(request):
  # USING APIS => Example 1
  response = requests.get('https://api.github.com/events')
  data = response.json()
  result = data[0]["repo"]

  # Example 2
  reponse2 = requests.get('https://dog.ceo/api/breeds/image/random')
  data2 = reponse2.json()
  result2 = data2["message"]

  return render(request, 'templates/index.html', {'result': result, 'result2': result2})

# Install python-dotenv package to load environment variables from .env file
# pip install python-dotenv
# pip install django djangorestframework requests 

import os
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache
import requests

# Load environment variables from .env file
load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

class WeatherView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, format=None):
        # Get the user's IP address
        ip = request.META.get('REMOTE_ADDR', None)
        if not ip:
            return Response({'error': 'Could not get IP address'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the location using the Geoapify API
        try:
            response = requests.get(f'https://api.geoapify.com/v1/ipinfo?ip={ip}&apiKey={os.getenv("GEOAPIFY_API_KEY")}')
            response.raise_for_status()
            geolocation_data = response.json()
            location = f"{geolocation_data['location']['lat']},{geolocation_data['location']['lon']}"
        except requests.exceptions.RequestException as err:
            return Response({"Geolocation API error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check if the data is in cache
        data = cache.get(location)
        if not data:
            try:
                response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={os.getenv("WEATHER_API_KEY")}&q={location}')
                response.raise_for_status()
                data = response.json()
                # Store the data in cache for 1 hour
                cache.set(location, data, 60*60)
            except requests.exceptions.RequestException as err:
                return Response({"Weather API error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CustomUser, blogPost, Comment
from .forms import CustomUserForm, blogPostForm, CommentForm

class blogPostListView(ListView):
    model = blogPost
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']

class blogPostDetailView(DetailView):
    model = blogPost

class blogPostCreateView(LoginRequiredMixin, CreateView):
    model = blogPost
    form_class = blogPostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class blogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = blogPost
    form_class = blogPostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class blogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = blogPost
    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(blogPost, pk=self.kwargs.get('pk'))
        return super().form_valid(form)

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = '/'

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False
