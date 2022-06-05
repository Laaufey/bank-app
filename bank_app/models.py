from http.client import PROCESSING
from urllib import request
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.query import QuerySet
from decimal import Decimal
import uuid

class Store(models.Model):
   @classmethod
   @property
   def uid(cls):
      return cls.objects.create()

   def __str__(self):
      return f'{self.pk}'

class Account(models.Model):
   LOANACCOUNT = 'Loan account'
   CREDITCARD = 'Credit card'
   DEBITCARD = 'Debit card'
   SAVINGSACCOUNT = 'Savings account'

   ACCOUNTS = [
      (LOANACCOUNT, 'Loan Account'),
      (DEBITCARD, 'Debit Card Account'),
      (CREDITCARD, 'Credit Card Account'),
      (SAVINGSACCOUNT, 'Savings Account'),
   ]

   user = models.ForeignKey(User, on_delete=models.CASCADE)
   title = models.CharField(max_length=200)
   account_type = models.CharField(choices=ACCOUNTS, default=SAVINGSACCOUNT, max_length=20)
   last_update = models.DateTimeField(auto_now_add=True, null=True)

   class Meta:
      get_latest_by = 'pk'

   @property
   def movements(self) -> QuerySet:
      return Ledger.objects.filter(account=self)

   @property
   def money(self) -> Decimal:
      return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

   
   def __str__(self):
      return f"{self.pk} | {self.title} | {self.account_type} | {self.money} kr."
      

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
   totp_identity = models.UUIDField(default=uuid.uuid4, editable=False)

   @property
   def full_name(self) -> str:
      return f'{self.user.first_name} {self.user.last_name}'
   
   @property
   def accounts(self) -> QuerySet:
      return Account.objects.filter(user=self.user)

   def __str__(self):
      return f'{self.user} - {self.full_name} - {self.customer_rank}'

class Ledger(models.Model):
   account = models.ForeignKey(Account, on_delete=models.PROTECT)
   transaction = models.ForeignKey(Store, on_delete=models.PROTECT)
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   text = models.TextField(default="text")

   @classmethod
   def transfer(cls, amount, debit_account, debit_text, credit_account, credit_text, is_loan=False):
      assert amount >= 0
      with transaction.atomic():
         if debit_account.money >= amount or is_loan:
            uid = Store.uid
            cls(amount=-amount, transaction=uid, account=debit_account, text=debit_text,).save()
            cls(amount=amount, transaction=uid, account=credit_account, text=credit_text).save()
         else:
            print("Sorry")
      return uid
   
   @classmethod
   def externalTransfer(cls, amount, debit_account, debit_text, credit_account, credit_text, internal_transfer = True):
      assert amount >= 0
      with transaction.atomic():
         if debit_account.money >= amount:
            uid = Store.uid

            if internal_transfer:
               amount = amount * -1
            Ledger(amount=amount, transaction=uid, account=debit_account, text=debit_text,).save()
         else:
            print("Sorry")
      return uid

   def __str__(self):
      return f'{self.amount} -- {self.transaction} -- {self.account} -- {self.text}'


class ExternalLedger(models.Model):
   account = models.ForeignKey(Account, on_delete=models.PROTECT)
   transaction = models.ForeignKey(Store, on_delete=models.PROTECT)
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   text = models.TextField(default="text")

   @classmethod
   def transfer(cls, amount, debit_account, debit_text, internal_transfer = True):
      assert amount >= 0
      with transaction.atomic():
         if debit_account.money >= amount:
            uid = Store.uid

            if internal_transfer:
               amount = amount * -1
            Ledger(amount=amount, transaction=uid, account=debit_account, text=debit_text,).save()
         else:
            print("Sorry")
      return uid
   
   def __str__(self):
      return f'{self.amount} -- {self.transaction} -- {self.account} -- {self.text}'

class Bank(models.Model):
   id = models.IntegerField(primary_key=True)
   transfer_path = models.CharField(max_length=255)