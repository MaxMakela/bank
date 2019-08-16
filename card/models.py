from django.db import models
from datetime import datetime, timezone, timedelta
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser
)

USERNAME_REGEX = '^[0-9]*$'
PIN_REGEX = '^[0-9]*$'


class AccManager(BaseUserManager):
    def create_user(self, card_id, password=None):
        if not card_id:
            raise ValueError('Users must have a username')
        user = self.model(card_id=card_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, card_id, password=None):
        user = self.create_user(card_id, password=password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CardInfo(AbstractBaseUser, PermissionsMixin):
    card_id = models.CharField(
        max_length=16,
        validators=[RegexValidator(regex=USERNAME_REGEX)],
        unique=True)
    balance = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_thru = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=365))
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = AccManager()

    USERNAME_FIELD = 'card_id'
    REQUIRED_FIELDS = []


class LoginInfo(models.Model):
    card_id = models.CharField(
        max_length=16,
        validators=[RegexValidator(regex=USERNAME_REGEX)])
    time = models.DateTimeField(default=timezone.now)


class Transaction(models.Model):
    card_id = models.CharField(
        max_length=16,
        validators=[RegexValidator(regex=USERNAME_REGEX)])
    operation = models.BooleanField(default=True)
    value = models.BigIntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)
    new_balance = models.BigIntegerField(default=0)


class PinSaver(models.Model):
    card_id = models.CharField(
        max_length=16,
        validators=[RegexValidator(regex=USERNAME_REGEX)])
    new_pin = models.CharField(
        max_length=4,
        validators=[RegexValidator(regex=PIN_REGEX)])
    confirm = models.BooleanField(default=False)
