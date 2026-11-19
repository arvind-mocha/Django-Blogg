import re
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .forms import ProfileUpdateForm


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@example.com', 'Strong-passphrase-789!')

    def test_register_and_login_and_csrf_protected_logout(self):
        response = self.client.post(reverse('register'), {
            'username': 'bob', 'email': 'bob@example.com',
            'password1': 'Another-passphrase-456!', 'password2': 'Another-passphrase-456!',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.get(username='bob').profile)
        self.assertRedirects(self.client.post(reverse('login'), {
            'username': 'bob', 'password': 'Another-passphrase-456!',
        }), reverse('blog-home'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        self.assertEqual(csrf_client.post(reverse('logout')).status_code, 403)
        csrf_client.get(reverse('profile'))
        token = csrf_client.cookies['csrftoken'].value
        self.assertEqual(csrf_client.post(reverse('logout'), {'csrfmiddlewaretoken': token}).status_code, 200)
        self.assertNotIn('_auth_user_id', csrf_client.session)

    def test_profile_requires_login_and_displays_default_avatar(self):
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)
        self.client.force_login(self.user)
        self.assertContains(self.client.get(reverse('profile')), '/static/blog/avatar.svg')

    def test_password_reset_end_to_end(self):
        response = self.client.post(reverse('password_reset'), {'email': self.user.email})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        reset_url = re.search(r'https?://[^\s]+(/password-reset-confirm/[^\s]+)', mail.outbox[0].body).group(1)
        response = self.client.get(reset_url)
        confirmation_url = response.url
        self.assertEqual(self.client.get(confirmation_url).status_code, 200)
        response = self.client.post(confirmation_url, {
            'new_password1': 'New-passphrase-789!', 'new_password2': 'New-passphrase-789!',
        })
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.assertTrue(self.client.login(username='alice', password='New-passphrase-789!'))


class AvatarTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.directory.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = User.objects.create_user('alice', password='Strong-passphrase-789!')
        self.client.force_login(self.user)

    def test_upload_is_reencoded_resized_and_served_without_debug(self):
        data = BytesIO()
        image = Image.new('RGB', (1000, 600), 'red')
        exif = Image.Exif()
        exif[270] = 'private metadata'
        image.save(data, format='JPEG', exif=exif)
        upload = SimpleUploadedFile('private-location.jpg', data.getvalue(), content_type='image/jpeg')
        response = self.client.post(reverse('profile'), {
            'username': self.user.username, 'email': 'alice@example.com', 'image': upload,
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.profile.refresh_from_db()
        self.assertNotIn('private-location', self.user.profile.image.name)
        with self.user.profile.image.open('rb') as stored:
            with Image.open(stored) as result:
                self.assertEqual(result.format, 'JPEG')
                self.assertLessEqual(max(result.size), 512)
                self.assertFalse(result.getexif())
        response = self.client.get(self.user.profile.image.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        response.close()

    def test_rejects_non_images_and_oversized_uploads(self):
        for upload in (
            SimpleUploadedFile('avatar.svg', b'<svg onload="alert(1)"/>', content_type='image/svg+xml'),
            SimpleUploadedFile('avatar.jpg', b'x' * (5 * 1024 * 1024 + 1), content_type='image/jpeg'),
        ):
            form = ProfileUpdateForm(files={'image': upload}, instance=self.user.profile)
            self.assertFalse(form.is_valid())
            self.assertIn('image', form.errors)

    def test_rejects_excessive_pixel_dimensions(self):
        data = BytesIO()
        Image.new('1', (5000, 4000)).save(data, format='PNG')
        form = ProfileUpdateForm(files={'image': SimpleUploadedFile('large.png', data.getvalue())})
        self.assertFalse(form.is_valid())
        self.assertIn('16 million pixels', str(form.errors))

    def test_does_not_serve_arbitrary_media(self):
        for url in ['/media/db.sqlite3', '/media/profile_pics/missing.jpg', '/media/profile_pics/../db.sqlite3']:
            self.assertEqual(self.client.get(url).status_code, 404)
