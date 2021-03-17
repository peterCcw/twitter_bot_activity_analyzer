import datetime

from django.test import TestCase

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from .views import load_classifier, make_snapshot, get_most_important_features


class ClassifierTests(TestCase):
    """Tests classifier methods"""

    def test_load_classifier(self):
        """Tests loading of classifier from the file."""
        self.classifier = load_classifier()

        self.assertIsInstance(self.classifier.steps[0][1], StandardScaler)
        self.assertIsInstance(self.classifier.steps[1][1], LogisticRegression)

    def test_make_snapshot(self):
        """Tests making of snapshot."""
        snapshot = make_snapshot(screen_name='BarackObama')

        self.assertIsInstance(snapshot['twitter_id'], int)
        self.assertIsInstance(snapshot['screen_name'], str)
        self.assertIsInstance(snapshot['name'], str)
        self.assertIsInstance(snapshot['location'], str)
        self.assertIsInstance(snapshot['url'], str)
        self.assertIsInstance(snapshot['description'], str)
        self.assertTrue(type(snapshot['created_at']) == datetime.datetime or
                        type(snapshot['created_at']) == str)
        self.assertIsInstance(snapshot['statuses_count'], int)
        self.assertIsInstance(snapshot['followers_count'], int)
        self.assertIsInstance(snapshot['friends_count'], int)
        self.assertIsInstance(snapshot['favourites_count'], int)
        self.assertIsInstance(snapshot['listed_count'], int)
        self.assertIsInstance(snapshot['default_profile'], bool)
        self.assertIsInstance(snapshot['verified'], bool)
        self.assertIsInstance(snapshot['protected'], bool)
        self.assertIsInstance(snapshot['bot_score'], float)
        self.assertIsInstance(snapshot['is_active'], bool)
        self.assertTrue(type(snapshot['suspended_info']) == str or
                        type(snapshot['suspended_info']) is None)

    def test_get_most_important_features(self):
        """Tests if features are returned in the correct order."""
        features = {
            'statuses_count': 71944,
            'followers_count': 70787,
            'friends_count': 1055,
            'favourites_count': 36147,
            'listed_count': 265,
            'default_profile': False,
            'verified': True,
            'protected': False,
        }

        output = get_most_important_features(features)

        self.assertEqual('verified', output.popitem()[0])
        self.assertEqual('favourites_count', output.popitem()[0])
        self.assertEqual('default_profile', output.popitem()[0])
        self.assertEqual('statuses_count', output.popitem()[0])
        self.assertEqual('friends_count', output.popitem()[0])
        self.assertEqual('protected', output.popitem()[0])
        self.assertEqual('listed_count', output.popitem()[0])
        self.assertEqual('followers_count', output.popitem()[0])
