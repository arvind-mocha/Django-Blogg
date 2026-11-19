from django.db import models
from django.templatetags.static import static
from django.contrib.auth.models import User
# Create your models here.

class profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(default='', blank=True, upload_to='profile_pics')

    @property
    def image_url(self):
        if self.image and self.image.name != 'default.jpg':
            return self.image.url
        return static('blog/avatar.svg')
    
    def __str__(self):
        return f'{self.user.username} Profile'  
    
