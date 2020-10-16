from django.db import models
from PIL import Image
from django.contrib.auth.models import User
# Create your models here.

class profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(default ='default.jpg',upload_to='profile_pics')
    
    def __str__(self):
        return f'{self.user.username} Profile'  
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)