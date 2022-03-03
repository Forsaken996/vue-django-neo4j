# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# Create your models here.


# Create your models here.
class Relation(models.Model):
    objects = models.Manager()
    entity1 = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)
    entity2 = models.CharField(max_length=100)


class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
