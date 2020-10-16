from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView,DeleteView
from django.http import HttpResponse
from .models import post
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.


def home(request):
    context = {
        'posts': post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):  # one way of writing class views
    model = post   
    template_name = 'blog/home.html'  # default naming convention app name/model name _ view type.html
    context_object_name = 'posts'   # overriding the default name (must)
    ordering = ['-date_posted']  # - refers descending order
    paginate_by = 3

class UserPostListView(ListView):  # one way of writing class views
    model = post   
    template_name = 'blog/user_posts.html'  # default naming convention app name/model name _ view type.html
    context_object_name = 'posts'   # overriding the default name (must)
    ordering = ['-date_posted']  # - refers descending order
    paginate_by = 3
    
    def get_queryset(self):
        query = get_object_or_404(User,username = self.kwargs.get('username'))
        return post.objects.filter(author = query).order_by('-date_posted')

class PostDetailView(DetailView):  # other way of creating class views
    model = post
    # default naming convention app name/model name _ view type.html
    # instead of connecting it to other template we create a template name post_detail.html based on its naming convintions
    # Detail view likes to call model name as objects in the html page so be carefull


class PostCreateView(LoginRequiredMixin, CreateView):
    model = post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):            # this is the method of the inherited class UserPassesTestMixin
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = post
    success_url = '/'

    def test_func(self):            # this is the method of the inherited class UserPassesTestMixin
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
