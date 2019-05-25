from django.db import models
from datetime import datetime, timezone, timedelta
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser
)

USERNAME_REGEX = '^[0-9]*$'

class AccManager(BaseUserManager):
  def create_user(self, cardID, password=None):
    if not cardID:
      raise ValueError('Users must have a username')
    user = self.model(cardID = cardID)
    user.set_password(password)
    user.save(using=self._db)
    return user


  def create_superuser(self, cardID, password=None):
    user = self.create_user(cardID, password=password)
    user.is_staff = True
    user.is_admin = True
    user.is_superuser = True
    user.save(using=self._db)
    return user




class CardInfo(AbstractBaseUser, PermissionsMixin):
  cardID = models.CharField(
        max_length=16,
        validators=[RegexValidator(regex=USERNAME_REGEX)], 
        unique=True)
  balance = models.BigIntegerField(default=0)
  is_active = models.BooleanField(default=True)
  valid_thru = models.DateField(default=datetime.now() + timedelta(days=365))
  is_superuser = models.BooleanField(default=False)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)

  objects = AccManager()
    
  USERNAME_FIELD = 'cardID'
  REQUIRED_FIELDS = []