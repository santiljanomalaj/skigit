"""
Celery tasks in the friends app!
"""

from celery import shared_task
from django.conf import settings
from datetime import date, timezone, timedelta
from django.contrib.auth.models import User
from friends.models import Notification, Friend


@shared_task
def remove_older_notifications():
    """

    Removing the notifications' created dates are below to settings.NOTIFICATION_EXPIRATION_DAYS days*
    """

    # cur_date = date.today()
    # deleted_day_notifications = cur_date - timedelta(days=settings.NOTIFICATION_EXPIRATION_DAYS)
    # Notification.objects.filter(is_read=True, created_date__lte=deleted_day_notifications).delete()
    # Friend.objects.filter(is_read=True, created_date__lte=deleted_day_notifications).delete()

    # limit max number of notifications to 30 for each user
    notification_users = User.objects.filter(id__in=Notification.objects.values_list('user_id', flat=True))
    for user in notification_users:
        Notification.objects.filter(
            id__in=Notification.objects.filter(user_id=user).order_by('-updated_date').values_list('id')[30:]).delete()

