from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Photo
from .forms import PhotoForm, RegisterForm


# --- Login / Logout: beépített Django nézetek, nem kell semmit írni ---

class CustomLoginView(LoginView):
    template_name = 'app/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('photo_list')


# --- Többi nézet: function-based, átlátható ---

def photo_list(request):
    sort = request.GET.get('sort', 'name')
    if sort == 'date':
        photos = Photo.objects.all().order_by('uploaded_at')
    else:
        photos = Photo.objects.all().order_by('name')
    return render(request, 'app/photo_list.html', {'photos': photos, 'sort': sort})


def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'app/photo_detail.html', {'photo': photo})


@login_required
def photo_upload(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.owner = request.user
            photo.save()
            messages.success(request, 'Photo uploaded successfully.')
            return redirect('photo_list')
    else:
        form = PhotoForm()
    return render(request, 'app/photo_upload.html', {'form': form})


@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if not request.user.is_staff and photo.owner != request.user:
        messages.error(request, 'You can only delete your own photos.')
        return redirect('photo_list')
    if request.method == 'POST':
        photo.photo.delete(save=False)
        photo.delete()
        messages.success(request, 'Photo deleted.')
        return redirect('photo_list')
    return render(request, 'app/photo_confirm_delete.html', {'photo': photo})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('photo_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('photo_list')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})