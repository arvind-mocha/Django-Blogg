from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import profile as Profile

# Create your views here.


def avatar(request, filename):
    """Only serve profile images referenced by a profile, never arbitrary media."""
    image = get_object_or_404(Profile, image=f'profile_pics/{filename}').image
    if not filename.endswith('.jpg'):
        raise Http404
    try:
        response = FileResponse(image.open('rb'), content_type='image/jpeg')
    except (FileNotFoundError, OSError):
        raise Http404
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return response

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'You can now Login {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    return render(request,'usersapp/register.html',{'form':form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'your profile has been updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    
    return render(request,'usersapp/profile.html',context)
