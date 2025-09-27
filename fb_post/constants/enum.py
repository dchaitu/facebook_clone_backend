from django.db import models
from enum import Enum


class ReactionType(Enum):
    WOW = "WOW"
    LIT = "LIT"
    LOVE = "LOVE"
    HA = "HAHA"
    UP = "THUMBS - UP"
    DOWN = "THUMBS - DOWN"
    ANGRY = "ANGRY"
    SAD = "SAD"
