from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   title = models.CharField(max_length=200)
   balance = models.DecimalField(max_digits=6, decimal_places=2, default=0)
   last_update = models.DateTimeField(auto_now_add=True, null=True)
   
   def __str__(self):
      return f"{self.title} - {self.user} - {self.balance}"

class Customer(models.Model):
   BASIC = 'basic'
   SILVER = 'silver'
   GOLD = 'GOLD'

   RANKS = [
      (BASIC, 'Basic'),
      (SILVER, 'Silver'),
      (GOLD, 'Gold'),
   ]

   user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
   phone_number = models.CharField(max_length=20)
   customer_rank = models.CharField(choices=RANKS, default=BASIC, max_length=6)

   @property
   def full_name(self) -> str:
      return f'{self.user.first_name} {self.user.last_name}'
   
   def __str__(self):
      return f"{self.user} - {self.full_name} - {self.customer_rank}"
