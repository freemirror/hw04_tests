from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='freemirror')
        cls.group = Group.objects.create(
            title='Погода',
            slug='group_slug',
            description='Тестовое описание',
        )
        cls.group_without_posts = Group.objects.create(
            title='Ветра',
            slug='group2_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текстовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.urls_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Страницы используют правильные шаблоны."""
        for reverse_name, template in self.urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Текстовый пост')
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_post = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(first_post.text, 'Текстовый пост')
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(group, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        first_post = response.context['page_obj'][0]
        user = response.context['user']
        self.assertEqual(first_post.text, 'Текстовый пост')
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(user, self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        post = response.context['posts']
        self.assertEqual(post.text, 'Текстовый пост')
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pk, self.post.pk)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_not_included_into_anotger_group(self):
        """Пост с группой 'Погода' не попал в группу 'Ветра'"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_without_posts.slug}
            )
        )
        self.assertEqual(response.context.get('post'), None)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context['is_edit'])


class PaginatorViewsTest(TestCase):
    first_page_posts = 10
    second_page_posts = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Природа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text='Тестовый_пост ' + str(i),
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_page_ten_posts(self):
        """На первой странице index должно быть 10 постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.first_page_posts)

    def test_second_index_page_three_posts(self):
        """На второй странице index должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.second_page_posts)

    def test_first_group_list_page_ten_posts(self):
        """На первой странице group_list должно быть 10 постов"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.first_page_posts)

    def test_second_group_list_page_three_posts(self):
        """На второй странице group_list должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.second_page_posts)

    def test_first_profile_page_ten_posts(self):
        """На первой странице profile должно быть 10 постов"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.first_page_posts)

    def test_second_profile_page_three_posts(self):
        """На второй странице profile должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + '?page=2')
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.second_page_posts)
