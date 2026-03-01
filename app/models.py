from django.db import models

# Create your models here.
class Photo(models.Model):
    name = models.CharField(max_length=60)
    photo = models.ImageField(upload_to='media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='photos', on_delete=models.CASCADE)