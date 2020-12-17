# This script should be run every 24h. The way of launch depends on OS. In
# Windows it is possible to use Task scheduler
#
# IMPORTANT: because of import issues, in Windows Task Scheduler this file
# should be started in "\..path to project\backend" in module mode
# "-m bot_scorer.cron"

import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'activity_analyzer.settings'
django.setup()

from api.models import Account, AccountSnapshot
from bot_scorer.views import make_snapshot

accounts = Account.objects.all()

for account in accounts:
    snapshot_dict = make_snapshot(twitter_id=account.twitter_id)

    snapshot = AccountSnapshot(
        account=account,

        name=snapshot_dict["name"],
        location=snapshot_dict["location"],
        url=snapshot_dict["url"],
        description=snapshot_dict["description"],
        created_at=snapshot_dict["created_at"],
        statuses_count=snapshot_dict["statuses_count"],
        followers_count=snapshot_dict["followers_count"],
        friends_count=snapshot_dict["friends_count"],
        favourites_count=snapshot_dict["favourites_count"],
        listed_count=snapshot_dict["listed_count"],
        default_profile=snapshot_dict["default_profile"],
        verified=snapshot_dict["verified"],
        protected=snapshot_dict["protected"],
        bot_score=snapshot_dict["bot_score"],
        is_active=snapshot_dict["is_active"],
        suspended_info=snapshot_dict["suspended_info"],
    )

    if account.screen_name != snapshot_dict["screen_name"] and \
            snapshot_dict["suspended_info"] == "":
        account.screen_name = snapshot_dict["screen_name"]
        account.save()

    snapshot.save()
