from django.db import models

class Photo(models.Model):
    name = models.CharField(max_length=40)
    photo = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='photos', on_delete=models.CASCADE)

    def __str__(self):
        return self.name