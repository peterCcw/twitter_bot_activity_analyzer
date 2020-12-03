from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, ValidationError, \
    CharField
from .models import AccountSnapshot, Account


class AccountSnapshotAllSerializer(ModelSerializer):
    class Meta:
        model = AccountSnapshot
        fields = ['name', 'account']


class AccountSnapshotDetailSerializer(ModelSerializer):
    class Meta:
        model = AccountSnapshot
        fields = ['name', 'account']


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'twitter_id', 'screen_name']


class UserRegistrationSerializer(ModelSerializer):
    confirmed_password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True,
            }
        }

    def save(self):
        user = User(username=self.validated_data['username'])
        password = self.validated_data['password']
        confirmed_password = self.validated_data['confirmed_password']
        if password != confirmed_password:
            raise ValidationError({'password': 'Passwords are not'
                                               ' the same'})
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
