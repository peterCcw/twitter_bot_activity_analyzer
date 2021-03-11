from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.db.models import ObjectDoesNotExist

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token

from tweepy import TweepError

from .models import Account, AccountSnapshot
from .serializers import AccountSnapshotAllSerializer, \
    AccountSnapshotDetailSerializer, AccountSerializer, \
    UserRegistrationSerializer

from bot_scorer.views import make_snapshot, get_most_important_features


class AccountSnapshotViewSet(ViewSet):
    """Handles snapshots access."""

    def retrieve(self, request, pk=None):
        """
        Returns all snapshots for specific user (pk = account id).

        :param request: rest_framework.request.Request
        :param pk: int
        :return: rest_framework.response.Response
        """
        account_id = pk
        try:
            account = Account.objects.get(id=account_id)
        except ObjectDoesNotExist:
            return Response(data={'message': "Account not found"},
                            status=status.HTTP_404_NOT_FOUND)
        # checks if account is on logged user's list - permissions
        users = User.objects.all().filter(account=account)
        if request.user not in users:
            return Response(data={'message': "Account is not on the user's list"},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            snapshots = AccountSnapshot.objects.all().filter(account=account_id)
            serializer = AccountSnapshotAllSerializer(snapshots, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """
        Returns details for specific snapshot (pk = snapshot id).

        :param request: rest_framework.request.Request
        :param pk: int
        :return: rest_framework.response.Response
        """
        snapshot_id = pk
        # checks if snapshot exists
        try:
            snapshot = AccountSnapshot.objects.get(id=snapshot_id)
        except ObjectDoesNotExist:
            return Response(data={'message': "Snapshot not found"},
                            status=status.HTTP_404_NOT_FOUND)
        # checks if snapshot's account is on logged user's list
        account = Account.objects.get(accountsnapshot=snapshot)
        users = User.objects.all().filter(account=account)
        if request.user not in users:
            return Response(data={'message': "Account is not on the user's list"},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = AccountSnapshotDetailSerializer(snapshot)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def single(self, request):
        """
        Returns current snapshot of specific account. Account's screen name
        needs to be provided as request's param
        (screen_name).

        :param request: rest_framework.request.Request
        :return: rest_framework.response.Response
        """
        if 'screen_name' not in request.query_params:
            return Response(data={'message': "Missing screen name"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            screen_name = request.query_params['screen_name']
        try:
            snapshot_dict = make_snapshot(screen_name=screen_name)
        except TweepError as e:
            return Response(data={'message': e.args[0][0]['message']},
                            status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(data={'message': "Incorrect screen name"},
                            status=status.HTTP_400_BAD_REQUEST)

        features = {
            'statuses_count': snapshot_dict['statuses_count'],
            'followers_count': snapshot_dict['followers_count'],
            'friends_count': snapshot_dict['friends_count'],
            'favourites_count': snapshot_dict['favourites_count'],
            'listed_count': snapshot_dict['listed_count'],
            'default_profile': snapshot_dict['default_profile'],
            'verified': snapshot_dict['verified'],
            'protected': snapshot_dict['protected'],
        }

        output_dict = {
            'twitter_id': snapshot_dict['twitter_id'],
            'name': snapshot_dict['name'],
            'screen_name': snapshot_dict['screen_name'],
            'location': snapshot_dict['location'],
            'url': snapshot_dict['url'],
            'description': snapshot_dict['description'],
            'created_at': snapshot_dict['created_at'],
            'features': get_most_important_features(features),
            'bot_score': snapshot_dict['bot_score'],
            'is_active': snapshot_dict['is_active'],
            'suspended_info': snapshot_dict['suspended_info'],
        }

        return Response(data=output_dict, status=status.HTTP_200_OK)


class AccountViewSet(ViewSet):
    """Handles accounts access."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Returns list of logged user's accounts.

        :param request: rest_framework.request.Request
        :return: rest_framework.response.Response
        """
        accounts = Account.objects.all().filter(users=request.user) \
            .order_by('screen_name')
        serializer = AccountSerializer(accounts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Adds specific account to the logged user's list. Needs request data:
        twitter_id & screen_name.

        :param request: rest_framework.request.Request
        :return: rest_framework.response.Response
        """
        user = request.user
        account = Account()
        serializer = AccountSerializer(account, data=request.data)
        # checks validation
        if serializer.is_valid():
            serializer.save()
            account.users.add(user)
            return Response(data={'message': 'Account added'},
                            status=status.HTTP_201_CREATED)
        # if validation went false, account might already exists
        else:
            # check if account exists - if yes - binds account and user
            try:
                account = Account.objects.get(twitter_id=
                                              request.data['twitter_id'])
            # handling errors in serializer or if account does not exists
            except (ObjectDoesNotExist, KeyError, ValueError):
                return Response(data=serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            # checks if account is already on the user's list
            users = User.objects.all().filter(account=account)
            if user in users:
                return Response(data={'message': 'Account is already on the list'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                account.users.add(user)
                return Response(data={'message': 'Account added'},
                                status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Deletes account by it's id (pk = account id).

        :param request: rest_framework.request.Request
        :param pk: int
        :return: rest_framework.response.Response
        """
        id_account = pk
        print(pk)
        try:
            account = Account.objects.get(id=id_account)
        except ObjectDoesNotExist:
            return Response(data={'message': 'Account not found'},
                            status=status.HTTP_404_NOT_FOUND)
        users = User.objects.all().filter(account=account)
        # checks if account is on logged user's list
        if request.user not in users:
            return Response(data={'message': "Account is not on the user's list"},
                            status=status.HTTP_403_FORBIDDEN)
        # checks if logged user is not only user with this specific account
        # on his list
        elif len(users) != 1:
            account.users.remove(request.user)
        else:
            account.users.remove(request.user)
            account.delete()
        return Response(data={'message': 'Account removed from the list'},
                        status=status.HTTP_200_OK)

    @receiver(pre_delete, sender=User)
    def delete_accounts(sender, instance=None, **kwargs):
        """
        Deletes accounts with no users (when last
        owner of account is being deleted).

        :param sender: django.db.models.Model
        :param instance: model instance
        :param kwargs: dicts
        :return:
        """
        user = instance
        accounts = Account.objects.all().filter(users=user)
        for account in accounts:
            users = User.objects.all().filter(account=account)
            if (len(users) == 1) and (user in users):
                account.delete()


class UserViewSet(ViewSet):
    """Handles users access"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        Creates user. Needs request data: useername, password & confirmed
        password.

        :param request: rest_framework.request.Request
        :return: rest_framework.response.Response
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Account created'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Logs user in - returns auth token. Needs request data: useername,
        password.

        :param request: rest_framework.request.Request
        :return: rest_framework.response.Response
        """
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @action(detail=False, methods=['get'])
    def logout(self, request):
        """
        Logs user out.

        :param request: rest_framework.request.Request
        :return: rest_framework.response.Response
        """
        request.user.auth_token.delete()
        return Response(data={'message': 'Successfully logged out'},
                        status=status.HTTP_200_OK)
