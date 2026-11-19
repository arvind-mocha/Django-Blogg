from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import profile
from io import BytesIO
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError


class AvatarField(forms.ImageField):
    """Bound image work and store only fresh JPEG pixels, without metadata."""

    def to_python(self, data):
        if not data or not hasattr(data, 'size'):
            return super().to_python(data)
        if data.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Choose an image no larger than 5 MB.')
        try:
            with Image.open(data) as image:
                if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                    raise forms.ValidationError('Choose a JPEG, PNG, or WebP image.')
                if image.width * image.height > 16_000_000:
                    raise forms.ValidationError('Choose an image with at most 16 million pixels.')
                image = ImageOps.exif_transpose(image).convert('RGB')
                image.thumbnail((512, 512))
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
            raise forms.ValidationError('Choose a valid image.') from exc
        finally:
            data.seek(0)
        return SimpleUploadedFile(f'{uuid4().hex}.jpg', output.getvalue(), content_type='image/jpeg')

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']
        
class ProfileUpdateForm(forms.ModelForm):
    image = AvatarField(required=False)

    class Meta:
        model = profile
        fields = ['image']
