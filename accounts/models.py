from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Player(AbstractUser):
    rating = models.PositiveSmallIntegerField(default=1200)
    games = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
