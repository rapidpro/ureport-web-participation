import datetime
from django.db import models
from django.utils import timezone
from random import randint

class UreportUser(models.Model):
    def generate_token():
        return str(randint(100, 999))
    def token_has_expired(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    def invalidate_token(self):
        self.token = None
    def activate_user(self):
        self.active = True
    email = models.EmailField(max_length=255, null=False)
    password = models.CharField(max_length=255, null=False)
    active = models.BooleanField(default=False)
    token = models.IntegerField(null=False, default=generate_token())
    uuid = models.CharField(max_length=36)
    pub_date = models.DateTimeField(default=timezone.now())
    def __unicode__(self):
        return self.user_id