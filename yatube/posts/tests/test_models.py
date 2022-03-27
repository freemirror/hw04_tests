from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текстовый пост который больше пятнадцати знаков',
            author=cls.user,
        )

    def test_post_models_have_correct_object_names(self):
        """Проверка метода __str__ у модели Post"""
        post = PostModelTest.post
        correct_model_name = 'Текстовый пост '
        with self.subTest(value=correct_model_name):
            self.assertEqual(
                post.__str__(), correct_model_name)

    def test_group_models_have_correct_object_names(self):
        """Проверка метода __str__ у модели Group"""
        group = PostModelTest.group
        correct_model_name = 'Тестовая группа'
        with self.subTest(value=correct_model_name):
            self.assertEqual(
                group.__str__(), correct_model_name)
