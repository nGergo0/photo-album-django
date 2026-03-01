from django.contrib import admin

from app.models import Photo

# Register your models here.
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'photo', 'uploaded_at', 'owner')
    list_filter = ('uploaded_at', 'owner')
    search_fields = ('name', 'owner__username')

admin.site.register(Photo, PhotoAdmin)