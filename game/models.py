from django.db import models

from accounts.models import Player
# Create your models here.

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class Game(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for opponent'),
        ('active', 'Game in progress'),
        ('finished', 'Finished'),
    ]
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="owned_games")
    owner_side = models.CharField(max_length=5)
    owner_online = models.BooleanField(default=False)
    opponent = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name="participated_in_games")
    opponent_online = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name="won_games")
    fen = models.TextField(default=STARTING_FEN)
    pgn = models.TextField(null=True, blank=True)