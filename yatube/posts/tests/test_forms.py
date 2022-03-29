from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='freemirror')
        cls.post = Post.objects.create(
            text='Текстовый пост',
            author=cls.user,
        )
        cls.form = PostForm

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текстовый пост 2'}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Текстовый пост 2').exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирование записи в Post."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текстовый пост 3'}
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(text='Текстовый пост 3').exists()
        )

    def test_create_post_anonymous(self):
        """"Создание поста под гостевым пользователем."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текстовый пост от гостя'}
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/create/'
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(text='Текстовый пост от гостя').exists()
        )
