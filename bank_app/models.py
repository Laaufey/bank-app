from django.contrib.auth.models import User
from django.db import models

class Account(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   title = models.CharField(max_length=200)
   balance = models.DecimalField(max_digits=6, decimal_places=2, default=0)
   last_update = models.DateTimeField(auto_now_add=True, null=True)

   def __str__(self):
      return f"{self.title} - {self.balance}"
