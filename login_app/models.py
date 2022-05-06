from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    BASIC = 'basic'
    SILVER = 'silver'
    GOLD = 'GOLD'

    RANKS = [
            (BASIC, 'Basic'),
            (SILVER, 'Silver'),
            (GOLD, 'Gold'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(default=12345)
    customer_rank = models.CharField(choices=RANKS, default=BASIC, max_length=6)

    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
