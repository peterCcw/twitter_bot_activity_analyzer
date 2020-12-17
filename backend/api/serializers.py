from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, ValidationError, \
    CharField, SerializerMethodField
from .models import AccountSnapshot, Account

from bot_scorer.views import get_most_important_features, get_data_change

import django.contrib.auth.password_validation as validators


class AccountSnapshotAllSerializer(ModelSerializer):
    features = SerializerMethodField()  # features are sorted from most to
                                        # least important
    screen_name = SerializerMethodField()

    class Meta:
        model = AccountSnapshot
        fields = [
            'id', 'name', 'screen_name', 'features', 'date_of_snapshot',
            'bot_score', 'is_active', 'account', 'suspended_info',
        ]

    def get_features(self, obj):
        features = {
            'statuses_count': obj.statuses_count,
            'followers_count': obj.followers_count,
            'friends_count': obj.friends_count,
            'favourites_count': obj.favourites_count,
            'listed_count': obj.listed_count,
            'default_profile': obj.default_profile,
            'verified': obj.verified,
            'protected': obj.protected,
        }
        return get_most_important_features(features)

    def get_screen_name(self, obj):
        account = Account.objects.get(accountsnapshot=obj)
        return account.screen_name


class AccountSnapshotDetailSerializer(ModelSerializer):
    twitter_id = SerializerMethodField()
    features = SerializerMethodField()   # features are sorted from most to
                                         # least important
    screen_name = SerializerMethodField()
    change = SerializerMethodField()

    class Meta:
        model = AccountSnapshot
        fields = [
            'id', 'twitter_id', 'name', 'screen_name', 'location', 'url',
            'description', 'created_at', 'features', 'date_of_snapshot',
            'bot_score', 'is_active', 'account', 'suspended_info', 'change',
        ]

    def get_twitter_id(self, obj):
        account = Account.objects.get(accountsnapshot=obj)
        return account.twitter_id

    def get_screen_name(self, obj):
        account = Account.objects.get(accountsnapshot=obj)
        return account.screen_name

    def get_features(self, obj):
        features = {
            'statuses_count': obj.statuses_count,
            'followers_count': obj.followers_count,
            'friends_count': obj.friends_count,
            'favourites_count': obj.favourites_count,
            'listed_count': obj.listed_count,
            'default_profile': obj.default_profile,
            'verified': obj.verified,
            'protected': obj.protected,
        }
        return get_most_important_features(features)

    def get_change(self, obj):
        return get_data_change(obj.id)


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

    def validate_password(self, data):
        user = User(username=self.initial_data['username'],
                    password=self.initial_data['password'])

        password = self.initial_data['password']
        confirmed_password = self.initial_data['confirmed_password']

        if password != confirmed_password:
            raise ValidationError("Passwords are not the same")

        errors = dict()
        try:
            # validation with standard Django password validators
            validators.validate_password(password=password, user=user)

        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise ValidationError(errors)

        return super(UserRegistrationSerializer, self).validate(data)

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'])
        user.save()
        return user
