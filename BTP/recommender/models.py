from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import django.utils
import json
import numpy as np
import re
from django.core.validators import RegexValidator
# Create your models here.


class Product(models.Model):
    
    asin = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    imURL = models.CharField(max_length=500)
    keyword = models.CharField(max_length=500, default="")
    features = models.CharField(max_length=30000, default="")#models.CharField(max_length=30000, default="")
        
    def get_features(self):
        return [float(y) for  y in self.features.split()]
    
    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(all_ratings)
    def num_reviews(self):
        all_ratings =  self.review_set.all()
        return len(all_ratings)
    
    def __unicode__(self):
        return self.name
    
class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    product = models.ForeignKey(Product)
    pub_date = models.DateTimeField('date published',default = django.utils.timezone.now)
    user_name = models.CharField(max_length = 100)
    reviewer_id = models.CharField(max_length=100)
    review_text = models.CharField(max_length = 1000)
    rating = models.IntegerField(choices = RATING_CHOICES)
    
class Cluster(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)

    def get_members(self):
        return "\n".join([u.username for u in self.users.all()])

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/uploads_BTP')