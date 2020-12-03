from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Account, AccountSnapshot#, AccountList
from django.db.models import ObjectDoesNotExist
from .serializers import AccountSnapshotAllSerializer, \
    AccountSnapshotDetailSerializer, AccountSerializer, \
    UserRegistrationSerializer
from django.db.models.signals import pre_delete
from django.dispatch import receiver


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def snapshot_list(request):
    """
    Returns list of snapshots for specific account. Needs account id as
    account_id in the request.

    :param request: rest_framework.request.Request
    :return: rest_framework.response.Response
    """
    # checks account_id request param
    try:
        account_id = request.query_params['account_id']
        account_id = int(account_id)
    except KeyError:
        return Response(data={'message': "missing value of account_id"},
                        status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response(data={'message': "incorrect value of account_id"},
                        status=status.HTTP_400_BAD_REQUEST)
    # checks if specific account exists
    try:
        account = Account.objects.get(id=account_id)
    except ObjectDoesNotExist:
        return Response(data={'message': "account not found"},
                        status=status.HTTP_404_NOT_FOUND)
    # checks if account is on logged user's list - permissions
    users = User.objects.all().filter(account=account)
    if request.user not in users:
        return Response(status=status.HTTP_403_FORBIDDEN)
    else:
        snapshots = AccountSnapshot.objects.all().filter(account=account_id)
        serializer = AccountSnapshotAllSerializer(snapshots, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def snapshot_detail(request, id_snapshot):
    """
    Returns single snapshot.

    :param request: rest_framework.request.Request
    :param id_snapshot: int
    :return: rest_framework.response.Response
    """
    # checks if snapshot exists
    try:
        snapshot = AccountSnapshot.objects.get(id=id_snapshot)
    except ObjectDoesNotExist:
        return Response(data={'message': "snapshot not found"},
                        status=status.HTTP_404_NOT_FOUND)
    # checks if snapshot's account is on logged user's list
    account = Account.objects.get(accountsnapshot=snapshot)
    users = User.objects.all().filter(account=account)
    if request.user not in users:
        return Response(status=status.HTTP_403_FORBIDDEN)
    else:
        serializer = AccountSnapshotDetailSerializer(snapshot)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def account_list(request):
    """
    Returns list of logged user's accounts.

    :param request: rest_framework.request.Request
    :return: rest_framework.response.Response
    """
    accounts = Account.objects.all().filter(users=request.user)
    serializer = AccountSerializer(accounts, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def account_create(request):
    """
    Adds specific account to the logged user's list

    :param request: rest_framework.request.Request
    :return: rest_framework.response.Response
    """
    user = request.user
    account = Account()
    serializer = AccountSerializer(account, data=request.data)
    # checks validation
    if serializer.is_valid():
        print(serializer['twitter_id'])
        serializer.save()
        account.users.add(user)
        return Response(status=status.HTTP_201_CREATED)
    # if validation went false, account might already exists
    else:
        # check if account exists - if yes - binds account and user
        try:
            account = Account.objects.get(twitter_id=
                                          request.data['twitter_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        account.users.add(user)
        return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def account_delete(request, id_account):
    """
    Deletes account by it's id.
    
    :param request: rest_framework.request.Request
    :param id_account: int
    :return: rest_framework.response.Response
    """
    account = Account.objects.get(id=id_account)
    users = User.objects.all().filter(account=account)
    # checks if account is on logged user's list
    if request.user not in users:
        return Response(status=status.HTTP_403_FORBIDDEN)
    # checks if logged user is not only user with this specific account
    # on his list
    elif len(users) != 1:
        account.users.remove(request.user)
    else:
        account.users.remove(request.user)
        account.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def user_create(request):
    """
    Creates user

    :param request: rest_framework.request.Request
    :return: rest_framework.response.Response
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(data={'message': 'account created'},
                        status=status.HTTP_201_CREATED)
    else:
        return Response(data=serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    Logs out user

    :param request: rest_framework.request.Request
    :return: rest_framework.response.Response
    """
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def delete_accounts(sender, instance=None, **kwargs):
    user = instance
    accounts = Account.objects.all().filter(users=user)
    for account in accounts:
        users = User.objects.all().filter(account=account)
        if (len(users) == 1) and (user in users):
            print(f"deleted {account}")
            account.delete()

