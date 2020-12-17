import datetime
import tweepy
import sklearn
import numpy as np
import pickle

from tweepy import TweepError

# needs to import file with Twitter API keys with this structure:
# keys = {
#     "ACCESS_TOKEN": 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
#     "ACCESS_TOKEN_SECRET": 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
#     "CONSUMER_KEY": 'xxxxxxxxxxxxxxxxxxxxxxxxx',
#     "CONSUMER_SECRET": 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
# }

from .twitter_api_keys import keys

from api.models import AccountSnapshot


def load_classifier():
    """
    Loads pipeline (standard scaler and logistic regression) from the file

    :return: sklearn.pipeline.Pipeline
    """
    pipe = pickle.load(open('bot_scorer/pipe.p', 'rb'))
    return pipe


def make_snapshot(twitter_id=-1, screen_name="-1"):
    """
    Returns dictionary with current data of specific Twitter account

    :param twitter_id: id
    :param screen_name: string
    :return: dictionary
    """
    authentication = tweepy.OAuthHandler(keys['CONSUMER_KEY'],
                                         keys['CONSUMER_SECRET'])
    authentication.set_access_token(
        keys['ACCESS_TOKEN'], keys['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(authentication, wait_on_rate_limit=True)

    try:
        if twitter_id != -1:
            user = api.get_user(user_id=twitter_id)
        elif screen_name != '-1':
            user = api.get_user(screen_name=screen_name)
        else:
            raise ValueError("Missing twitter_id or screen_name as argument")
    except TweepError as e:
        error = e.args[0][0]['message']

        output_dict = {
            'twitter_id': twitter_id,
            'screen_name': screen_name,
            'name': screen_name,
            'location': error,
            'url': error,
            'description': error,
            'created_at': "0001-01-01 00:00",
            'statuses_count': 0,
            'followers_count': 0,
            'friends_count': 0,
            'favourites_count': 0,
            'listed_count': 0,
            'default_profile': False,
            'verified': False,
            'protected': False,
            'bot_score': 0.0,
            'is_active': False,
            'suspended_info': error,
        }
        return output_dict

    features = [
        user.statuses_count, user.followers_count, user.friends_count,
        user.favourites_count, user.listed_count, user.default_profile,
        user.verified, user.protected
    ]

    features = np.array(features)
    features = features.reshape(1, -1)

    classifier = load_classifier()

    proba_result = classifier.predict_proba(features)
    bot_score = proba_result[0][1]

    if twitter_id != -1:
        tweet = api.user_timeline(user_id=twitter_id, count=1)[0]
    elif screen_name != '-1':
        tweet = api.user_timeline(screen_name=screen_name, count=1)[0]

    diff_days = (datetime.date.today() - tweet.created_at.date()).days
    is_active = True

    if diff_days > 90:
        is_active = False

    output_dict = {
        'twitter_id': user.id,
        'screen_name': user.screen_name,
        'name': user.name,
        'location': user.location,
        'url': user.url,
        'description': user.description,
        'created_at': user.created_at,
        'statuses_count': features[0][0],
        'followers_count': features[0][1],
        'friends_count': features[0][2],
        'favourites_count': features[0][3],
        'listed_count': features[0][4],
        'default_profile': features[0][5],
        'verified': features[0][6],
        'protected': features[0][7],
        'bot_score': bot_score,
        'is_active': is_active,
        'suspended_info': "",
    }

    # url must not be None
    if output_dict['url'] is None:
        output_dict['url'] = ""

    return output_dict


def get_most_important_features(features_input):
    """
    Returns features sorted from most important

    :param features_input: dictionary
    :return: list
    """
    features = []
    for feature in features_input:
        features.append(features_input[feature])

    features = np.array(features)
    features = features.reshape(1, -1)

    pipe = load_classifier()

    features_std = pipe['standardscaler'].transform(features)
    coefs = pipe['logisticregression'].coef_[0]

    multiplified_coefs = []
    for i in range(8):
        multiplified_coefs.append(coefs[i] * features_std[0][i])

    multiplified_coefs_dict = {
        'statuses_count': multiplified_coefs[0],
        'followers_count': multiplified_coefs[1],
        'friends_count': multiplified_coefs[2],
        'favourites_count': multiplified_coefs[3],
        'listed_count': multiplified_coefs[4],
        'default_profile': multiplified_coefs[5],
        'verified': multiplified_coefs[6],
        'protected': multiplified_coefs[7],
    }

    sorted_keys = []
    for key, value in sorted(multiplified_coefs_dict.items(),
                             key=lambda item: item[1], reverse=True):
        sorted_keys.append(key)

    output = {}
    for key in sorted_keys:
        output[key] = features_input[key]
    return output


def get_data_change(snapshot_id):
    """
    Calculate change of features and other account data (up, same or down)
    between input snapshot and previous one

    :param snapshot_id: int
    :return: dictionary
    """
    snapshot = AccountSnapshot.objects.get(id=snapshot_id)
    snapshots = list(AccountSnapshot.objects.all().filter(
        account=snapshot.account).order_by('-date_of_snapshot'))
    if snapshots[-1] == snapshot:
        return None
    else:
        snapshot_index = snapshots.index(snapshot)
        previous_snapshot = snapshots[snapshot_index + 1]

        data = {
            'statuses_count': snapshot.statuses_count,
            'followers_count': snapshot.followers_count,
            'friends_count': snapshot.friends_count,
            'favourites_count': snapshot.favourites_count,
            'listed_count': snapshot.listed_count,
            'default_profile': snapshot.default_profile,
            'verified': snapshot.verified,
            'protected': snapshot.protected,
            'bot_score': snapshot.bot_score,
            'is_active': snapshot.is_active
        }

        previous_data = {
            'statuses_count': previous_snapshot.statuses_count,
            'followers_count': previous_snapshot.followers_count,
            'friends_count': previous_snapshot.friends_count,
            'favourites_count': previous_snapshot.favourites_count,
            'listed_count': previous_snapshot.listed_count,
            'default_profile': previous_snapshot.default_profile,
            'verified': previous_snapshot.verified,
            'protected': previous_snapshot.protected,
            'bot_score': previous_snapshot.bot_score,
            'is_active': previous_snapshot.is_active
        }

        data_difference = {}

        for key in previous_data:
            if data[key] > previous_data[key]:
                data_difference[key] = 'up'
            elif data[key] == previous_data[key]:
                data_difference[key] = '-'
            else:
                data_difference[key] = 'down'

        return data_difference
