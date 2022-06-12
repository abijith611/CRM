# from statistics import models
from email.policy import default
# from time import timezone
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_organiser = models.BooleanField(default = True)
    is_agent = models.BooleanField(default = False)
    is_customer = models.BooleanField(default = False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.user.username

class Lead(models.Model):
    first_name = models.CharField(max_length = 20)
    last_name = models.CharField(max_length = 20)
    age = models.IntegerField(default = 0)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent",null = True, blank = True, on_delete = models.SET_NULL)
    category = models.ForeignKey("Category",related_name = "leads",null=True, blank=True, on_delete = models.SET_NULL)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add = True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def getEmail(self):
        return self.user.email


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

    def getEmail(self):
        return self.user.email

class Feedback(models.Model):
    name = models.CharField(max_length= 20)
    email = models.EmailField()
    time = models.DateField(default = timezone.now)
    is_read = models.BooleanField(default = False)
    feedback = models.TextField()
    sentiment_value = models.IntegerField(default=-1)

class Category(models.Model):
    name = models.CharField(max_length = 30)
    total_count = models.IntegerField(default = 0)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

def post_user_created_signal(sender, instance, created, **kwargs):
    # print (instance, created)
    if created:
        UserProfile.objects.create(user = instance)

post_save.connect(post_user_created_signal, sender = User)