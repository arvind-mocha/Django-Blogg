from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import post


class PostTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author', password='Strong-passphrase-789!')
        self.other = User.objects.create_user('other', password='Strong-passphrase-789!')
        self.post = post.objects.create(title='Hello', content='<script>alert(1)</script>', author=self.author)

    def test_public_pages_and_escaped_content(self):
        for url in ['/', '/about/', '/user/author/', self.post.get_absolute_url()]:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.get(self.post.get_absolute_url()), '&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_anonymous_cannot_modify_posts(self):
        for name in ['blog-update', 'blog-delete']:
            self.assertEqual(self.client.post(reverse(name, args=[self.post.pk])).status_code, 302)
        self.assertEqual(self.client.post(reverse('blog-create')).status_code, 302)

    def test_other_user_cannot_update_or_delete(self):
        self.client.force_login(self.other)
        for name in ['blog-update', 'blog-delete']:
            url = reverse(name, args=[self.post.pk])
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {'title': 'stolen', 'content': 'changed'}).status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Hello')

    def test_author_can_create_edit_and_delete(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse('blog-create'), {
            'title': 'New post', 'content': 'Hello', 'author': self.other.pk,
        })
        created = post.objects.get(title='New post')
        self.assertEqual(created.author, self.author)
        self.assertRedirects(response, created.get_absolute_url())
        self.assertRedirects(self.client.post(reverse('blog-update', args=[created.pk]), {
            'title': 'Edited', 'content': 'Updated',
        }), created.get_absolute_url())
        self.assertRedirects(self.client.post(reverse('blog-delete', args=[created.pk])), '/')
        self.assertFalse(post.objects.filter(pk=created.pk).exists())

    def test_post_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.author)
        self.assertEqual(client.post(reverse('blog-create'), {'title': 'CSRF', 'content': 'bad'}).status_code, 403)

    def test_untrusted_host_is_rejected(self):
        self.assertEqual(self.client.get('/', HTTP_HOST='evil.example').status_code, 400)
