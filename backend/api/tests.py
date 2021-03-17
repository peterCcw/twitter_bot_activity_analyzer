import datetime

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User

from api.models import AccountSnapshot, Account


class APIUserTests(APITestCase):
    """Tests user's API endpoints."""

    def test_user_registration_incorrect(self):
        """Tries to register user with incorrect data."""
        data = {
            'username': 'user1',
            'password': 'some_password',
            'confirmed_password': 'incorrect'
        }
        url = reverse('user-list')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_correct(self):
        """Tries to register user with correct data."""
        data = {
            'username': 'user12',
            'password': 'some_password',
            'confirmed_password': 'some_password'
        }
        url = reverse('user-list')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        """Tries to login user with correct data."""
        data = {
            'username': 'user1',
            'password': 'some_password'
        }
        url = reverse('user-login')

        User.objects.create_user(username="user1", password="some_password")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout(self):
        """Tries to logout user with correct data."""
        data = {
            'username': 'user1',
            'password': 'some_password'
        }
        url_login = reverse('user-login')
        url_logout = reverse('user-logout')

        User.objects.create_user(username="user1", password="some_password")
        login_response = self.client.post(url_login, data)
        token = login_response.data['token']

        response = self.client.get(url_logout, **{'HTTP_AUTHORIZATION':
                                                      f'Token {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIAccountTests(APITestCase):
    """Tests accounts's API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username="user1",
                                             password="some_password")

        self.token = Token.objects.create(user=self.user)

        self.account1 = Account(id=1, twitter_id=1, screen_name="name1")
        self.account2 = Account(id=2, twitter_id=2, screen_name="name2")
        self.account3 = Account(id=3, twitter_id=3, screen_name="name3")

        self.account1.save()
        self.account2.save()
        self.account3.save()

        self.account1.users.add(self.user)
        self.account2.users.add(self.user)
        self.account3.users.add(self.user)

    def test_account_list(self):
        """Tries to list all accounts of specific user."""
        url = reverse('account-list')

        response = self.client.get(url, **{'HTTP_AUTHORIZATION':
                                               f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_account_create_incorrect_already_on_list(self):
        """Tries to create new account which already is on the user's list."""
        url = reverse('account-list')
        data = {
            'twitter_id': '1',
            'screen_name': 'name1'
        }

        response = self.client.post(url, data, **{'HTTP_AUTHORIZATION':
                                                      f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_create_incorrect_bad_data(self):
        """Tries to create new account with incomplete data."""
        url = reverse('account-list')
        data = {
            'twitter_id': '4',
        }

        response = self.client.post(url, data, **{'HTTP_AUTHORIZATION':
                                                      f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_create_correct(self):
        """Tries to create new account with correct data."""
        url = reverse('account-list')
        data = {
            'twitter_id': '4',
            'screen_name': 'name4'
        }

        response = self.client.post(url, data, **{'HTTP_AUTHORIZATION':
                                                      f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_account_delete(self):
        """Tries to delete account."""
        url = reverse('account-detail', kwargs={'pk': 1})

        response = self.client.delete(url, **{'pk': 1, 'HTTP_AUTHORIZATION':
            f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIAccountSnapshot(APITestCase):
    """Tests accounts's API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username="user1",
                                             password="some_password")

        self.token = Token.objects.create(user=self.user)

        self.account1 = Account(id=1, twitter_id=1, screen_name="name1")
        self.account1.save()
        self.account1.users.add(self.user)

        self.snapshot1 = AccountSnapshot(
            account=self.account1,
            name='snapshot1',
            location='snapshot1',
            url='snapshot1',
            description='snapshot1',
            created_at='0001-01-01',
            statuses_count=1,
            followers_count=1,
            friends_count=1,
            favourites_count=1,
            listed_count=1,
            default_profile=False,
            verified=False,
            protected=False,
            bot_score=0.45,
            is_active=True,
            suspended_info='',
        )

        self.snapshot2 = AccountSnapshot(
            account=self.account1,
            name='snapshot2',
            location='snapshot2',
            url='snapshot2',
            description='snapshot2',
            created_at='0001-01-01',
            statuses_count=1,
            followers_count=1,
            friends_count=2,
            favourites_count=1,
            listed_count=1,
            default_profile=False,
            verified=False,
            protected=True,
            bot_score=0.50,
            is_active=True,
            suspended_info='',
        )

        self.snapshot1.save()
        self.snapshot2.save()

        date1 = datetime.datetime.now() - datetime.timedelta(days=7)
        date2 = datetime.datetime.now() - datetime.timedelta(days=2)

        AccountSnapshot.objects.filter(pk=self.snapshot1.pk).update(
            date_of_snapshot=date1)
        AccountSnapshot.objects.filter(pk=self.snapshot2.pk). \
            update(date_of_snapshot=date2)

    def test_accountsnapshot_list(self):
        """Tries to list all snapshots of specific account."""
        url = reverse('snapshot-detail', kwargs={'pk': 1})

        response = self.client.get(url, **{'HTTP_AUTHORIZATION':
                                               f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_accountsnapshot_detail(self):
        """Tries to list details of specific snapshot."""
        url = reverse('snapshot-details', kwargs={'pk': 2})

        response = self.client.get(url, **{'HTTP_AUTHORIZATION':
                                               f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('up', response.data['change']['friends_count'])

    def test_accountsnapshot_single(self):
        """Tries to get single snapshot based on current Twitter data."""
        url = reverse('snapshot-single')

        response = self.client.get(url, {'screen_name': 'BarackObama'},
                                   **{'HTTP_AUTHORIZATION':
                                          f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


