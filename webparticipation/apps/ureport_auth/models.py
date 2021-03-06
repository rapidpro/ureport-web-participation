import uuid
from django.db import models
from django.conf import settings

class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    expiry = models.DateTimeField()
    token = models.CharField(max_length=32, default=0)

    def set_expiry(self, expiry):
        self.expiry = expiry
        self.save()

    def generate_password_reset_token(self):
        self.token = uuid.uuid4().hex
        self.save()

    def __unicode__(self):
        return self.user
