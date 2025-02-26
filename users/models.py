import os
from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    # Only process the image if it exists
    if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
        # Resize profile image if needed
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
