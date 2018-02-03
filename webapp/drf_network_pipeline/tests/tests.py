from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from drf_network_pipeline.api.user import UserViewSet


User = get_user_model()  # noqa


class AccountsTest(APITestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(
                            'testuser',
                            'test@example.com',
                            'testpassword')

        # URL for creating an account.
        self.factory = APIRequestFactory()
        self.create_url = "/users/"
    # end setUp

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertFalse('password' in response.data)
    # end of test_create_user

    def test_create_user_with_short_password(self):
        """
        Ensures user is not created for password lengths less than 8.
        """

        data = {
                'username': 'foobar',
                'email': 'foobarbaz@example.com',
                'password': 'foo'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)
    # end of test_create_user_with_short_password

    def test_create_user_with_no_password(self):
        data = {
                'username': 'foobar',
                'email': 'foobarbaz@example.com',
                'password': ''
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)
    # end of test_create_user_with_no_password

    def test_create_user_with_too_long_username(self):

        long_name = \
            ("badnametoolongasdfjdsklafjdklsajf"
             "lkjdslakfjkldsajflkjdsalkjfldskaflksj"
             "lkjdslakfjkldsajflkjdsalkjfldskaflksj"
             "lkjdslakfjkldsajflkjdsalkjfldskaflksj"
             "lkjdslakfjkldsajflkjdsalkjfldskaflksj"
             "lkjdslakfjkldsajflkjdsalkjfldskaflksj")
        data = {
            'username': long_name,
            'email': 'foobarbaz@example.com',
            'password': 'foobar'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)
    # end of test_create_user_with_too_long_username

    def test_create_user_with_no_username(self):
        data = {
                'username': '',
                'email': 'foobarbaz@example.com',
                'password': 'foobarbaz'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)
    # end of test_create_user_with_no_username

    def test_create_user_with_preexisting_username(self):
        data = {
                'username': 'testuser',
                'email': 'user@example.com',
                'password': 'testuser'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)
    # end of test_create_user_with_preexisting_username

    def test_create_user_with_preexisting_email(self):
        data = {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'testuser'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
    # end of test_create_user_with_preexisting_email

    def test_create_user_with_invalid_email(self):
        data = {
            'username': 'foobarbaz',
            'email': 'testing',
            'passsword': 'foobarbaz'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
    # end of test_create_user_with_invalid_email

    def test_create_user_with_no_email(self):
        data = {
            'username': 'foobar',
            'email': '',
            'password': 'foobarbaz'
        }

        request = self.factory.post(self.create_url, data, format='json')
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
    # end of test_create_user_with_no_email

# end of AccountsTest
