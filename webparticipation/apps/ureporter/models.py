import datetime
import uuid
from random import randint

import requests
from django.conf import settings
from django.db import models
from django.utils import timezone

from webparticipation.apps.latest_poll.models import LatestPoll


def delete_user_from_rapidpro(ureporter):
    requests.delete(settings.RAPIDPRO_API_PATH + '/contacts.json?uuid=' + ureporter.uuid,
                    data={'uuid': ureporter.uuid},
                    headers={'Authorization': 'Token ' + settings.RAPIDPRO_API_TOKEN})


def generate_token():
    return str(randint(1000, 9999))


def generate_unsubscribe_token():
    return uuid.uuid4().hex


class Ureporter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    uuid = models.CharField(max_length=36)
    urn_tel = models.CharField(max_length=13)
    token = models.IntegerField(default=generate_token)
    last_poll_taken = models.IntegerField(default=0)
    subscribed = models.BooleanField(default=True)
    unsubscribe_token = models.CharField(max_length=32, default=generate_unsubscribe_token)

    def invalidate_token(self):
        self.token = 0
        self.save()

    def token_has_expired(self):
        return self.user.date_joined >= timezone.now() - datetime.timedelta(days=settings.TOKEN_EXPIRY_DAYS)

    def is_latest_poll_taken(self):
        latest_poll_id = LatestPoll.get_solo().poll_id
        return self.last_poll_taken == latest_poll_id

    def set_last_poll_taken(self, poll_id):
        self.last_poll_taken = poll_id
        self.save()

    def save(self, **kwargs):
        self.user.save()
        super(Ureporter, self).save()

    def delete(self):
        self.user.delete()
        super(Ureporter, self).delete()

    def __unicode__(self):
        return self.uuid
