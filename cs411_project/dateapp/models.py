from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Date(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateField()
    emotion=models.CharField(max_length=200, null=True)
    movie_suggestion_1= models.CharField(max_length=200, null=True)
    movie_suggestion_2= models.CharField(max_length=200, null=True)
    movie_suggestion_3 = models.CharField(max_length=200, null=True)
    movie_path_1=models.CharField(max_length=200, null=True)
    movie_path_2 = models.CharField(max_length=200, null=True)
    movie_path_3 = models.CharField(max_length=200, null=True)