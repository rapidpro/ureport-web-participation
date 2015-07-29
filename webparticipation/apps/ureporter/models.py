import datetime
from django.db import models
from django.utils import timezone
from random import randint
from django.conf import settings


def generate_token():
    return str(randint(1000, 9999))


class Ureporter(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    uuid = models.CharField(max_length=36)
    token = models.IntegerField(default=generate_token)

    def set_uuid(self, uuid):
        self.uuid = uuid
        self.save()

    def invalidate_token(self):
        self.token = 0
        self.save()

    def token_has_expired(self):
        return self.user.date_joined >= timezone.now() - datetime.timedelta(days=1)

    def __unicode__(self):
        return self.uuid