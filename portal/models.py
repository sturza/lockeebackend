from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Lock(models.Model):
    lock_inner_id = models.CharField(max_length=30)
    is_opened = models.BooleanField(default=True)
    nickname = models.CharField(max_length=30, default='')
    share_id = models.CharField(max_length=12, default='')
    ip_address = models.CharField(max_length=30, default='')

    def __str__(self):
        return self.lock_inner_id


class Owner(models.Model):
    owner = models.CharField
    lock_inner_id = models.ManyToManyField(Lock)






